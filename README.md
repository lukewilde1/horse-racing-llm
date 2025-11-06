# Horse Racing Results Scraper & ML Dataset Builder

This project automates the extraction, cleaning, and structuring of historical horse racing results from [tab.com.au](https://tab.com.au) using custom scraping logic and machine learning-friendly formatting. It was built for predictive modeling and racing analytics using Python and custom APIs.

## Project Structure

```
RACING_POC/
├── dashboard/                              # UI
├── data/                                   # Folder for storing and retrieving data
│   ├── csv_data/                           # CSV data compiled from API race results - see below example
│   ├── json_data/                          # Json data of race links per day - see below example
│   ├── final_combined_racing_data.csv      # All racing data compiled into a CSV (Currently filters for Randwick and Rosehill)
│   └── data_ingest/                        # Data ingest scripts
│       ├── combine.py                      # Combines data into singular CSV
│       ├── extract-data.py                 # Extracts structured data from URLs
│       └── extract-day.py                  # Fetches race result URLs
├── features/
│   ├── encode_stats.py                     # Encodes the Jockey and Trainer stats for DataFile
│   ├── racing_poc.ipynb                    # Encodes the DF and spits out the rand_rose_features_encoded.csv
│   └── rand_rose_features_encoded.csv
├── models/                                 # Training models
│   ├── poc_model.txt                       # Training model result
│   └── training_model.ipynb                # Model that trains and predicts races
├── notebooks/
├── utils/
├── venv/
├── config.yaml
├── README.md
└── requirements.txt

```

### Example data structures

**JSON Data**
```json
{
    "Date": "2025-10-01",
    "Venue": "S",
    "Race Number": 1,
    "Race Type": "R",
    "Track Condition": "GOOD4",
    "Weather": "FINE",
    "API URL": "https://api.beta.tab.com.au/v1/historical-results-service/NSW/racing/2025-10-01/S/R/races/1"
},
```

**CSV Data**
```csv
Date,Track,Race Number,Horse,Barrier,Jockey,Trainer,SP,Finish Position,Race Distance,Class,Track Condition,Weather,Total Runners
2025-10-01,ROSEHILL,1,AMARILLO SKY,15,BRAITH NOCK,Ciaron Maher,41.0,,1400,3YO MDN,GOOD4,FINE,17
```

## Features

- Automated Historical Scraping with retry logic and proxies  
- Date Range Support for fetching only required days
- JSON to CSV Parsing with structured formatting
- Ready for Machine Learning Training
- Handles:
  - Missing or malformed JSON
  - Failed API retries with logging
  - Previous runs resume without duplications

## How It Works

### 1. Collect Race URLs by Date
**`extract-day.py`**  
Fetches race metadata & result API links from each date in a defined range.

```bash
python extract-day.py
```

Outputs JSON files in `racing-apis/YYYY-MM/`.

### 2. Scrape and Clean Data
**`extract-data.py`**  
Loads the race result URLs from step 1, scrapes relevant race fields (horse, jockey, barrier, trainer, odds, finish), and saves daily structured CSVs.

```bash
python extract-data.py
```

Output: Cleaned daily CSVs in `racing-data/YYYY-MM/`.

### 3. Combine All Monthly Files
**`combine.py`**  
Scans the `racing-data` directory and merges all daily CSVs into a single file.

```bash
python combine.py
```

Final dataset: `final_combined_racing_data.csv`.

## Example Data Columns

- `Date`
- `Track`
- `Race Number`
- `Horse`
- `Jockey`
- `Trainer`
- `Barrier`
- `SP` (Starting Price / Odds)
- `Finish Position`
- `Race Distance`
- `Class`
- `Track Condition`
- `Weather`
- `Total Runners`
