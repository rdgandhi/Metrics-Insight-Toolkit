from __future__ import annotations
from dataclasses import dataclass
from typing import List
import pandas as pd


@dataclass
class ValidationResult:
    ok: bool
    errors: List[str]


def _require_columns(df: pd.DataFrame, required: List[str], name: str) -> List[str]:
    missing = [c for c in required if c not in df.columns]
    if missing:
        return [f"{name} missing columns: {missing}"]
    return []


def validate_tables(
    dim_date: pd.DataFrame,
    dim_sku: pd.DataFrame,
    dim_store: pd.DataFrame,
    dim_channel: pd.DataFrame,
    fact_sales: pd.DataFrame,
    fact_inv: pd.DataFrame,
) -> ValidationResult:
    errors: List[str] = []

    errors += _require_columns(dim_date, ["Date", "WeekStart"], "DimDate")
    errors += _require_columns(dim_sku, ["SKU", "Category", "Brand", "BasePrice"], "DimSKU")
    errors += _require_columns(dim_store, ["Store", "Region"], "DimStore")
    errors += _require_columns(dim_channel, ["Channel"], "DimChannel")

    errors += _require_columns(
        fact_sales,
        ["OrderDate", "OrderID", "SKU", "Store", "Channel", "Units", "Sales", "DiscountAmt", "GrossMarginAmt", "ReturnFlag"],
        "FactSales",
    )
    errors += _require_columns(fact_inv, ["SnapshotDate", "SKU", "Store", "OnHandUnits"], "FactInventorySnapshot")

    # Basic sanity checks
    if "Units" in fact_sales.columns and (fact_sales["Units"] < 0).any():
        errors.append("FactSales has negative Units.")
    if "Sales" in fact_sales.columns and (fact_sales["Sales"] < 0).any():
        errors.append("FactSales has negative Sales.")
    if "OnHandUnits" in fact_inv.columns and (fact_inv["OnHandUnits"] < 0).any():
        errors.append("FactInventorySnapshot has negative OnHandUnits.")

    return ValidationResult(ok=(len(errors) == 0), errors=errors)
