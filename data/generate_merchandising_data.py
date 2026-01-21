import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class Config:
    start_date: str = "2025-01-01"
    end_date: str = "2025-12-31"
    n_skus: int = 250
    n_stores: int = 30
    n_orders: int = 30000
    seed: int = 42


CATEGORIES = ["Apparel", "Footwear", "Electronics", "Home", "Beauty", "Sports"]
BRANDS = ["Apex", "NorthPeak", "UrbanCo", "Zenith", "CoreWear", "Nova", "TrailPro", "Pulse"]
REGIONS = ["West", "East", "Central", "South"]
CHANNELS = ["Store", "Online"]


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def make_dim_date(start_date: str, end_date: str) -> pd.DataFrame:
    dates = pd.date_range(start_date, end_date, freq="D")
    df = pd.DataFrame({"Date": dates})
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["MonthName"] = df["Date"].dt.strftime("%b")
    df["WeekOfYear"] = df["Date"].dt.isocalendar().week.astype(int)
    df["WeekStart"] = (df["Date"] - pd.to_timedelta(df["Date"].dt.weekday, unit="D")).dt.date
    df["WeekStart"] = pd.to_datetime(df["WeekStart"])
    df["DayName"] = df["Date"].dt.strftime("%a")
    return df


def make_dim_sku(rng: np.random.Generator, n_skus: int) -> pd.DataFrame:
    skus = [f"SKU-{i:05d}" for i in range(1, n_skus + 1)]
    categories = rng.choice(CATEGORIES, size=n_skus, replace=True)
    brands = rng.choice(BRANDS, size=n_skus, replace=True)

    # Base price by category with noise
    cat_price = {
        "Apparel": (25, 80),
        "Footwear": (50, 160),
        "Electronics": (80, 900),
        "Home": (20, 250),
        "Beauty": (10, 120),
        "Sports": (25, 300),
    }
    base_prices = []
    margin_rates = []
    for c in categories:
        lo, hi = cat_price[c]
        base_prices.append(float(rng.uniform(lo, hi)))
        # margin rate by category: electronics lower, beauty higher, etc.
        if c == "Electronics":
            margin_rates.append(float(rng.uniform(0.12, 0.22)))
        elif c == "Beauty":
            margin_rates.append(float(rng.uniform(0.30, 0.45)))
        elif c == "Apparel":
            margin_rates.append(float(rng.uniform(0.25, 0.40)))
        else:
            margin_rates.append(float(rng.uniform(0.18, 0.35)))

    df = pd.DataFrame(
        {
            "SKU": skus,
            "Category": categories,
            "Brand": brands,
            "BasePrice": np.round(base_prices, 2),
            "BaseMarginRate": np.round(margin_rates, 4),
        }
    )
    return df


def make_dim_store(rng: np.random.Generator, n_stores: int) -> pd.DataFrame:
    stores = [f"Store-{i:03d}" for i in range(1, n_stores + 1)]
    regions = rng.choice(REGIONS, size=n_stores, replace=True)
    df = pd.DataFrame({"Store": stores, "Region": regions})
    return df


def make_dim_channel() -> pd.DataFrame:
    return pd.DataFrame({"Channel": CHANNELS})


def generate_fact_sales(cfg: Config, dim_date: pd.DataFrame, dim_sku: pd.DataFrame, dim_store: pd.DataFrame) -> pd.DataFrame:
    rng = _rng(cfg.seed)

    # Sample order dates
    order_dates = rng.choice(dim_date["Date"].values, size=cfg.n_orders, replace=True)

    # Order ID per transaction line (keep it simple: one line per order)
    order_ids = [f"ORD-{i:08d}" for i in range(1, cfg.n_orders + 1)]

    # Choose SKU, store, channel
    sku_vals = dim_sku["SKU"].values
    store_vals = dim_store["Store"].values
    channels = np.array(CHANNELS)

    chosen_skus = rng.choice(sku_vals, size=cfg.n_orders, replace=True)
    chosen_stores = rng.choice(store_vals, size=cfg.n_orders, replace=True)
    chosen_channels = rng.choice(channels, size=cfg.n_orders, replace=True, p=[0.70, 0.30])  # mostly in-store

    # Units and pricing
    units = rng.integers(1, 9, size=cfg.n_orders)

    sku_lookup = dim_sku.set_index("SKU")
    base_price = sku_lookup.loc[chosen_skus, "BasePrice"].values.astype(float)
    margin_rate = sku_lookup.loc[chosen_skus, "BaseMarginRate"].values.astype(float)

    # Price noise and promo cadence
    price_multiplier = rng.normal(loc=1.0, scale=0.06, size=cfg.n_orders).clip(0.75, 1.35)
    unit_price = base_price * price_multiplier

    gross_sales = unit_price * units

    # Discount rate depends on channel and random promo, online tends to have higher discount
    promo_flag = rng.random(cfg.n_orders) < 0.25
    base_disc = np.where(chosen_channels == "Online", 0.08, 0.05)
    promo_disc = np.where(promo_flag, rng.uniform(0.05, 0.30, size=cfg.n_orders), 0.0)
    discount_rate = (base_disc + promo_disc).clip(0.0, 0.45)
    discount_amt = gross_sales * discount_rate

    net_sales = gross_sales - discount_amt

    # Gross margin dollars: margin_rate applied to net sales, add small noise
    gm_noise = rng.normal(loc=1.0, scale=0.03, size=cfg.n_orders).clip(0.85, 1.20)
    gross_margin_amt = net_sales * margin_rate * gm_noise

    # Return probability: higher online, slightly higher for apparel/footwear
    cat = sku_lookup.loc[chosen_skus, "Category"].values
    base_ret = np.where(chosen_channels == "Online", 0.06, 0.02)
    cat_bump = np.where(np.isin(cat, ["Apparel", "Footwear"]), 0.02, 0.0)
    return_prob = (base_ret + cat_bump).clip(0.0, 0.20)
    return_flag = (rng.random(cfg.n_orders) < return_prob).astype(int)

    fact = pd.DataFrame(
        {
            "OrderDate": pd.to_datetime(order_dates),
            "OrderID": order_ids,
            "SKU": chosen_skus,
            "Store": chosen_stores,
            "Channel": chosen_channels,
            "Units": units.astype(int),
            "Sales": np.round(net_sales, 2),
            "DiscountAmt": np.round(discount_amt, 2),
            "GrossMarginAmt": np.round(gross_margin_amt, 2),
            "ReturnFlag": return_flag,
        }
    )

    # Optional derived columns that help drivers visuals in Power BI
    fact["UnitPrice"] = np.round((fact["Sales"] + fact["DiscountAmt"]) / fact["Units"], 2)
    fact["DiscountRate"] = np.round(np.where((fact["Sales"] + fact["DiscountAmt"]) > 0,
                                            fact["DiscountAmt"] / (fact["Sales"] + fact["DiscountAmt"]),
                                            0.0), 4)

    return fact


def generate_fact_inventory_snapshot(
    cfg: Config,
    dim_date: pd.DataFrame,
    dim_sku: pd.DataFrame,
    dim_store: pd.DataFrame,
    fact_sales: pd.DataFrame,
) -> pd.DataFrame:
    rng = _rng(cfg.seed + 1)

    dates = dim_date["Date"].sort_values().values
    skus = dim_sku["SKU"].values
    stores = dim_store["Store"].values

    # Initialize on-hand per SKU-store
    init_on_hand = rng.integers(20, 200, size=(len(skus), len(stores)))

    # Build daily units sold per SKU-store (across channels)
    daily_sold = (
        fact_sales.groupby(["OrderDate", "SKU", "Store"], as_index=False)["Units"]
        .sum()
        .rename(columns={"OrderDate": "Date", "Units": "UnitsSold"})
    )
    # For fast lookup
    daily_sold_key = {(r["Date"], r["SKU"], r["Store"]): int(r["UnitsSold"]) for _, r in daily_sold.iterrows()}

    # Replenishment: occasional arrivals per SKU-store
    # Simple rule: each week, 25% of SKU-store combos get replenished
    replenishment_rate = 0.25
    replenishment_units_low, replenishment_units_high = 20, 120

    rows = []
    current = init_on_hand.astype(int)

    for d in dates:
        d_ts = pd.to_datetime(d)

        # Weekly replenishment event (on Mondays)
        is_monday = pd.Timestamp(d_ts).weekday() == 0
        if is_monday:
            repl_mask = rng.random(size=current.shape) < replenishment_rate
            repl_units = rng.integers(replenishment_units_low, replenishment_units_high + 1, size=current.shape)
            current = current + (repl_mask * repl_units).astype(int)

        # Decrement on-hand by units sold that day per sku-store
        for i, sku in enumerate(skus):
            for j, store in enumerate(stores):
                sold = daily_sold_key.get((d_ts, sku, store), 0)
                current[i, j] = max(int(current[i, j]) - int(sold), 0)

                rows.append(
                    {
                        "SnapshotDate": d_ts,
                        "SKU": sku,
                        "Store": store,
                        "OnHandUnits": int(current[i, j]),
                    }
                )

    return pd.DataFrame(rows)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate merchandising star schema dataset for BI and metrics.")
    parser.add_argument("--rows_orders", type=int, default=30000, help="Number of orders (FactSales rows).")
    parser.add_argument("--n_skus", type=int, default=250, help="Number of SKUs.")
    parser.add_argument("--n_stores", type=int, default=30, help="Number of stores.")
    parser.add_argument("--start_date", type=str, default="2024-01-01")
    parser.add_argument("--end_date", type=str, default="2024-12-31")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out_dir", type=str, default="data_out", help="Output folder for CSV files.")
    args = parser.parse_args()

    cfg = Config(
        start_date=args.start_date,
        end_date=args.end_date,
        n_skus=args.n_skus,
        n_stores=args.n_stores,
        n_orders=args.rows_orders,
        seed=args.seed,
    )

    out_dir = Path(args.out_dir)

    dim_date = make_dim_date(cfg.start_date, cfg.end_date)
    dim_sku = make_dim_sku(_rng(cfg.seed), cfg.n_skus)
    dim_store = make_dim_store(_rng(cfg.seed + 10), cfg.n_stores)
    dim_channel = make_dim_channel()

    fact_sales = generate_fact_sales(cfg, dim_date, dim_sku, dim_store)
    fact_inventory = generate_fact_inventory_snapshot(cfg, dim_date, dim_sku, dim_store, fact_sales)

    write_csv(dim_date, out_dir / "DimDate.csv")
    write_csv(dim_sku, out_dir / "DimSKU.csv")
    write_csv(dim_store, out_dir / "DimStore.csv")
    write_csv(dim_channel, out_dir / "DimChannel.csv")
    write_csv(fact_sales, out_dir / "FactSales.csv")
    write_csv(fact_inventory, out_dir / "FactInventorySnapshot.csv")

    print("Generated merchandising dataset:")
    print(f"- {out_dir / 'DimDate.csv'} ({len(dim_date)} rows)")
    print(f"- {out_dir / 'DimSKU.csv'} ({len(dim_sku)} rows)")
    print(f"- {out_dir / 'DimStore.csv'} ({len(dim_store)} rows)")
    print(f"- {out_dir / 'DimChannel.csv'} ({len(dim_channel)} rows)")
    print(f"- {out_dir / 'FactSales.csv'} ({len(fact_sales)} rows)")
    print(f"- {out_dir / 'FactInventorySnapshot.csv'} ({len(fact_inventory)} rows)")


if __name__ == "__main__":
    main()
