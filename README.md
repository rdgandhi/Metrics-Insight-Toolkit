# Merchandising Metrics and Insight Toolkit (Power BI + Governed Metrics)

End to end merchandising analytics project that generates a retail star schema dataset, computes governed KPIs, produces stakeholder-ready artifacts, and supports a three page Power BI dashboard.

## What it does
1. Generates a merchandising star schema dataset:
   - FactSales, FactInventorySnapshot
   - DimDate, DimSKU, DimStore, DimChannel
2. Computes governed merchandising KPIs:
   - Sales $, Units, GM %, Markdown Rate %, AOV
   - Sell-through %, Weeks of Supply (WOS), Stockout proxy
3. Produces artifacts automatically:
   - `reports/merch_kpi_report.md`
   - `reports/metric_definitions.md`
   - `docs/one_pager.md`
4. Power BI support:
   - DAX measures and model instructions in `/powerbi`

## Run end to end
Install:
```bash
pip install -r requirements.txt


## Generate Data
python data/generate_merchandising_data.py --rows_orders 30000 --n_skus 250 --n_stores 30 --out_dir data_out

## Build artifacts:
python -m src.build_artifacts --data_dir data_out
