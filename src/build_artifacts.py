from __future__ import annotations
import argparse

from src.metrics import load_tables, kpi_summary, exec_page_tables, inventory_page_tables, avg_weekly_units, stockout_days
from src.reporting import md_table, write_text, metric_definitions_md
from src.validate import validate_tables


def build_report(data_dir: str, report_path: str, defs_path: str, one_pager_path: str) -> None:
    t = load_tables(data_dir)

    vr = validate_tables(
        t["DimDate"], t["DimSKU"], t["DimStore"], t["DimChannel"], t["FactSales"], t["FactInventorySnapshot"]
    )
    if not vr.ok:
        raise ValueError("Validation failed:\n" + "\n".join(vr.errors))

    fs = t["FactSales"]
    inv = t["FactInventorySnapshot"]

    kpis = kpi_summary(fs)
    avg_week = avg_weekly_units(fs)
    stockouts = stockout_days(inv)

    exec_tables = exec_page_tables(fs)
    inv_tables = inventory_page_tables(fs, inv, t["DimSKU"], t["DimStore"])

    report = []
    report.append("# Merchandising Metrics Report\n")
    report.append("## Executive KPIs\n")
    for k, v in kpis.items():
        report.append(f"- {k}: {v}")
    report.append(f"- Avg Weekly Units (proxy): {round(avg_week, 2)}")
    report.append(f"- Stockout Days (proxy): {stockouts}")
    report.append("")

    report.append("## Trend: Sales $ by Week\n")
    report.append(md_table(exec_tables["sales_by_week"], max_rows=12))
    report.append("")

    report.append("## Top Movers (Top 10 SKUs)\n")
    report.append(md_table(exec_tables["top_movers"], max_rows=10))
    report.append("")

    report.append("## Inventory Health (Latest Snapshot)\n")
    report.append(f"- Latest snapshot date: {inv_tables['latest_snapshot'].date().isoformat()}")
    report.append("")
    report.append("### Inventory by Category\n")
    report.append(md_table(inv_tables["by_category"], max_rows=12))
    report.append("")
    report.append("### Inventory by Store (Top 15 by Units Sold)\n")
    report.append(md_table(inv_tables["by_store"], max_rows=15))
    report.append("")

    write_text(report_path, "\n".join(report))
    write_text(defs_path, metric_definitions_md())

    one_pager = f"""# One Pager: Merchandising Analytics Toolkit

## Business question
Which categories, brands, and SKUs are driving Sales and Gross Margin, and where are we at risk on inventory health (Sell-through, Weeks of Supply, Stockouts) across stores and channels?

## Data model
Star schema:
- **FactSales** (OrderDate, SKU, Store, Channel, Units, Sales, DiscountAmt, GrossMarginAmt, ReturnFlag)
- **FactInventorySnapshot** (SnapshotDate, SKU, Store, OnHandUnits)
Joined to **DimDate**, **DimSKU**, **DimStore**, **DimChannel**.

## Measures governed
See `reports/metric_definitions.md`. Core KPIs:
Sales $, Units, GM %, Markdown Rate %, AOV, Sell-through %, WOS, Stockout proxy.

## Adoption intent
- Merch leaders review **Merch Executive** weekly to track Sales, GM, promo pressure, and top movers.
- Planners review **Inventory** daily to monitor Sell-through, WOS, and stockout risk by category and store.
- Analysts use **Drivers** to isolate whether performance changes are driven by Units, Discounting, or price mix.

## Outputs created by this project
- Markdown KPI report: `{report_path}`
- Metric definitions (governance): `{defs_path}`
"""
    write_text(one_pager_path, one_pager)


def main() -> None:
    p = argparse.ArgumentParser(description="End to end merchandising analytics artifacts builder.")
    p.add_argument("--data_dir", type=str, default="data_out")
    p.add_argument("--report_path", type=str, default="reports/merch_kpi_report.md")
    p.add_argument("--defs_path", type=str, default="reports/metric_definitions.md")
    p.add_argument("--one_pager_path", type=str, default="docs/one_pager.md")
    args = p.parse_args()

    build_report(args.data_dir, args.report_path, args.defs_path, args.one_pager_path)
    print("Artifacts generated:")
    print(f"- {args.report_path}")
    print(f"- {args.defs_path}")
    print(f"- {args.one_pager_path}")


if __name__ == "__main__":
    main()
