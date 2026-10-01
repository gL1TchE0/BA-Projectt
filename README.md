# Movie Performance Analysis

## Problem Statement

Movie performance varies across genres, release periods, audience ratings, languages, and other movie characteristics. These differences make it difficult to identify the factors associated with successful movie performance. This project analyses patterns in TMDB movie data to understand audience preferences and the characteristics associated with higher-performing movies.

## Project Objectives

- Compare movie ratings and popularity across genres, languages, and release periods.
- Assess the effect of audience engagement, measured through vote count and popularity.
- Identify characteristics associated with highly rated movies.
- Build and evaluate classification models for predicting whether a movie is high-rated.
- Examine whether the findings remain stable when the minimum vote threshold is increased.

## Dataset

The project uses movie metadata collected from the [TMDB API](https://developer.themoviedb.org/reference/intro/getting-started).

| Dataset | Description |
| --- | --- |
| `data/raw/tmdb_raw.csv` | Raw movie records collected for release years 2000–2025. |
| `data/processed/tmdb_clean.csv` | Clean analysis dataset containing 15,386 movies. |
| `data/processed/tmdb_model.csv` | Modeling dataset containing movies with at least 20 votes and derived features. |

The cleaned dataset contains movie titles, release dates, original languages, plot overviews, TMDB popularity, average ratings, vote counts, genres, release years, and a low-vote indicator. It covers 19 genres and 89 languages. A full field-level description is available in [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

### Data preparation

- Removed duplicate movie IDs.
- Removed records with missing dates or genres, empty overviews, or invalid rating, vote-count, or popularity values.
- Converted release dates to datetime values and derived `release_year`.
- Mapped TMDB genre IDs to genre names.
- Flagged movies with fewer than 20 votes as `low_votes`, because their average ratings are more likely to be noisy.
- Applied `log1p` transformations to popularity and vote count for modeling and correlation analysis.

The cleaning process removed 169 records. The final cleaned dataset contains no missing values or duplicate IDs.

## Analysis Approach

The analysis is implemented in [`notebook.ipynb`](notebook.ipynb) and includes:

1. Data collection from TMDB with retry logic and a checkpoint file so collection can resume after interruption.
2. Data quality checks, cleaning, and feature creation.
3. Exploratory analysis using distributions, box plots, genre and language comparisons, correlation matrices, and release-period analysis.
4. Text exploration of movie overviews using TF-IDF features.
5. Classification of high-rated movies, defined as `vote_average >= 6.5`, among movies with at least 20 votes.
6. Model comparison using a dummy baseline, logistic regression, random forest, and XGBoost.
7. Five-fold cross-validation, grid-search tuning, permutation feature importance, and a robustness check using a 50-vote threshold.

### Feature sets

- **Set A: content and metadata** — release year, release month, overview length, number of genres, genre indicators, and language indicators.
- **Set B: content and engagement** — Set A plus `log_pop` and `log_votes`.
- **Text features** — up to 1,000 TF-IDF unigram and bigram features from movie overviews, fitted on the training split only.

## Key Findings

- Drama, Comedy, and Thriller are the most common genres in the dataset.
- Documentary has the highest average rating among movies with at least 20 votes, while Horror has the lowest.
- Animation shows a strong combination of rating and popularity. Documentary has high ratings but relatively low popularity, demonstrating that audience reach and perceived quality are not identical.
- English-language movies dominate the dataset and have the highest average popularity, while several non-English language groups have higher average ratings. These comparisons should be interpreted cautiously because movies receiving enough international attention to reach the vote threshold may be a self-selected group.
- Vote count is positively associated with rating, but the relationship is moderate. Popularity and rating measure different aspects of performance.
- Adding popularity and vote count improves predictive performance over content and metadata alone.
- Text features contributed limited additional predictive value and were mainly useful for interpretation.

## Model Results

The reported results use a stratified 80/20 train-test split with `random_state=42`. The test set contains 2,016 movies.

| Feature set | Accuracy | Precision | Recall | F1 | AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Set B: with popularity and votes | 0.758 | 0.747 | 0.575 | 0.650 | 0.836 |
| Set A: content and metadata only | 0.736 | 0.720 | 0.527 | 0.608 | 0.785 |
| Dummy baseline | 0.610 | 0.000 | 0.000 | 0.000 | 0.500 |

For the tuned random forest using Set B, the most important features by permutation importance were `log_votes`, Documentary and Horror genre indicators, English-language status, Animation, and release year. Using a stricter minimum of 50 votes produced an AUC of 0.841 across 5,717 movies, suggesting that the overall pattern is reasonably robust.

## Limitations

- TMDB popularity and vote count are post-release measures. Set B explains observed ratings but is not suitable for a pre-release forecasting use case; Set A is the more appropriate pre-release feature set.
- The dataset samples roughly 600 movies per release year rather than representing every movie equally.
- Movies with fewer than 20 votes are excluded from modeling because their ratings are less reliable.
- Genre and language groups are imbalanced, so averages for rare groups should be interpreted cautiously.
- Model feature importance indicates predictive usefulness, not causation or the direction of an effect.
- `log_votes` and `log_pop` are correlated, so their individual importance may be distributed between them.

## Repository Structure

```text
BA-Project/
├── DATA_DICTIONARY.md
├── README.md
├── notebook.ipynb
├── data/
│   ├── raw/
│   │   ├── checkpoint.json
│   │   └── tmdb_raw.csv
│   └── processed/
│       ├── tmdb_clean.csv
│       └── tmdb_model.csv
└── models/
	 ├── RandForest_A.pkl
	 ├── RandForest_B.pkl
	 ├── XGBoost_A.pkl
	 └── XGBoost_B.pkl
```

## Reproducing the Analysis

1. Clone or open this repository and create a Python environment.
2. Install the notebook dependencies:

	```bash
	pip install requests pandas python-dotenv numpy matplotlib seaborn scikit-learn scipy xgboost joblib tabulate
	```

3. Create a `.env` file in the project root containing a TMDB API key:

	```text
	TMDB_API_KEY=your_api_key_here
	```

4. Open [`notebook.ipynb`](notebook.ipynb) and run the cells from top to bottom. The first cells collect and clean data; later cells perform the analysis, train the models, and save model files in `models/`.

The raw-data collection uses `data/raw/checkpoint.json` to resume year-by-year collection if the API request process is interrupted. Existing checkpoint and processed files can be used to inspect the project without recollecting data.

## Outputs

- Clean and modeling datasets in `data/processed/`.
- Trained random forest and XGBoost models in `models/`.
- Visual analysis, evaluation metrics, confusion matrices, ROC curves, and permutation importance plots in the notebook.