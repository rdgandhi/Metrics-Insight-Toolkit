# One Pager: Merchandising Analytics Toolkit

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
- Markdown KPI report: `reports/merch_kpi_report.md`
- Metric definitions (governance): `reports/metric_definitions.md`
