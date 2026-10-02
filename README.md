# Movie Performance Analysis and Prediction Using TMDB Data

Analysing which movie characteristics (genre, language, release period, audience engagement) are associated with higher-rated films, using a dataset we collected ourselves from the TMDB API, and predicting whether a movie will be **high-rated**.

> **Status:** Review 1 complete (data collection, cleaning, EDA, feature engineering, predictive modelling).
> Review 2 will add time-series analysis, text mining and an interactive dashboard.

---

## Table of Contents
- [Problem Statement](#problem-statement)
- [Dataset](#dataset)
- [Methodology](#methodology)
- [Results](#results)
- [Key Findings](#key-findings)
- [Repository Structure](#repository-structure)
- [Setup and Usage](#setup-and-usage)
- [Limitations](#limitations)
- [Roadmap (Review 2)](#roadmap-review-2)
- [Team](#team)
- [Acknowledgements](#acknowledgements)

---

## Problem Statement

Movie performance varies across genres, release periods, languages and audience ratings, which makes it hard to see which factors go with successful movies. We study these patterns to understand audience preferences and the characteristics of higher-performing movies.

- **Performance** is measured by audience rating (`vote_average`) and engagement (`popularity`, `vote_count`).
- **Prediction target:** a movie is **high-rated** if `vote_average >= 6.5`. Only movies with at least **20 votes** are used for modelling, because ratings from very few voters are unreliable.

## Dataset

Collected by us from the [TMDB API](https://developer.themoviedb.org/) (`/discover/movie` and `/genre/movie/list`). Only the fields needed for the analysis were kept.

| Item | Value |
|------|-------|
| Raw movies collected | 15,555 |
| Clean movies | 15,386 |
| Used for modelling (20+ votes) | 10,078 |
| Release years | 2000 to 2025 (about 600 movies per year) |
| Languages / genres | 89 / 19 |

**Sampling strategy (to avoid a popular-only dataset):** for each year, 30 pages were picked at random from the available pages (sorted by popularity, `vote_count >= 10`, adult content excluded). Random pages give a natural mix of well-known and obscure movies. Median popularity is 1.88 and median vote count is 30.

**Fields kept:** `id`, `title`, `release_date`, `genres`, `original_language`, `overview`, `popularity`, `vote_average`, `vote_count` (plus derived `release_year` and `low_votes`).
Dropped: poster/backdrop paths, `adult`, `video`, `softcore`, `original_title`.

See [`data/DATA_DICTIONARY.md`](data/DATA_DICTIONARY.md) for column details.

## Methodology

1. **Collection:** reusable API session with retries and back-off, and a per-year checkpoint so interrupted runs resume.
2. **Cleaning:** removed duplicates, invalid dates, empty overviews (105), invalid values and movies without genres (169 rows removed in total); mapped genre IDs to names.
3. **Quality checks:** no missing values or duplicates left; outliers (popularity 913, vote count 653) are real hits and were kept.
4. **EDA:** distributions, genre and language comparisons, Spearman correlations, rating by decade.
5. **Features:**
   - **Set A (content only, 34 features):** release year and month, overview word count, number of genres, 19 genre flags, 11 language flags.
   - **Set B (36 features):** set A plus log popularity and log vote count (audience engagement, known only after release).
   - **Text:** TF-IDF on overviews (1,000 features, fitted on training data only).
6. **Models:** majority-class baseline, Logistic Regression, Random Forest, XGBoost; stratified 80/20 split (8,062 train / 2,016 test); Random Forest and XGBoost tuned with 5-fold cross-validation on the training set only.
7. **Evaluation:** accuracy, precision, recall, F1, ROC-AUC, confusion matrix, permutation feature importance, and a robustness check with a 50-vote threshold.

## Results

Test-set results for the final Random Forest models (baseline accuracy is 0.610):

| Model | Accuracy | Precision (high) | Recall (high) | F1 (high) | AUC |
|-------|---------:|-----------------:|--------------:|----------:|----:|
| Baseline (majority class) | 0.610 | 0.000 | 0.000 | 0.000 | 0.500 |
| Random Forest, set A (content only) | 0.736 | 0.720 | 0.527 | 0.608 | 0.785 |
| Random Forest, set B (with engagement) | 0.758 | 0.747 | 0.575 | 0.650 | 0.836 |

- Cross-validated AUC (tuned): set B 0.819 and set A 0.761 for Random Forest; test scores are close, so the models are not overfitting.
- Robustness: at 50+ votes (5,717 movies) the AUC is 0.841.
- TF-IDF text features did not improve prediction, so text is used for interpretation (Review 2).

## Key Findings

- **Highest-rated genres:** Documentary (6.89), Animation (6.82), Music (6.65), History (6.62). **Lowest:** Horror (5.36), Thriller (5.81), Science Fiction (5.82).
- **Popularity is not quality:** Adventure is the most popular genre but only mid-table on rating; Documentary is top-rated but least popular. English movies are the most popular (4.24) but second-lowest on rating (5.99).
- **Linear correlations with rating are weak** (0.11 to 0.24), so genre and other categorical signals matter more.
- **Most important features:** genre (Documentary, Horror, Animation), vote count, language and release year.
- Ratings are flat until about 2016 and then rise (2000s 6.06, 2010s 6.06, 2020s 6.33). This is an association only.

## Repository Structure

```
.
├── data/
│   ├── raw/
│   │   └── tmdb_raw.csv            # 15,555 collected movies
│   ├── processed/
│   │   ├── tmdb_clean.csv          # 15,386 cleaned movies
│   │   └── tmdb_model.csv          # 10,078 movies used for modelling
│   └── DATA_DICTIONARY.md
├── notebooks/
│   └── Review1_TMDB.ipynb          # full Review 1 analysis
├── models/                         # tuned Random Forest / XGBoost models
├── presentations/                  # Review 1 slides
├── reports/                        # Review 1 report
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup and Usage

**Requirements:** Python 3.10+ and a free [TMDB API key](https://www.themoviedb.org/settings/api).

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. Create a virtual environment (Windows: .venv\Scripts\activate)
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env        # then edit .env
```

`.env` format:

```
TMDB_API_KEY=your_key_here
```

**Run the analysis:**

```bash
jupyter notebook notebooks/Review1_TMDB.ipynb
```

Run the cells from top to bottom. To skip the collection step (about 15 minutes), load the saved `data/raw/tmdb_raw.csv` instead of calling the API.

**Note on loading the CSVs:** the `genres` column is saved as text, so convert it after reading:

```python
import pandas as pd, ast
df = pd.read_csv("data/processed/tmdb_clean.csv", parse_dates=["release_date"])
df["genres"] = df["genres"].apply(ast.literal_eval)
```

`requirements.txt`:

```
requests
pandas
numpy
python-dotenv
matplotlib
seaborn
scikit-learn
xgboost
scipy
joblib
tabulate
statsmodels
jupyter
```

## Limitations

- Feature importance shows what the model uses, not the direction or cause of an effect.
- Popularity and vote count are correlated (0.65 to 0.68), so their importance is shared.
- Set B uses post-release audience data, so it explains ratings but cannot forecast a new release. Set A is the pre-release version.
- The data is a sample of about 600 movies per year, so movies per year reflect our sampling, not TMDB. Movies with fewer than 20 votes are excluded from modelling.
- TMDB popularity is a recent-activity score, which favours newer films.

## Roadmap (Review 2)

- [ ] Time-series analysis of ratings and popularity (trend, seasonality, forecast)
- [ ] Text mining of overviews (frequent terms, topics, link to performance)
- [ ] Interactive dashboard with filters for year, genre and language

## Team

Course: 23CSE452 Business Analytics (Data Analysis and Predictive Modelling)

| Name | Register number | Contribution (Review 1 issues) |
|------|-----------------|--------------------------------|
| Soundarya Satalgoan | CB.SC.U4CSE23447 | Issues 1 to 4: problem statement, dataset plan, documentation, TMDB API setup |
| Balaji N | CB.SC.U4CSE23011 | Issues 5 to 7: data collection, cleaning, data quality check |
| Parvathy Krishna A | CB.SC.U4CSE23739 | Issues 8 to 10: numerical, genre/language and relationship EDA |
| Venkata Kanna Bhavan Surya Addap | CB.SC.U4CSE23467 | Issues 11 to 13: structured and text features, target definition, baseline |
| Dareddy Tejeswara Reddy | CB.SC.U4CSE23614 | Issues 14 to 17: model training, tuning, evaluation, interpretation |

Task planning and progress: https://github.com/users/soundarya-satal/projects/4

## Acknowledgements

This product uses the TMDB API but is not endorsed or certified by TMDB. Data is used for academic purposes only.
