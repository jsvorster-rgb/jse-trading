# JSE Trading Project

This repository contains tools and pipelines for sourcing, processing, and analyzing data to develop and backtest trading strategies on the Johannesburg Stock Exchange (JSE).

## Directory Structure

```
├── data/
│   └── raw/
│       └── sharenet/        # Raw CSV downloads or scraped HTML from Sharenet
├── notebooks/               # Jupyter notebooks for exploration and prototyping
├── src/
│   ├── etl/                 # ETL scripts to ingest and normalize raw data
│   └── models/              # Model definitions, backtesting, and optimization code
├── .gitignore               # Files and folders to exclude from version control
└── requirements.txt         # Python dependencies
```

## Autonomous ETL via GitHub Actions

After the daily raw data pull, you can normalize and process the data automatically or on demand.

### Data Normalization Pipeline

We provide a normalization script to combine and standardize raw EOD CSVs:

```bash
# Run normalization (local Docker example)
docker run --rm \
  -v "$(pwd)/data/raw/sharenet:/app/data/raw/sharenet" \
  -v "$(pwd)/data/processed:/app/data/processed" \
  jse-trading \
  python3 src/etl/normalize.py
```

This will produce `data/processed/prices.csv` with standardized columns (`date`, `ticker`, `open`, `high`, `low`, `close`, `volume`).

## Getting Started

To run the ETL pipeline automatically each trading day without manual intervention, we’ve configured a GitHub Actions workflow (`.github/workflows/etl.yml`) that:

1. Triggers **daily at 18:00 SAST (16:00 UTC)**
2. Checks out the repo
3. Builds the `jse-trading` Docker image
4. Runs the ETL container (sharenet scraper)
5. Commits any new raw data into `data/raw/sharenet`

After pushing this repo, the pipeline will keep `data/raw/sharenet` up to date in your main branch.

## Getting Started

### Configuration

| Env Variable      | Description                               | Example                  |
|-------------------|-------------------------------------------|--------------------------|
| `SHARENET_USER`   | Sharenet login username (optional)        | `user@example.com`       |
| `SHARENET_PASS`   | Sharenet login password (optional)        | `s3cr3t`                 |

### CLI Usage

Run the Sharenet scraper directly (for testing or custom dates):

```bash
# Fetch all available CSVs
docker run --rm \
  -v "$(pwd)/data/raw/sharenet:/app/data/raw/sharenet" \
  -e SHARENET_USER -e SHARENET_PASS \
  jse-trading

# Fetch only a specific date (e.g., 2026-02-02)
docker run --rm \
  -v "$(pwd)/data/raw/sharenet:/app/data/raw/sharenet" \
  -e SHARENET_USER -e SHARENET_PASS \
  jse-trading \
  --date 2026-02-02
```

### Using Docker

Instead of installing dependencies locally, you can build and run this project in Docker:

```bash
# Build the Docker image
docker build -t jse-trading .

# Run the ETL pipeline (e.g., Sharenet scraper)
docker run --rm \
  -v "$(pwd)/data/raw:/app/data/raw" \
  jse-trading
```

You can override the default command to run notebooks, backtests, etc.:

```bash
docker run --rm -it -v "$(pwd):/app" jse-trading bash
```

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Populate data**:
   Run ETL scripts under `src/etl/` to download and preprocess JSE data.

3. **Explore and prototype**:
   Use notebooks in `notebooks/` to analyze data, build prototypes, and test strategies.

4. **Model development**:
   Implement strategy logic under `src/models/` and integrate with the backtesting framework.

---

*Generated on 2026-02-02*