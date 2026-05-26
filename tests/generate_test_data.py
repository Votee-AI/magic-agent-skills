#!/usr/bin/env python3
"""
Generate synthetic test datasets for data science skills testing.

This script creates multiple CSV and JSONL files with various data characteristics
for comprehensive testing of data loading, profiling, cleaning, and validation skills.

All random data is generated with seed=42 for reproducibility.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


# Word lists for generating realistic text data
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "André", "María", "François", "José", "Pierre", "Jean", "Sébastien", "Stéphanie"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Dupont", "Müller", "García", "López", "González", "Pérez", "Rodríguez"
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Indianapolis"
]

EUROPEAN_CITIES = [
    "Paris", "München", "Zürich", "Genève", "Montréal",
    "Málaga", "São Paulo", "Québec", "Bruxelles", "Strasbourg"
]

CATEGORIES = ["Electronics", "Clothing", "Food", "Books", "Sports"]
TEXT_CATEGORIES = ["Technology", "Health", "Business", "Entertainment"]
STATUS_VALUES = ["active", "inactive", "pending", "suspended"]

ADJECTIVES = [
    "quick", "lazy", "happy", "serious", "innovative", "efficient", "modern",
    "traditional", "advanced", "simple", "complex", "effective", "powerful",
    "flexible", "robust", "reliable", "scalable", "sustainable", "dynamic"
]

NOUNS = [
    "solution", "approach", "system", "method", "strategy", "framework", "platform",
    "process", "service", "product", "technology", "tool", "application", "interface",
    "architecture", "model", "design", "implementation", "workflow", "protocol"
]

VERBS = [
    "optimize", "enhance", "improve", "develop", "implement", "create", "design",
    "build", "integrate", "streamline", "automate", "transform", "revolutionize",
    "accelerate", "simplify", "strengthen", "expand", "upgrade", "modernize"
]


def set_seed(seed=42):
    """Set random seed for reproducibility."""
    np.random.seed(seed)


def generate_text(min_words=5, max_words=15):
    """Generate random text from word lists."""
    n_words = np.random.randint(min_words, max_words + 1)
    words = []
    for _ in range(n_words):
        word_type = np.random.choice(['adj', 'noun', 'verb'])
        if word_type == 'adj':
            words.append(np.random.choice(ADJECTIVES))
        elif word_type == 'noun':
            words.append(np.random.choice(NOUNS))
        else:
            words.append(np.random.choice(VERBS))
    return ' '.join(words).capitalize()


def generate_paragraph(min_sentences=3, max_sentences=8):
    """Generate a paragraph of text."""
    n_sentences = np.random.randint(min_sentences, max_sentences + 1)
    sentences = [generate_text(5, 15) + '.' for _ in range(n_sentences)]
    return ' '.join(sentences)


def generate_date_range(start_date, end_date, n):
    """Generate random dates between start and end."""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    delta = (end - start).days
    random_days = np.random.randint(0, delta + 1, size=n)
    return [start + timedelta(days=int(d)) for d in random_days]


def generate_sample_clean(n=1000):
    """Generate clean dataset with no issues."""
    set_seed(42)

    dates = generate_date_range('2023-01-01', '2024-12-31', n)

    data = {
        'id': range(1, n + 1),
        'name': [f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}" for _ in range(n)],
        'age': np.random.randint(18, 81, size=n),
        'income': np.random.uniform(20000, 150000, size=n).round(2),
        'city': np.random.choice(CITIES, size=n),
        'score': np.random.uniform(0, 100, size=n).round(2),
        'date': dates,
        'is_active': np.random.choice([True, False], size=n)
    }

    return pd.DataFrame(data)


def generate_sample_missing(n=1000):
    """Generate dataset with missing values."""
    set_seed(42)
    df = generate_sample_clean(n)

    # Introduce missing values
    # age: 3% missing
    age_missing_idx = np.random.choice(df.index, size=int(n * 0.03), replace=False)
    df.loc[age_missing_idx, 'age'] = np.nan

    # income: 8% missing
    income_missing_idx = np.random.choice(df.index, size=int(n * 0.08), replace=False)
    df.loc[income_missing_idx, 'income'] = np.nan

    # city: 52% missing (high missingness)
    city_missing_idx = np.random.choice(df.index, size=int(n * 0.52), replace=False)
    df.loc[city_missing_idx, 'city'] = np.nan

    return df


def generate_sample_outliers(n=1000):
    """Generate dataset with extreme outliers."""
    set_seed(42)

    # Normal data
    revenue = np.random.normal(5000, 1000, size=n)
    cost = np.random.normal(3000, 600, size=n)
    margin = np.random.normal(0.3, 0.1, size=n)
    count = np.random.poisson(100, size=n)

    # Add 5 extreme outliers to each numeric column
    outlier_indices = np.random.choice(n, size=5, replace=False)
    revenue[outlier_indices] = np.random.uniform(500000, 1000000, size=5)
    cost[outlier_indices] = np.random.uniform(400000, 800000, size=5)

    # Different outliers for margin and count
    margin_outlier_idx = np.random.choice(n, size=5, replace=False)
    margin[margin_outlier_idx] = np.random.uniform(5, 10, size=5)

    count_outlier_idx = np.random.choice(n, size=5, replace=False)
    count[count_outlier_idx] = np.random.randint(10000, 50000, size=5)

    data = {
        'id': range(1, n + 1),
        'revenue': revenue.round(2),
        'cost': cost.round(2),
        'profit': (revenue - cost).round(2),
        'margin': margin.round(4),
        'count': count
    }

    return pd.DataFrame(data)


def generate_sample_duplicates(n=1000, n_duplicates=50):
    """Generate dataset with exact row duplicates."""
    set_seed(42)
    df = generate_sample_clean(n)

    # Add duplicates by repeating random rows
    duplicate_indices = np.random.choice(df.index, size=n_duplicates, replace=True)
    duplicates = df.loc[duplicate_indices].copy()

    df_with_dupes = pd.concat([df, duplicates], ignore_index=True)

    return df_with_dupes


def generate_sample_text(n=500):
    """Generate text dataset."""
    set_seed(42)

    data = {
        'id': range(1, n + 1),
        'title': [generate_text(5, 15) for _ in range(n)],
        'description': [generate_paragraph(3, 8) for _ in range(n)],
        'category': np.random.choice(CATEGORIES, size=n),
        'word_count': np.random.randint(50, 500, size=n)
    }

    return pd.DataFrame(data)


def generate_sample_mixed_types(n=1000):
    """Generate dataset with mixed type issues (N/A, unknown in numeric columns)."""
    set_seed(42)

    dates = generate_date_range('2023-01-01', '2024-12-31', n)

    # Create base numeric data
    age = np.random.randint(18, 81, size=n).astype(float)
    income = np.random.uniform(20000, 150000, size=n)
    score = np.random.uniform(0, 100, size=n)

    data = {
        'id': range(1, n + 1),
        'age': age,
        'income': income,
        'status': np.random.choice(STATUS_VALUES, size=n),
        'score': score,
        'date': dates
    }

    df = pd.DataFrame(data)

    # Convert to object dtype to allow string values
    df['age'] = df['age'].astype(object)
    df['income'] = df['income'].astype(object)
    df['score'] = df['score'].astype(object)

    # Introduce string values in numeric columns
    # age: 5% "N/A"
    age_na_idx = np.random.choice(df.index, size=int(n * 0.05), replace=False)
    df.loc[age_na_idx, 'age'] = "N/A"

    # income: 3% "unknown"
    income_unknown_idx = np.random.choice(df.index, size=int(n * 0.03), replace=False)
    df.loc[income_unknown_idx, 'income'] = "unknown"

    # score: 2% "null"
    score_null_idx = np.random.choice(df.index, size=int(n * 0.02), replace=False)
    df.loc[score_null_idx, 'score'] = "null"

    return df


def generate_sample_latin1(n=500):
    """Generate Latin-1 encoded dataset with accented characters."""
    set_seed(42)

    # Names with accents
    accented_first = ["André", "François", "José", "María", "Stéphanie", "Sébastien",
                     "Béatrice", "Céline", "Hélène", "Jérôme", "Amélie", "Émilie"]
    accented_last = ["Müller", "García", "López", "Pérez", "Dupré", "Lefèvre",
                    "González", "Rodríguez", "Martínez", "Sánchez"]

    names = [f"{np.random.choice(accented_first)} {np.random.choice(accented_last)}" for _ in range(n)]
    cities = [np.random.choice(EUROPEAN_CITIES) for _ in range(n)]

    descriptions = [
        "Café très agréable", "Hôtel de qualité supérieure", "Restaurant français",
        "Librairie spécialisée", "Université renommée", "Musée d'art contemporain",
        "Théâtre classique", "Société d'électronique", "Pâtisserie artisanale"
    ]

    data = {
        'id': range(1, n + 1),
        'name': names,
        'city': cities,
        'description': [np.random.choice(descriptions) for _ in range(n)],
        'amount': np.random.uniform(100, 10000, size=n).round(2)
    }

    return pd.DataFrame(data)


def generate_sample_jsonl(n=200):
    """Generate JSONL dataset."""
    set_seed(42)

    data = []
    for i in range(1, n + 1):
        record = {
            'id': i,
            'text': generate_paragraph(5, 15),
            'label': np.random.choice(TEXT_CATEGORIES)
        }
        data.append(record)

    return data


def generate_sample_large(n=100000):
    """Generate large dataset for performance testing."""
    set_seed(42)

    dates = generate_date_range('2020-01-01', '2024-12-31', n)

    data = {
        'id': range(1, n + 1),
        # Numeric columns (10)
        'value1': np.random.uniform(0, 1000, size=n).round(2),
        'value2': np.random.normal(500, 100, size=n).round(2),
        'value3': np.random.exponential(50, size=n).round(2),
        'value4': np.random.uniform(0, 100, size=n).round(2),
        'value5': np.random.randint(0, 1000, size=n),
        'amount': np.random.uniform(10, 10000, size=n).round(2),
        'quantity': np.random.poisson(50, size=n),
        'score': np.random.uniform(0, 100, size=n).round(2),
        'rating': np.random.uniform(1, 5, size=n).round(1),
        'metric': np.random.normal(100, 25, size=n).round(2),
        # Categorical columns (5)
        'category1': np.random.choice(CATEGORIES, size=n),
        'category2': np.random.choice(STATUS_VALUES, size=n),
        'region': np.random.choice(['North', 'South', 'East', 'West'], size=n),
        'type': np.random.choice(['Type A', 'Type B', 'Type C'], size=n),
        'segment': np.random.choice(['Premium', 'Standard', 'Basic'], size=n),
        # Text columns (3)
        'description': [generate_text(5, 10) if i % 10 == 0 else generate_text(3, 6) for i in range(n)],
        'notes': [generate_text(8, 15) if i % 5 == 0 else '' for i in range(n)],
        'comment': [generate_paragraph(2, 4) if i % 20 == 0 else '' for i in range(n)],
        # Datetime column (1)
        'timestamp': dates,
        # Boolean column (1)
        'is_verified': np.random.choice([True, False], size=n, p=[0.7, 0.3])
    }

    return pd.DataFrame(data)


def get_file_size(filepath):
    """Get human-readable file size."""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic test datasets')
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for generated files (default: tests/unit/test_data/)'
    )
    args = parser.parse_args()

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # Default: script is in tests/, output to tests/unit/test_data/
        script_dir = Path(__file__).parent
        output_dir = script_dir / 'unit' / 'test_data'

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating test datasets in: {output_dir.absolute()}")
    print("=" * 80)

    results = []

    # 1. Clean dataset
    print("Generating sample_clean.csv...")
    df = generate_sample_clean(1000)
    filepath = output_dir / 'sample_clean.csv'
    df.to_csv(filepath, index=False)
    results.append(('sample_clean.csv', len(df), get_file_size(filepath)))

    # 2. Missing values dataset
    print("Generating sample_missing.csv...")
    df = generate_sample_missing(1000)
    filepath = output_dir / 'sample_missing.csv'
    df.to_csv(filepath, index=False)
    results.append(('sample_missing.csv', len(df), get_file_size(filepath)))

    # 3. Outliers dataset
    print("Generating sample_outliers.csv...")
    df = generate_sample_outliers(1000)
    filepath = output_dir / 'sample_outliers.csv'
    df.to_csv(filepath, index=False)
    results.append(('sample_outliers.csv', len(df), get_file_size(filepath)))

    # 4. Duplicates dataset
    print("Generating sample_duplicates.csv...")
    df = generate_sample_duplicates(1000, 50)
    filepath = output_dir / 'sample_duplicates.csv'
    df.to_csv(filepath, index=False)
    results.append(('sample_duplicates.csv', len(df), get_file_size(filepath)))

    # 5. Text dataset
    print("Generating sample_text.csv...")
    df = generate_sample_text(500)
    filepath = output_dir / 'sample_text.csv'
    df.to_csv(filepath, index=False)
    results.append(('sample_text.csv', len(df), get_file_size(filepath)))

    # 6. Mixed types dataset
    print("Generating sample_mixed_types.csv...")
    df = generate_sample_mixed_types(1000)
    filepath = output_dir / 'sample_mixed_types.csv'
    df.to_csv(filepath, index=False)
    results.append(('sample_mixed_types.csv', len(df), get_file_size(filepath)))

    # 7. Latin-1 encoded dataset
    print("Generating sample_latin1.csv...")
    df = generate_sample_latin1(500)
    filepath = output_dir / 'sample_latin1.csv'
    df.to_csv(filepath, index=False, encoding='latin-1')
    results.append(('sample_latin1.csv', len(df), get_file_size(filepath)))

    # 8. JSONL dataset
    print("Generating sample_jsonl.jsonl...")
    data = generate_sample_jsonl(200)
    filepath = output_dir / 'sample_jsonl.jsonl'
    with open(filepath, 'w') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')
    results.append(('sample_jsonl.jsonl', len(data), get_file_size(filepath)))

    # 9. Large dataset
    print("Generating sample_large.csv (this may take a moment)...")
    df = generate_sample_large(100000)
    filepath = output_dir / 'sample_large.csv'
    df.to_csv(filepath, index=False)
    results.append(('sample_large.csv', len(df), get_file_size(filepath)))

    print("=" * 80)
    print("\nGeneration complete! Summary:\n")
    print(f"{'Filename':<30} {'Rows':>10} {'Size':>12}")
    print("-" * 80)
    for filename, rows, size in results:
        print(f"{filename:<30} {rows:>10} {size:>12}")

    print(f"\nAll files generated in: {output_dir.absolute()}")


if __name__ == '__main__':
    main()
