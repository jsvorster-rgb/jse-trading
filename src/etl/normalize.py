"""
Normalization pipeline for Sharenet EOD CSV files.
"""
import os
import glob
import pandas as pd

def load_raw_csvs(raw_dir='data/raw/sharenet'):
    """Load all raw CSVs from the raw directory into a single DataFrame."""
    pattern = os.path.join(raw_dir, '*.csv')
    files = sorted(glob.glob(pattern))
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            df['source_file'] = os.path.basename(f)
            dfs.append(df)
        except Exception as e:
            print(f"Failed to read {f}: {e}")
    if not dfs:
        raise RuntimeError(f"No CSV files loaded from {raw_dir}")
    return pd.concat(dfs, ignore_index=True)

def normalize_prices(df):
    """Standardize column names and types for price data."""
    # Example mapping (adjust based on actual CSV headers)
    mapping = {
        'Date': 'date',
        'Code': 'ticker',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }
    df = df.rename(columns=mapping)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df[list(mapping.values()) + ['source_file']]

def save_normalized(df, out_path='data/processed/prices.csv'):
    """Save the normalized DataFrame to CSV."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Normalized data written to {out_path}")

def main():
    print("Loading raw CSVs...")
    raw_df = load_raw_csvs()
    print(f"Loaded {len(raw_df)} rows from raw data.")
    norm_df = normalize_prices(raw_df)
    print(f"Normalized DataFrame contains {len(norm_df)} rows.")
    save_normalized(norm_df)

if __name__ == '__main__':
    main()
