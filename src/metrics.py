from __future__ import annotations
import pandas as pd


def load_tables(data_dir: str) -> dict:
    dim_date = pd.read_csv(f"{data_dir}/DimDate.csv", parse_dates=["Date", "WeekStart"])
    dim_sku = pd.read_csv(f"{data_dir}/DimSKU.csv")
    dim_store = pd.read_csv(f"{data_dir}/DimStore.csv")
    dim_channel = pd.read_csv(f"{data_dir}/DimChannel.csv")

    fact_sales = pd.read_csv(f"{data_dir}/FactSales.csv", parse_dates=["OrderDate"])
    fact_inv = pd.read_csv(f"{data_dir}/FactInventorySnapshot.csv", parse_dates=["SnapshotDate"])

    return {
        "DimDate": dim_date,
        "DimSKU": dim_sku,
        "DimStore": dim_store,
        "DimChannel": dim_channel,
        "FactSales": fact_sales,
        "FactInventorySnapshot": fact_inv,
    }


def add_week_start(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    out = df.copy()
    out["WeekStart"] = (out[date_col] - pd.to_timedelta(out[date_col].dt.weekday, unit="D")).dt.normalize()
    return out


def kpi_summary(fact_sales: pd.DataFrame) -> dict:
    sales = float(fact_sales["Sales"].sum())
    orders = int(fact_sales["OrderID"].nunique())
    units = int(fact_sales["Units"].sum())
    gm = float(fact_sales["GrossMarginAmt"].sum())
    markdown = float(fact_sales["DiscountAmt"].sum())

    gm_pct = (gm / sales) if sales > 0 else 0.0
    markdown_rate = (markdown / (sales + markdown)) if (sales + markdown) > 0 else 0.0
    aov = (sales / orders) if orders > 0 else 0.0

    return {
        "Sales $": round(sales, 2),
        "Orders": orders,
        "Units": units,
        "GM $": round(gm, 2),
        "GM %": round(gm_pct, 4),
        "Markdown $": round(markdown, 2),
        "Markdown Rate %": round(markdown_rate, 4),
        "AOV": round(aov, 2),
    }


def sell_through_pct(units_sold: float, on_hand: float) -> float:
    denom = units_sold + on_hand
    return (units_sold / denom) if denom > 0 else 0.0


def avg_weekly_units(fact_sales: pd.DataFrame) -> float:
    fs = add_week_start(fact_sales, "OrderDate")
    weekly = fs.groupby("WeekStart", as_index=False)["Units"].sum()
    return float(weekly["Units"].mean()) if len(weekly) else 0.0


def weeks_of_supply(on_hand: float, avg_week_units: float) -> float:
    return (on_hand / avg_week_units) if avg_week_units > 0 else 0.0


def stockout_days(fact_inv: pd.DataFrame) -> int:
    daily = fact_inv.groupby("SnapshotDate", as_index=False)["OnHandUnits"].sum()
    return int((daily["OnHandUnits"] == 0).sum())


def exec_page_tables(fact_sales: pd.DataFrame) -> dict:
    fs = add_week_start(fact_sales, "OrderDate")
    sales_by_week = fs.groupby("WeekStart", as_index=False)["Sales"].sum().sort_values("WeekStart")

    top_movers = (
        fact_sales.groupby("SKU", as_index=False)
        .agg({"Sales": "sum", "Units": "sum", "GrossMarginAmt": "sum", "DiscountAmt": "sum"})
        .sort_values("Sales", ascending=False)
        .head(10)
    )
    for c in ["Sales", "GrossMarginAmt", "DiscountAmt"]:
        top_movers[c] = top_movers[c].round(2)

    return {"sales_by_week": sales_by_week, "top_movers": top_movers}


def inventory_page_tables(fact_sales: pd.DataFrame, fact_inv: pd.DataFrame, dim_sku: pd.DataFrame, dim_store: pd.DataFrame) -> dict:
    # Current on hand (latest snapshot)
    latest = fact_inv["SnapshotDate"].max()
    inv_latest = fact_inv[fact_inv["SnapshotDate"] == latest].copy()

    # Units sold in last 28 days
    last_date = fact_sales["OrderDate"].max()
    start = last_date - pd.Timedelta(days=27)
    fs_28 = fact_sales[(fact_sales["OrderDate"] >= start) & (fact_sales["OrderDate"] <= last_date)].copy()

    sold = fs_28.groupby(["SKU", "Store"], as_index=False)["Units"].sum().rename(columns={"Units": "Units28d"})
    inv = inv_latest.groupby(["SKU", "Store"], as_index=False)["OnHandUnits"].sum()

    merged = inv.merge(sold, on=["SKU", "Store"], how="left").fillna({"Units28d": 0})
    merged = merged.merge(dim_sku[["SKU", "Category", "Brand"]], on="SKU", how="left")
    merged = merged.merge(dim_store[["Store", "Region"]], on="Store", how="left")

    # Avg weekly units proxy from last 28 days
    merged["AvgWeeklyUnits"] = merged["Units28d"] / 4.0

    merged["SellThrough%"] = merged.apply(lambda r: sell_through_pct(r["Units28d"], r["OnHandUnits"]), axis=1)
    merged["WOS"] = merged.apply(lambda r: weeks_of_supply(r["OnHandUnits"], r["AvgWeeklyUnits"]), axis=1)

    # Aggregate to Category and Store views
    by_category = (
        merged.groupby(["Category"], as_index=False)
        .agg({"OnHandUnits": "sum", "Units28d": "sum", "SellThrough%": "mean", "WOS": "mean"})
        .sort_values("Units28d", ascending=False)
    )
    by_store = (
        merged.groupby(["Store", "Region"], as_index=False)
        .agg({"OnHandUnits": "sum", "Units28d": "sum", "SellThrough%": "mean", "WOS": "mean"})
        .sort_values("Units28d", ascending=False)
        .head(15)
    )

    by_category["SellThrough%"] = by_category["SellThrough%"].round(4)
    by_category["WOS"] = by_category["WOS"].round(2)
    by_store["SellThrough%"] = by_store["SellThrough%"].round(4)
    by_store["WOS"] = by_store["WOS"].round(2)

    return {"by_category": by_category, "by_store": by_store, "latest_snapshot": latest}
