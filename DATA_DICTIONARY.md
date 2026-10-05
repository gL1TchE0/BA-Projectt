# Dataset Documentation: TMDB Movies (2000 to 2025)

Project: Movie Performance Analysis and Prediction Using TMDB Data
Course: 23CSE452 Business Analytics

## 1. Overview

| Item | Detail |
|------|--------|
| Source | The Movie Database (TMDB) API v3, collected by the team (no pre-built dataset used) |
| Endpoints | `/discover/movie` (movies), `/genre/movie/list` (genre names) |
| Collected on | [add collection date] (TMDB data changes over time, so record this) |
| Coverage | Movies released from 2000-01-01 to 2025-12-31 |
| Raw dataset | 15,555 unique movies, 9 columns |
| Clean dataset | 15,386 movies, 11 columns |
| Modelling dataset | 10,078 movies (20 or more votes), 18 columns |
| Prediction target | `high_rated` = 1 if `vote_average >= 6.5`, else 0 (39% positive) |

## 2. Collection method

- One request series per release year (`primary_release_year` = 2000 to 2025).
- For each year, 30 pages were chosen **at random** (seed 42) from the pages TMDB offers, sorted by `popularity.desc`, with `vote_count.gte=10` and `include_adult=false`. Random pages give a mix of well-known and obscure movies, so the data is not limited to popular films.
- Requests use one HTTP session with automatic retries and back-off. Progress is saved after each year in `data/raw/checkpoint.json`.
- Only the fields needed for the analysis were kept. Dropped fields: `adult`, `backdrop_path`, `poster_path`, `original_title`, `softcore`, `video`.
- The API key is stored in a local `.env` file and is not part of the repository.

## 3. Files

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| `data/raw/tmdb_raw.csv` | 15,555 | 9 | Collected data, only deduplicated by `id` |
| `data/raw/genres.csv` | 19 | 2 | Genre ID to name mapping (if saved) |
| `data/processed/tmdb_clean.csv` | 15,386 | 11 | Cleaned dataset used for EDA |
| `data/processed/tmdb_model.csv` | 10,078 | 18 | Movies with 20 or more votes, with model features and target |

## 4. Data dictionary: `tmdb_clean.csv`

| # | Column | Data type | Field type | Description | Range / values | Missing |
|---|--------|-----------|------------|-------------|----------------|---------|
| 1 | `id` | int64 | Identifier | Unique TMDB movie ID (primary key) | 16 to 1,688,177 | 0 |
| 2 | `title` | object (string) | Text (label) | Movie title | free text | 0 |
| 3 | `release_date` | datetime64 | Date | Release date | 2000-01-01 to 2025-12-31 | 0 |
| 4 | `original_language` | object (string) | Categorical | ISO 639-1 code of the original language | 89 values; `en` 8,229, `fr` 1,138, `es` 806, `ja` 751 | 0 |
| 5 | `overview` | object (string) | Text | Plot summary, used for text features | 5 or more words for all but 4 rows | 0 |
| 6 | `popularity` | float64 | Numerical (continuous) | TMDB popularity score, based on recent activity | 0.01 to 92.51 | 0 |
| 7 | `vote_average` | float64 | Numerical (continuous) | Mean user rating on a 0 to 10 scale | 1.2 to 10.0 | 0 |
| 8 | `vote_count` | int64 | Numerical (discrete) | Number of user votes behind `vote_average` | 10 to 34,747 | 0 |
| 9 | `genres` | object (list of strings) | Categorical (multi-label) | Genre names; a movie has one or more | 19 genres, 1 or more per movie | 0 |
| 10 | `release_year` | int32 | Numerical (derived) | Year taken from `release_date` | 2000 to 2025 | 0 |
| 11 | `low_votes` | bool | Binary flag (derived) | True if `vote_count < 20` (rating is noisy) | True for 5,308 movies (34.5%) | 0 |

Notes:
- In the raw file, genres are stored as `genre_ids` (a list of integer IDs). They were mapped to names using `/genre/movie/list`, and `genre_ids` was then dropped.
- In CSV files, `genres` is stored as text such as `['Drama', 'Action']`. Convert it back after loading:
  ```python
  import ast
  df["genres"] = df["genres"].apply(ast.literal_eval)
  ```

### Field types at a glance

| Type | Columns |
|------|---------|
| Numerical | `popularity`, `vote_average`, `vote_count`, `release_year` |
| Categorical | `original_language`, `genres` (multi-label) |
| Date | `release_date` |
| Text | `overview` (and `title` as a label) |
| Identifier | `id` |
| Flag | `low_votes` |

## 5. Additional columns in `tmdb_model.csv`

These are added for the modelling subset (movies with `vote_count >= 20`).

| Column | Data type | Description |
|--------|-----------|-------------|
| `high_rated` | int | **Target.** 1 if `vote_average >= 6.5`, else 0 (39% are 1) |
| `lang` | object | `original_language` limited to the top 10 languages, others grouped as `other` |
| `month` | int | Release month (1 to 12) |
| `ov_words` | int | Number of words in `overview` |
| `n_genres` | int | Number of genres of the movie |
| `log_pop` | float | `log(1 + popularity)` |
| `log_votes` | float | `log(1 + vote_count)` |

Feature sets used for modelling (built in the notebook, not saved as files):

| Set | Features | Count |
|-----|----------|-------|
| A (content only) | `release_year`, `month`, `ov_words`, `n_genres`, 19 genre flags, 10 language flags + `other` | 34 |
| B | Set A + `log_pop` + `log_votes` | 36 |
| Text | 1,000 TF-IDF terms (unigrams and bigrams) from `overview`, fitted on the training split only | 1,000 |

## 6. Summary statistics (`tmdb_clean.csv`, 15,386 movies)

| Variable | Mean | Std | Min | 25% | Median | 75% | Max | Skew |
|----------|------|-----|-----|-----|--------|-----|-----|------|
| `popularity` | 2.77 | 3.43 | 0.01 | 1.40 | 1.88 | 2.76 | 92.51 | 6.85 |
| `vote_average` | 6.00 | 1.08 | 1.20 | 5.30 | 6.10 | 6.70 | 10.00 | -0.45 |
| `vote_count` | 331.45 | 1,600.58 | 10 | 16 | 30 | 98 | 34,747 | 10.24 |
| `release_year` | 2012.5 | 7.5 | 2000 | 2006 | 2013 | 2019 | 2025 | n/a |

`popularity` and `vote_count` are heavily right-skewed, so log transforms are used in models.

### Genre counts (a movie can have several genres)

| Genre | Movies | Genre | Movies |
|-------|--------|-------|--------|
| Drama | 6,910 | Family | 1,130 |
| Comedy | 4,898 | Adventure | 1,028 |
| Thriller | 2,905 | Animation | 1,021 |
| Romance | 2,450 | Science Fiction | 1,006 |
| Horror | 2,117 | Mystery | 984 |
| Action | 2,033 | Fantasy | 963 |
| Documentary | 1,515 | History | 587 |
| Crime | 1,510 | Music | 518 |
| TV Movie | 1,216 | War | 293 |
|  |  | Western | 99 |

### Distribution over years

575 to 598 movies per release year (about 600 sampled per year), so the years are almost evenly represented.

## 7. Cleaning applied (raw to clean)

| Step | Effect |
|------|--------|
| Remove duplicate `id` | 0 duplicates found |
| Parse `release_date` to a date, drop invalid | no invalid dates |
| Drop blank `overview` | 105 rows removed |
| Drop invalid values (`vote_count` of 0, `popularity` of 0 or below, rating outside 0 to 10) and rows without genre | 64 rows removed |
| Map `genre_ids` to `genres`, add `release_year` and `low_votes` | 2 columns added |
| **Result** | **15,555 to 15,386 rows (169 removed, 1.1%)** |

## 8. Data quality checks

| Check | Result |
|-------|--------|
| Missing values (NaN) in the clean data | 0 |
| Duplicate IDs | 0 |
| Release dates in the future | 0 |
| Overviews with fewer than 5 words | 4 (kept) |
| Outliers by IQR rule on log values | 913 for `popularity` (5.9%), 653 for `vote_count` (4.2%); kept because they are genuine hits |
| Languages | 89; the top 10 cover 84.9% of movies |

## 9. Data sample (first 3 rows of `tmdb_clean.csv`, overview shortened)

| id | title | release_date | original_language | overview | popularity | vote_average | vote_count | genres | release_year | low_votes |
|----|-------|--------------|-------------------|----------|-----------|--------------|-----------|--------|--------------|-----------|
| 159627 | Ground Zero | 2000-05-12 | en | When a series of tremors rocks Los Angeles, se... | 1.6756 | 4.1 | 13 | Drama, Action | 2000 | True |
| 28085 | Blind Target | 2000-01-01 | en | A popular American novelist, who has written h... | 1.7006 | 3.4 | 11 | Thriller, Drama | 2000 | True |
| 60074 | La Squale | 2000-11-29 | fr | Désirée, a black girl, is nicknamed "The Shark... | 1.8364 | 6.1 | 16 | Drama | 2000 | True |

## 10. Known limitations and biases

- **Sampling:** about 600 movies per year were sampled, so movie counts per year reflect our design, not TMDB itself. The dataset is a sample, not every TMDB movie.
- **Minimum votes:** collection used `vote_count >= 10`, so movies with fewer than 10 votes are not included.
- **Noisy ratings:** 34.5% of movies have fewer than 20 votes, so their `vote_average` is unreliable. Modelling uses only movies with 20 or more votes.
- **Popularity:** TMDB popularity reflects recent activity, so it favours newer films and changes over time.
- **Language imbalance:** English is about 53% of movies. Non-English movies that reach 20 votes may be a self-selected, well-received group.
- **Overview text:** the language of `overview` was not filtered or checked, and some entries are very short.
- **Time:** ratings and popularity are a snapshot at collection time and will differ if the data is collected again.

## 11. Reproducibility

1. Create a TMDB API key and store it in `.env` as `TMDB_API_KEY`.
2. Run the collection cells of `notebooks/Review1_TMDB_Final.ipynb` (random seed 42, so the page selection is repeatable; TMDB's own data may have changed since).
3. Run the cleaning cell to create `data/processed/tmdb_clean.csv`.

## 12. Terms of use and attribution

Data comes from TMDB and is used here for academic purposes only. This product uses the TMDB API but is not endorsed or certified by TMDB. The dataset contains no personal data.
