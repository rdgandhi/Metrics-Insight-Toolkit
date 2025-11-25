# Metrics and Insight Reporting Toolkit

This project is an end to end analytics solution that combines a Python based metrics engine with a three page Power BI dashboard. Together, they form a complete workflow for generating, analyzing, and visualizing retail style revenue data using a synthetic Superstore dataset.

The toolkit demonstrates practical data analysis, metric design, dashboarding, and reporting techniques used by data analysts and BI professionals.

---

## Project Components

### 1. Synthetic Data Generation (`/data`)
- `generate_superstore_data.py` creates realistic retail transactions with sales, profit, category, region, segment, and discount fields.
- `superstore_sample_large.csv` contains a generated sample used across the toolkit.
- Fully reproducible with adjustable row counts.

### 2. Python Metrics Engine (`/src`)
The Python pipeline:
- Loads and validates the dataset
- Computes core business metrics:
  - Daily revenue
  - Revenue by segment, category, and region
  - Summary KPIs (total revenue, total orders, AOV)
- Generates a Markdown insights report that can be viewed directly in GitHub.
- Designed with clear modular structure for real analytical workflows.

Run the report:

```bash
python -m src.main --input data/superstore_sample_large.csv --output reports/metrics_report.md
