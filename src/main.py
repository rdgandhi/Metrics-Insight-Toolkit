import argparse
from pathlib import Path

from src.metrics import (
    load_superstore,
    daily_revenue,
    revenue_by_segment,
    revenue_by_category,
    revenue_by_region,
    kpi_summary,
)
from src.reporting import build_markdown_report, save_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate metrics and an insights report from Superstore style data."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input CSV file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/metrics_report.md",
        help="Path to output markdown report.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    df = load_superstore(args.input)

    daily = daily_revenue(df)
    by_segment = revenue_by_segment(df)
    by_category = revenue_by_category(df)
    by_region = revenue_by_region(df)
    kpis = kpi_summary(df)

    report_text = build_markdown_report(
        kpis, daily, by_segment, by_category, by_region
    )
    save_report(report_text, args.output)

    print(f"Report generated at {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
