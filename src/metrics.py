from typing import Dict
import pandas as pd


def load_superstore(csv_path: str) -> pd.DataFrame:
    """Load and basic clean of Superstore style data."""
    df = pd.read_csv(csv_path, parse_dates=["Order Date"])
    # Standardize text fields
    for col in ["Segment", "Region", "Category", "Sub Category", "Ship Mode"]:
        df[col] = df[col].astype(str).str.strip()
    return df


def daily_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by day."""
    return (
        df.groupby("Order Date", as_index=False)["Sales"]
        .sum()
        .rename(columns={"Sales": "Daily Revenue"})
        .sort_values("Order Date")
    )


def revenue_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by customer segment."""
    return (
        df.groupby("Segment", as_index=False)["Sales"]
        .sum()
        .rename(columns={"Sales": "Segment Revenue"})
        .sort_values("Segment Revenue", ascending=False)
    )


def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by product category."""
    return (
        df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .rename(columns={"Sales": "Category Revenue"})
        .sort_values("Category Revenue", ascending=False)
    )


def revenue_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by region."""
    return (
        df.groupby("Region", as_index=False)["Sales"]
        .sum()
        .rename(columns={"Sales": "Region Revenue"})
        .sort_values("Region Revenue", ascending=False)
    )


def kpi_summary(df: pd.DataFrame) -> Dict:
    """Compute simple KPI dictionary."""
    total_revenue = df["Sales"].sum()
    total_orders = len(df)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    first_date = df["Order Date"].min()
    last_date = df["Order Date"].max()

    return {
        "total_revenue": round(float(total_revenue), 2),
        "total_orders": int(total_orders),
        "avg_order_value": round(float(avg_order_value), 2),
        "start_date": first_date.date().isoformat(),
        "end_date": last_date.date().isoformat(),
        "n_days": int((last_date - first_date).days) + 1,
    }
