#!/usr/bin/env python3
"""
Generate synthetic E2E test datasets for scenario testing.

Creates 5 datasets with controlled issues for reproducible E2E testing.
All data generated with seed=42.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Reuse word lists from the unit test data generator
sys.path.insert(0, str(Path(__file__).parent.parent))
from generate_test_data import (
    FIRST_NAMES, LAST_NAMES, CITIES, EUROPEAN_CITIES,
    CATEGORIES, TEXT_CATEGORIES, STATUS_VALUES,
    ADJECTIVES, NOUNS, VERBS,
    generate_text, generate_paragraph, generate_date_range, get_file_size,
    set_seed
)

REGIONS = ["North", "South", "East", "West"]


def generate_full_pipeline_messy(n=10000):
    """Generate messy dataset for the full pipeline scenario.
    
    10,000 rows, 15 columns with:
    - Missing values: age (3%), income (8%), city (15%)
    - 45 duplicate rows
    - Outliers in purchase_amount and quantity
    - Mixed date formats
    - 3 text columns (description, notes, feedback)
    - Whitespace issues in notes
    """
    set_seed(42)
    
    # Generate dates in mixed formats
    raw_dates = generate_date_range('2022-01-01', '2024-12-31', n)
    dates = []
    for i, d in enumerate(raw_dates):
        if i % 3 == 0:
            dates.append(d.strftime('%Y-%m-%d'))
        elif i % 3 == 1:
            dates.append(d.strftime('%m/%d/%Y'))
        else:
            dates.append(d.strftime('%d-%m-%Y'))
    
    data = {
        'id': range(1, n + 1),
        'customer_name': [f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}" for _ in range(n)],
        'age': np.random.randint(18, 81, size=n).astype(float),
        'income': np.random.uniform(20000, 150000, size=n).round(2),
        'city': np.random.choice(CITIES, size=n).astype(object),
        'product_category': np.random.choice(CATEGORIES, size=n),
        'purchase_amount': np.random.lognormal(4, 1, size=n).round(2),
        'quantity': np.random.poisson(5, size=n),
        'date_purchased': dates,
        'is_active': np.random.choice([True, False], size=n, p=[0.7, 0.3]),
        'description': [generate_text(8, 20) for _ in range(n)],
        'notes': [generate_text(5, 15) for _ in range(n)],
        'feedback': [generate_paragraph(2, 5) if np.random.random() > 0.3 else "" for _ in range(n)],
        'score': np.random.uniform(0, 100, size=n).round(2),
        'region': np.random.choice(REGIONS, size=n),
    }
    
    df = pd.DataFrame(data)
    
    # Inject missing values
    age_idx = np.random.choice(df.index, size=int(n * 0.03), replace=False)
    df.loc[age_idx, 'age'] = np.nan
    
    income_idx = np.random.choice(df.index, size=int(n * 0.08), replace=False)
    df.loc[income_idx, 'income'] = np.nan
    
    city_idx = np.random.choice(df.index, size=int(n * 0.15), replace=False)
    df.loc[city_idx, 'city'] = np.nan
    
    # Inject outliers
    outlier_idx = np.random.choice(df.index, size=8, replace=False)
    df.loc[outlier_idx[:5], 'purchase_amount'] = np.random.uniform(50000, 200000, size=5)
    df.loc[outlier_idx[5:], 'quantity'] = np.random.randint(500, 1000, size=3)
    
    # Inject whitespace issues in notes
    ws_idx = np.random.choice(df.index, size=int(n * 0.05), replace=False)
    df.loc[ws_idx, 'notes'] = "  " + df.loc[ws_idx, 'notes'].astype(str) + "   "
    
    # Add 45 duplicate rows
    dup_idx = np.random.choice(df.index, size=45, replace=True)
    dupes = df.loc[dup_idx].copy()
    df = pd.concat([df, dupes], ignore_index=True)
    
    return df


def generate_latin1_encoded(n=500):
    """Generate Latin-1 encoded dataset with accented characters."""
    set_seed(42)
    
    accented_first = ["André", "François", "José", "María", "Stéphanie", "Sébastien",
                      "Béatrice", "Céline", "Hélène", "Jérôme", "Amélie", "Émilie"]
    accented_last = ["Müller", "García", "López", "Pérez", "Dupré", "Lefèvre",
                     "González", "Rodríguez", "Martínez", "Sánchez"]
    
    descriptions = [
        "Café très agréable avec une belle terrasse",
        "Hôtel de qualité supérieure au centre-ville",
        "Restaurant français avec cuisine traditionnelle",
        "Librairie spécialisée en littérature étrangère",
        "Université renommée pour la recherche scientifique",
        "Musée d'art contemporain et d'histoire naturelle",
        "Théâtre classique avec programmation variée",
        "Société d'électronique et de télécommunications",
        "Pâtisserie artisanale proposant des spécialités régionales",
    ]
    
    data = {
        'id': range(1, n + 1),
        'name': [f"{np.random.choice(accented_first)} {np.random.choice(accented_last)}" for _ in range(n)],
        'city': np.random.choice(EUROPEAN_CITIES, size=n),
        'description': [np.random.choice(descriptions) for _ in range(n)],
        'amount': np.random.uniform(100, 10000, size=n).round(2),
    }
    
    return pd.DataFrame(data)


def generate_mixed_types(n=1000):
    """Generate dataset with string values in numeric columns."""
    set_seed(42)
    
    dates = generate_date_range('2023-01-01', '2024-12-31', n)
    
    data = {
        'id': range(1, n + 1),
        'age': np.random.randint(18, 81, size=n).astype(float),
        'income': np.random.uniform(20000, 150000, size=n).round(2),
        'score': np.random.uniform(0, 100, size=n).round(2),
        'status': np.random.choice(STATUS_VALUES, size=n),
        'date': [d.strftime('%Y-%m-%d') for d in dates],
    }
    
    df = pd.DataFrame(data)
    
    # Convert numeric cols to object to allow string injection
    for col in ['age', 'income', 'score']:
        df[col] = df[col].astype(object)
    
    # Inject string values
    age_idx = np.random.choice(df.index, size=int(n * 0.05), replace=False)
    df.loc[age_idx, 'age'] = "N/A"
    
    income_idx = np.random.choice(df.index, size=int(n * 0.03), replace=False)
    df.loc[income_idx, 'income'] = "unknown"
    
    score_idx = np.random.choice(df.index, size=int(n * 0.02), replace=False)
    df.loc[score_idx, 'score'] = "null"
    
    return df


def generate_semicolon_delimited(n=800):
    """Generate semicolon-delimited CSV."""
    set_seed(42)
    
    dates = generate_date_range('2023-01-01', '2024-12-31', n)
    
    data = {
        'id': range(1, n + 1),
        'name': [f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}" for _ in range(n)],
        'city': np.random.choice(CITIES, size=n),
        'amount': np.random.uniform(100, 10000, size=n).round(2),
        'category': np.random.choice(CATEGORIES, size=n),
        'date': [d.strftime('%Y-%m-%d') for d in dates],
        'score': np.random.uniform(0, 100, size=n).round(2),
        'active': np.random.choice(['yes', 'no'], size=n),
    }
    
    return pd.DataFrame(data)


def generate_text_corpus(n=200):
    """Generate JSONL text corpus with 4 label categories."""
    set_seed(42)
    
    records = []
    labels = TEXT_CATEGORIES  # Technology, Health, Business, Entertainment
    
    for i in range(1, n + 1):
        label = labels[(i - 1) % len(labels)]
        text = generate_paragraph(5, 15)
        records.append({
            'id': i,
            'text': text,
            'label': label,
            'word_count': len(text.split()),
        })
    
    return records


def main():
    parser = argparse.ArgumentParser(description='Generate E2E test datasets')
    parser.add_argument('--output-dir', default=None,
                        help='Output directory (default: tests/e2e/datasets/)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    args = parser.parse_args()
    
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(__file__).parent / 'datasets'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    np.random.seed(args.seed)
    
    print(f"Generating E2E datasets in: {output_dir.absolute()}")
    print("=" * 70)
    
    results = []
    
    # 1. Full pipeline messy dataset
    print("Generating full_pipeline_messy.csv (10k rows, 15 cols)...")
    df = generate_full_pipeline_messy(10000)
    fp = output_dir / 'full_pipeline_messy.csv'
    df.to_csv(fp, index=False)
    results.append(('full_pipeline_messy.csv', len(df), get_file_size(fp)))
    
    # 2. Latin-1 encoded dataset
    print("Generating latin1_encoded.csv (500 rows, Latin-1 encoding)...")
    df = generate_latin1_encoded(500)
    fp = output_dir / 'latin1_encoded.csv'
    df.to_csv(fp, index=False, encoding='latin-1')
    results.append(('latin1_encoded.csv', len(df), get_file_size(fp)))
    
    # 3. Mixed types dataset
    print("Generating mixed_types.csv (1k rows, string values in numeric cols)...")
    df = generate_mixed_types(1000)
    fp = output_dir / 'mixed_types.csv'
    df.to_csv(fp, index=False)
    results.append(('mixed_types.csv', len(df), get_file_size(fp)))
    
    # 4. Semicolon delimited dataset
    print("Generating semicolon_delimited.csv (800 rows, ; delimiter)...")
    df = generate_semicolon_delimited(800)
    fp = output_dir / 'semicolon_delimited.csv'
    df.to_csv(fp, index=False, sep=';')
    results.append(('semicolon_delimited.csv', len(df), get_file_size(fp)))
    
    # 5. Text corpus JSONL
    print("Generating text_corpus.jsonl (200 records, 4 labels)...")
    records = generate_text_corpus(200)
    fp = output_dir / 'text_corpus.jsonl'
    with open(fp, 'w') as f:
        for record in records:
            f.write(json.dumps(record) + '\n')
    results.append(('text_corpus.jsonl', len(records), get_file_size(fp)))
    
    print("=" * 70)
    print(f"\n{'Filename':<35} {'Rows':>8} {'Size':>12}")
    print("-" * 70)
    for filename, rows, size in results:
        print(f"{filename:<35} {rows:>8} {size:>12}")
    
    print(f"\nAll E2E datasets generated in: {output_dir.absolute()}")


if __name__ == '__main__':
    main()
