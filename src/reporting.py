from pathlib import Path
from typing import Dict

import pandas as pd
from tabulate import tabulate


def df_to_markdown_table(df: pd.DataFrame, max_rows: int = 10) -> str:
    """Convert a DataFrame to a markdown table string."""
    df_to_show = df.head(max_rows).copy()
    return tabulate(df_to_show, headers="keys", tablefmt="github", showindex=False)


def build_markdown_report(
    kpis: Dict,
    daily: pd.DataFrame,
    by_segment: pd.DataFrame,
    by_category: pd.DataFrame,
    by_region: pd.DataFrame,
) -> str:
    """Build a markdown report string from KPI and metric tables."""
    lines = []

    lines.append("# Revenue Metrics and Insights Report\n")
    lines.append("## Summary KPIs\n")
    lines.append(f"- Total revenue: {kpis['total_revenue']}")
    lines.append(f"- Total orders: {kpis['total_orders']}")
    lines.append(f"- Average order value: {kpis['avg_order_value']}")
    lines.append(
        f"- Date range: {kpis['start_date']} to {kpis['end_date']} "
        f"({kpis['n_days']} days)"
    )
    lines.append("")

    lines.append("## Daily Revenue Trend (top 10 rows)\n")
    lines.append(df_to_markdown_table(daily))
    lines.append("")

    lines.append("## Revenue by Customer Segment\n")
    lines.append(df_to_markdown_table(by_segment))
    lines.append("")

    lines.append("## Revenue by Category\n")
    lines.append(df_to_markdown_table(by_category))
    lines.append("")

    lines.append("## Revenue by Region\n")
    lines.append(df_to_markdown_table(by_region))
    lines.append("")

    return "\n".join(lines)


def save_report(report_text: str, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_text, encoding="utf8")
