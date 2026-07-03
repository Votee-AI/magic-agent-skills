#!/usr/bin/env python3
"""Generate large synthetic datasets for deep evaluation testing.

Usage:
    python generate_large_data.py --rows 10000
    python generate_large_data.py --rows 100000 --columns 50
    python generate_large_data.py --rows 500000 --streaming  # creates 10 chunk files
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORIES = ["Electronics", "Clothing", "Home", "Food", "Sports", "Books", "Health", "Auto"]
STATUSES = ["active", "inactive", "pending", "cancelled"]
CITIES = ["New York", "London", "Tokyo", "Paris", "Berlin", "Sydney", "Toronto", "Mumbai", "Shanghai", "São Paulo",
          "Lagos", "Cairo", "Moscow", "Seoul", "Bangkok", "Dubai", "Rome", "Madrid", "Amsterdam", "Vienna"]

def generate_messy_dataset(n_rows: int, n_extra_cols: int = 0, seed: int = SEED) -> pd.DataFrame:
    """Generate a messy dataset with controlled quality issues.

    Issues injected:
    - 5% missing in age, 10% missing in income, 15% missing in city
    - 2% outliers in purchase_amount (10x normal range)
    - 3% sentinel values ("N/A", "TBD", "unknown") in notes
    - 1% duplicate rows
    - Mixed date formats
    - Whitespace issues in text columns
    """
    rng = np.random.default_rng(seed)

    dates_raw = pd.date_range("2022-01-01", periods=n_rows, freq="h")[:n_rows]
    dates = []
    for i, d in enumerate(dates_raw):
        fmt = ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"][i % 3]
        dates.append(d.strftime(fmt))

    data = {
        "id": np.arange(1, n_rows + 1),
        "customer_name": [f"Customer_{i}" for i in range(n_rows)],
        "age": rng.integers(18, 80, size=n_rows).astype(float),
        "income": rng.uniform(20000, 150000, size=n_rows).round(2),
        "city": rng.choice(CITIES, size=n_rows),
        "region": rng.choice(REGIONS, size=n_rows),
        "category": rng.choice(CATEGORIES, size=n_rows),
        "purchase_amount": rng.lognormal(4, 1, size=n_rows).round(2),
        "quantity": rng.poisson(5, size=n_rows),
        "date_purchased": dates,
        "status": rng.choice(STATUSES, size=n_rows),
        "score": rng.uniform(0, 100, size=n_rows).round(2),
        "notes": [f"Note for order {i}" for i in range(n_rows)],
        "feedback": ["" if rng.random() < 0.3 else f"Feedback text {i}" for i in range(n_rows)],
        "is_active": rng.choice([True, False], size=n_rows, p=[0.7, 0.3]),
    }

    for j in range(n_extra_cols):
        col_type = j % 3
        if col_type == 0:
            data[f"numeric_{j}"] = rng.normal(100, 25, size=n_rows).round(2)
        elif col_type == 1:
            data[f"cat_{j}"] = rng.choice(["A", "B", "C", "D", "E"], size=n_rows)
        else:
            data[f"text_{j}"] = [f"text_{j}_{i}" for i in range(n_rows)]

    df = pd.DataFrame(data)

    # Inject missing values
    miss_age = rng.choice(df.index, size=int(n_rows * 0.05), replace=False)
    df.loc[miss_age, "age"] = np.nan

    miss_income = rng.choice(df.index, size=int(n_rows * 0.10), replace=False)
    df.loc[miss_income, "income"] = np.nan

    miss_city = rng.choice(df.index, size=int(n_rows * 0.15), replace=False)
    df.loc[miss_city, "city"] = np.nan

    # Inject outliers
    outlier_idx = rng.choice(df.index, size=max(1, int(n_rows * 0.02)), replace=False)
    df.loc[outlier_idx, "purchase_amount"] = rng.uniform(50000, 200000, size=len(outlier_idx))

    # Inject sentinels in notes
    sentinel_idx = rng.choice(df.index, size=int(n_rows * 0.03), replace=False)
    sentinels = ["N/A", "TBD", "unknown", "placeholder", "  "]
    df.loc[sentinel_idx, "notes"] = rng.choice(sentinels, size=len(sentinel_idx))

    # Inject duplicates (1%)
    dup_idx = rng.choice(df.index, size=max(1, int(n_rows * 0.01)), replace=True)
    dupes = df.loc[dup_idx].copy()
    df = pd.concat([df, dupes], ignore_index=True)

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate large test datasets")
    parser.add_argument("--rows", type=int, default=10000, help="Number of rows")
    parser.add_argument("--columns", type=int, default=15, help="Total columns (15 base + N extra)")
    parser.add_argument("--streaming", action="store_true", help="Split into 10 chunk files")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    out = Path(args.output_dir) if args.output_dir else Path(__file__).parent / "datasets"
    out.mkdir(parents=True, exist_ok=True)

    extra_cols = max(0, args.columns - 15)
    print(f"Generating {args.rows:,} rows, {args.columns} columns (seed={args.seed})...")

    df = generate_messy_dataset(args.rows, extra_cols, args.seed)

    if args.streaming:
        chunk_size = len(df) // 10
        for i in range(10):
            chunk = df.iloc[i * chunk_size:(i + 1) * chunk_size]
            fp = out / f"stream_chunk_{i:02d}.csv"
            chunk.to_csv(fp, index=False)
            print(f"  {fp.name}: {len(chunk):,} rows ({fp.stat().st_size / 1024:.0f} KB)")
    else:
        tag = f"large_{args.rows // 1000}k" if args.rows >= 1000 else f"large_{args.rows}"
        fp = out / f"{tag}.csv"
        df.to_csv(fp, index=False)
        print(f"  {fp.name}: {len(df):,} rows, {len(df.columns)} cols ({fp.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
