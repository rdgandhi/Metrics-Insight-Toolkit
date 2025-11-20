import argparse
from pathlib import Path
import numpy as np
import pandas as pd


SEGMENTS = ["Consumer", "Corporate", "Home Office"]
REGIONS = ["West", "East", "Central", "South"]
CATEGORIES = ["Technology", "Furniture", "Office Supplies"]
SUBCATS = {
    "Technology": ["Phones", "Accessories", "Machines", "Copiers"],
    "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Binders", "Paper", "Storage", "Art"],
}
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]


def generate_superstore_data(n_rows: int, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)

    dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")

    rows = []
    for i in range(n_rows):
        category = np.random.choice(CATEGORIES)
        sales = np.random.uniform(20, 2000)
        discount = np.random.choice([0.0, 0.1, 0.2, 0.3])
        quantity = np.random.randint(1, 10)
        # simple profit model
        profit = sales * (0.15 - discount * 0.3)

        row = {
            "Order ID": f"CA-{100000 + i}",
            "Order Date": np.random.choice(dates),
            "Segment": np.random.choice(SEGMENTS),
            "Region": np.random.choice(REGIONS),
            "Category": category,
            "Sub Category": np.random.choice(SUBCATS[category]),
            "Ship Mode": np.random.choice(SHIP_MODES),
            "Customer Name": f"Customer {np.random.randint(1, 500)}",
            "Sales": round(sales, 2),
            "Quantity": int(quantity),
            "Discount": round(discount, 2),
            "Profit": round(profit, 2),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a synthetic Superstore style dataset."
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=10000,
        help="Number of rows to generate (default: 10000).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/superstore_sample_large.csv",
        help="Path to output CSV file.",
    )
    args = parser.parse_args()

    df = generate_superstore_data(args.rows)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated dataset with {len(df)} rows at {output_path.resolve()}")


if __name__ == "__main__":
    main()
