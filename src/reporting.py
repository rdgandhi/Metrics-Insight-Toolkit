from __future__ import annotations
from pathlib import Path
from typing import Dict
from tabulate import tabulate
import pandas as pd


def md_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    return tabulate(df.head(max_rows), headers="keys", tablefmt="github", showindex=False)


def write_text(path: str, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf8")


def metric_definitions_md() -> str:
    return """# Metric Definitions (Governed)

These definitions are used consistently across the Python report and the Power BI dashboard.

- **Sales $**: Net sales after discounts.
- **Orders**: Distinct count of OrderID.
- **AOV**: Sales $ / Orders.
- **Units**: Sum of Units sold.
- **Markdown $**: Sum of DiscountAmt.
- **Markdown Rate %**: Markdown $ / (Sales $ + Markdown $). (Uses gross sales basis.)
- **GM $**: Sum of GrossMarginAmt.
- **GM %**: GM $ / Sales $.
- **On Hand Units**: Latest snapshot OnHandUnits.
- **Sell-through %**: Units Sold / (Units Sold + On Hand Units). (Proxy for synthetic inventory.)
- **Weeks of Supply (WOS)**: On Hand Units / Avg Weekly Units. (Avg weekly based on last 28 days.)
- **Stockout proxy**: Number of days where total On Hand Units = 0.
"""
