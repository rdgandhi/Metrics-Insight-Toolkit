# Metrics and Insight Reporting Toolkit

Small analytics toolkit that turns Superstore style transactional data into reusable metrics and a markdown insights report.

## Features

- Generates a synthetic Superstore style dataset
- Computes core revenue metrics
  - Daily revenue
  - Revenue by customer segment, category, and region
  - Summary KPIs such as total revenue and average order value
- Produces a markdown report for fast review or sharing

## Project structure

- `data/generate_superstore_data.py` script to generate sample data
- `src/metrics.py` metric computation functions
- `src/reporting.py` report generation helpers
- `src/main.py` command line entry point

## Setup

Create a virtual environment (optional but recommended), then install dependencies:

```bash
pip install -r requirements.txt
