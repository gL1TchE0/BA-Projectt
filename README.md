# CinePredict: TMDB Movie Performance Analytics

An end-to-end business analytics project that investigates which movie characteristics are associated with stronger audience ratings. The project combines TMDB data collection, data preparation, exploratory analysis, predictive modelling, time-series analysis, text mining, and an interactive Streamlit dashboard.

## Project overview

The analysis focuses on three questions:

1. Which genres, languages, release periods, and engagement signals are associated with higher-rated movies?
2. Can movie characteristics be used to identify likely high-rated titles?
3. What can time-series and plot-summary analysis reveal about movie performance and audience preferences?

The project defines a movie as **high-rated** when its `vote_average` is at least **6.5**. Predictive modelling uses movies with at least **20 votes**, reducing the effect of unstable ratings based on very small audiences.

> **Important:** The results describe associations in a sampled TMDB catalogue. They should not be interpreted as proof of causation or as guaranteed predictions.

## Key results

The final Random Forest models were evaluated on a stratified held-out test set:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Majority-class baseline | 0.610 | 0.000 | 0.000 | 0.000 | 0.500 |
| Random Forest: content only | 0.736 | 0.720 | 0.527 | 0.608 | 0.785 |
| Random Forest: content + engagement | 0.758 | 0.747 | 0.575 | 0.650 | 0.836 |

Additional findings:

- Documentary, Animation, Music, and History have the strongest average ratings in the analysed sample.
- Horror, Thriller, and Science Fiction have lower average ratings than the leading genres.
- Popularity is a measure of reach and recent activity, not a direct measure of quality. Its relationship with rating is weak.
- Vote count, genre, language, and release year are among the most useful predictive features.
- The 50-vote robustness check produces an ROC-AUC of 0.841.
- Plot-summary text mining identifies recurring themes and terms associated with different rating groups, but text features did not improve the main predictive model.

## Interactive dashboard

The dashboard is implemented in [`dashboard/app.py`](dashboard/app.py) and reads the generated CSV files from the `data/` directory.

### Dashboard sections

- **Overview:** headline metrics, ratings by year, genre volume, and rating distribution.
- **EDA:** genre, language, decade, rating, popularity, and correlation analysis.
- **Time series:** monthly rating and popularity trends, rolling averages, forecasts, model comparison, seasonality, and changes in genre share.
- **Text mining:** topic summaries, significant terms, topic trends, genre-topic relationships, sentiment analysis, and a searchable movie explorer.
- **Model results:** test-set metrics, confusion matrix, cross-validation results, feature importance, and robustness notes.
- **Insights:** plain-language business recommendations, colour-coded insight cards, and live summary metrics that respond to the sidebar filters.

### Dashboard interface features

- Light and dark appearance modes
- Responsive wide layout
- Sidebar filters for release year, genre, language, and minimum vote count
- Interactive Plotly visualisations
- Expandable sections for secondary charts
- Downloadable filtered movie data
- Clear explanations of analytical limitations and interpretation

## Dataset

The dataset was collected from the [TMDB API](https://developer.themoviedb.org/) using movie discovery and genre endpoints.

| Dataset | Approximate size | Purpose |
|---|---:|---|
| Raw movie data | 15,555 rows | Collected TMDB records before cleaning |
| Clean movie data | 15,386 rows | Analysis-ready catalogue |
| Modelling data | 10,078 rows | Clean movies with at least 20 votes |
| Release period | 2000–2025 | Analysis window |
| Languages | 89 | Original-language coverage |
| Genres | 19 | Genre coverage |

### Sampling approach

Approximately 30 pages were selected at random for each release year from TMDB discovery results. The collection excluded adult content and used a minimum vote-count threshold during discovery. This produced a mixture of popular and less widely known titles rather than a catalogue containing only major hits.

### Main fields

The cleaned dataset includes:

- `id`
- `title`
- `release_date`
- `release_year`
- `genres`
- `original_language`
- `overview`
- `popularity`
- `vote_average`
- `vote_count`
- `low_votes`

See [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) for field definitions and data-quality notes.

## Analytical workflow

### 1. Data collection and cleaning

- Retrieve movie records from TMDB with retry and checkpoint support.
- Remove duplicate, invalid, incomplete, and genre-less records.
- Parse release dates and map genre IDs to genre names.
- Create derived fields such as release year, vote thresholds, and high-rating labels.

### 2. Exploratory data analysis

- Compare average ratings, popularity, and movie counts by genre and language.
- Analyse rating distributions and decade-level patterns.
- Measure Spearman correlations between rating, popularity, and vote count.
- Review outliers and data-quality constraints.

### 3. Feature engineering

- **Set A:** release year, release month, overview length, genre indicators, and language indicators.
- **Set B:** Set A plus log-transformed popularity and vote count.
- **Text features:** TF-IDF representations of plot overviews for separate text experiments.

### 4. Predictive modelling

- Establish a majority-class baseline.
- Train Logistic Regression, Random Forest, and XGBoost models.
- Use an 80/20 stratified train-test split.
- Tune tree-based models with five-fold cross-validation on the training data.
- Evaluate accuracy, precision, recall, F1, ROC-AUC, confusion matrix, permutation importance, and robustness at a 50-vote threshold.

### 5. Time-series analysis

- Aggregate movie performance into monthly and yearly series.
- Compare naive and Holt-style forecasting approaches.
- Measure MAE and RMSE on held-out months.
- Analyse seasonality and changes in genre share over time.

### 6. Text mining

- Analyse plot-summary terms associated with high- and low-rated movies.
- Build topic models from movie overviews.
- Compare topic prevalence by year and genre.
- Calculate sentiment polarity and subjectivity.
- Use text mining for interpretation rather than as the primary prediction model.

## Repository structure

```text
BA-Project/
├── dashboard/
│   └── app.py                         # Streamlit dashboard
├── data/
│   ├── raw/
│   │   ├── tmdb_raw.csv              # Raw collected movie records
│   │   └── checkpoint.json            # Collection checkpoint
│   ├── processed/
│   │   ├── tmdb_clean.csv             # Clean analysis dataset
│   │   ├── tmdb_model.csv             # Modelling dataset
│   │   └── *.png                      # Analysis figures
│   ├── text/
│   │   ├── text_movie_level.csv       # Movie-level text features
│   │   ├── topics_summary.csv         # Topic descriptions
│   │   ├── terms_association.csv      # Term-rating associations
│   │   └── *.csv                      # Text-mining outputs
│   └── ts/
│       ├── monthly_series.csv         # Monthly performance series
│       ├── forecast.csv                # Forecast values and intervals
│       └── *.csv                      # Time-series outputs
├── models/
│   ├── RandForest_A.pkl               # Content-only Random Forest
│   ├── RandForest_B.pkl               # Content + engagement Random Forest
│   ├── XGBoost_A.pkl                  # Content-only XGBoost
│   └── XGBoost_B.pkl                  # Content + engagement XGBoost
├── notebooks/
│   ├── EDA.ipynb
│   ├── Feature_Engineering.ipynb
│   └── Text_Mining.ipynb
├── notebook.ipynb                     # Main analysis notebook
├── Text_Mining_Revised.ipynb          # Revised text-mining workflow
├── TimeSeries.ipynb                   # Time-series workflow
├── DATA_DICTIONARY.md
├── Data Documentation Report.docx
└── README.md
```

## Installation

### Requirements

- Python 3.10 or later
- Jupyter Notebook
- A TMDB API key if collecting fresh data

Install the core packages used by the notebooks and dashboard:

```bash
pip install pandas numpy requests python-dotenv matplotlib seaborn \
    scikit-learn xgboost scipy joblib tabulate statsmodels jupyter \
    streamlit plotly textblob
```

If the repository contains a dependency manifest in your local branch, install from it instead:

```bash
pip install -r requirements.txt
```

## Running the project

### 1. Start the dashboard

From the project directory:

```bash
streamlit run dashboard/app.py
```

The dashboard uses the existing generated data files and does not require a TMDB API key for viewing the analysis.

### 2. Run the notebooks

Start Jupyter:

```bash
jupyter notebook
```

Run the notebooks in the following order when rebuilding the analysis:

1. `notebooks/EDA.ipynb`
2. `notebooks/Feature_Engineering.ipynb`
3. `notebook.ipynb`
4. `TimeSeries.ipynb`
5. `Text_Mining_Revised.ipynb`

Notebook names and execution order may vary depending on the current analysis branch. The dashboard expects its source CSV outputs to be present under `data/processed`, `data/ts`, and `data/text`.

### 3. Collect fresh TMDB data

Create a `.env` file in the project directory:

```text
TMDB_API_KEY=your_api_key_here
```

The collection workflow uses the API key to retrieve data and writes the raw output to `data/raw/`. Existing checkpoints allow an interrupted collection process to resume.

## Loading the cleaned data in Python

The `genres` column is stored as text in CSV files. Convert it back to Python lists after loading:

```python
import ast
import pandas as pd

df = pd.read_csv(
    "data/processed/tmdb_clean.csv",
    parse_dates=["release_date"],
)
df["genres"] = df["genres"].apply(
    lambda value: ast.literal_eval(value) if isinstance(value, str) else value
)
```

## Interpretation and limitations

- The dataset is a sample of TMDB discovery results, not a complete census of all movie releases.
- Movie counts by year reflect the sampling design and should not be interpreted as the number of movies released.
- TMDB popularity is a recent-activity score and may favour newer or currently visible titles.
- Ratings based on very few votes are noisy, which is why modelling uses a 20-vote minimum.
- Popularity and vote count are correlated, so their feature importance is partly shared.
- Set B uses post-release engagement information. It explains observed ratings but is not a true pre-release forecasting model.
- Feature importance identifies model reliance, not causal effects.
- Text sentiment describes the tone of a plot summary, not audience sentiment.
- Forecast intervals are approximate and should be used for directional planning rather than precise prediction.
- Topic labels are analytical summaries and may simplify complex movie narratives.

## Team and academic context

This project was completed for **23CSE452 Business Analytics**. It covers data collection, cleaning, exploratory analysis, predictive modelling, time-series analysis, text mining, and dashboard communication.

### Team members

| Name | Student ID |
|---|---|
| Soundarya Satalgoan | CB.SC.U4CSE23447 |
| Balaji N | CB.SC.U4CSE23011 |
| Parvathy Krishna A | CB.SC.U4CSE23739 |
| Venkata Kanna Bhavan Surya Addap | CB.SC.U4CSE23467 |
| Dareddy Tejeswara Reddy | CB.SC.U4CSE23614 |

## Acknowledgements

- Movie metadata and audience metrics: [The Movie Database (TMDB)](https://www.themoviedb.org/)
- Visual analytics: Plotly and Streamlit
- Statistical and machine-learning analysis: pandas, NumPy, scikit-learn, XGBoost, SciPy, and statsmodels
