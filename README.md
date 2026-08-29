# FortyGuard Heat vs. Heat-Illness Regression Toolkit

**Track 7 — Data Analysis & Correlation** | FortyGuard Hackathon'26

A regression toolkit that ingests FortyGuard's hyperlocal temperature data and correlates it with real-world, non-weather outcomes — in this case, heat-related emergency department (ED) visits — to quantify how strongly ambient heat drives health outcomes across the United States.

## The Problem

Extreme heat is a growing public health burden in the U.S., but most cities and health departments lack a simple, data-backed way to see how local temperature actually correlates with heat-illness emergency visits in their region. This tool closes that gap: feed it any set of U.S. locations, and it returns a statistically grounded relationship between hyperlocal temperature and heat-illness burden.

**Who this is for:** City health departments, emergency preparedness planners, and public health researchers who need a quick, defensible way to quantify heat-health risk for a set of locations before committing resources to cooling centers, outreach, or worker-safety programs.

## How It Works

1. **`fetch_temperatures.py`** — Reads a CSV of U.S. locations and calls the FortyGuard Temperature API (`POST /v1/heatmap`) for a small area around each coordinate, polling `/v1/status/{activity_id}` until the result is ready, and extracts the mean 2-metre ambient temperature.
2. **`merge_real_data.py`** — Joins the fetched temperature data with real CDC heat-illness ED visit rates (see Data Sources below).
3. **`analyze_regression.py`** — Runs a Pearson correlation and linear regression (via `scipy`) between temperature and the health outcome, and outputs a scatter plot with a fitted trend line.

## Data Sources

| Data | Source | Notes |
|---|---|---|
| **Temperature** | FortyGuard Temperature API (`/v1/heatmap`) | 2-metre ambient air temperature, 15 July 2024, 14:00 local (peak-heat hour), 20 U.S. cities |
| **Heat-illness ED visit rate** | CDC, *"Heat-Related Emergency Department Visits — United States, May–September 2023"*, MMWR 2024;73:324–329 ([source](https://www.cdc.gov/mmwr/volumes/73/wr/mm7315a1.htm)) | Rate per 100,000 all-cause ED visits, published at HHS-region level (10 regions) and matched to each city by its HHS region |

Both datasets are real, published data — no synthetic or mock values are used in the final results.

## Results (20 U.S. cities)

```
Pearson correlation (r):     0.451
p-value:                     0.0461
R-squared:                   0.203
Regression equation:         y = 13.171 * x - 183.553
```

There is a **statistically significant, positive relationship** (p < 0.05) between ambient temperature and heat-illness ED visit rates: hotter cities see measurably higher heat-illness burden. Temperature alone explains ~20% of the variation (R² = 0.203) — expected, since real-world heat-illness rates are also driven by humidity, healthcare access, outdoor-worker density, and air conditioning prevalence, none of which are captured here. This tool is best used as an early, low-cost screening signal rather than a complete predictive model.

See `outputs/scatter_plot.png` for the visualized relationship and `outputs/regression_result.txt` for the raw stats.

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your FortyGuard API key
```bash
cp .env.example .env
```
Open `.env` and paste your FortyGuard API key after `FORTYGUARD_API_KEY=`.

### 3. Fetch temperature data
```bash
python fetch_temperatures.py
```
Calls the FortyGuard API for each location in `data/sample_outcomes.csv` and saves results to `outputs/merged_data.csv`.

### 4. Merge in the real health outcome data
```bash
python merge_real_data.py
```
Joins `data/real_health_outcomes.csv` (CDC data) into `outputs/merged_data.csv`.

### 5. Run the regression analysis
```bash
python analyze_regression.py
```
Prints correlation/p-value/R² to the terminal and saves `outputs/scatter_plot.png` and `outputs/regression_result.txt`.

## Using Your Own Data

Replace `data/real_health_outcomes.csv` with your own outcome CSV in the same format:
```
location_name,latitude,longitude,date,time,<your_outcome_column>
```
Then update `OUTCOME_COLUMN` at the top of `analyze_regression.py` to match your column name. The pipeline works with any outcome that can be tied to a U.S. location and timestamp — energy load, transit ridership, retail foot traffic, crime, etc.

## Project Structure
```
fortyguard_regression/
├── data/
│   ├── sample_outcomes.csv          # demo dataset (synthetic energy values)
│   └── real_health_outcomes.csv     # real CDC heat-illness ED visit rates
├── fetch_temperatures.py            # Step 1: pull temperature from FortyGuard API
├── merge_real_data.py               # Step 2: merge in real health outcome data
├── analyze_regression.py            # Step 3: correlation + regression + chart
├── outputs/                         # merged data, chart, and stats land here
├── .env.example                     # API key template
└── requirements.txt
```

## Constraints (per FortyGuard API)
- Coverage is **U.S. locations only**
- Valid date range: **2021-01-01 to present** (plus up to 12 hours ahead for forecasts)
- Failed API tasks do not consume credits and are automatically skipped by the pipeline

## AI Tools Used
This project's code, data-source research, and documentation were built with assistance from Claude (Anthropic).
