# Data Dictionary: tmdb_clean.csv

## Dataset Overview

The `tmdb_clean.csv` dataset contains **15,386 cleaned movie records** covering movies released between **2000 and 2025**.

The dataset was collected from the **TMDB (The Movie Database) API** and cleaned to remove incomplete or invalid records. The final dataset is used for exploratory data analysis, feature engineering, text mining, and predictive modelling.

- **Final records:** 15,386
- **Original records:** 15,555
- **Records removed during cleaning:** 169
- **Time period:** 2000–2025
- **Unique languages:** 89
- **Genres:** 19
- **Duplicate IDs:** None
- **Missing values:** None
- **Low-vote records:** 34.5% (`vote_count < 20`)

---

## Data Dictionary

| Column | Type | Description | Range / Notes |
|---|---|---|---|
| `id` | int | TMDB movie ID and unique record identifier | No duplicates |
| `title` | text | Movie title | Used for movie identification |
| `release_date` | datetime | Original release date of the movie | 2000-01-01 to 2025-12-31 |
| `original_language` | categorical | Original language of the movie represented using an ISO 639-1 language code | 89 languages; top 10 account for 84.9% |
| `overview` | text | Plot summary of the movie | No empty values; used for text mining |
| `popularity` | float | TMDB popularity score | 0.01–92.5; right-skewed |
| `vote_average` | float | Mean user rating for the movie | 1.2–10.0; median 6.1 |
| `vote_count` | int | Number of user votes received by the movie | 10–34,747; median 30 |
| `genres` | list | Movie genre names mapped from TMDB genre IDs | 19 genres; multi-label |
| `release_year` | int | Year derived from `release_date` | 2000–2025 |
| `low_votes` | bool | Derived indicator identifying movies with fewer than 20 votes | `True` when `vote_count < 20`; 34.5% are `True` |

---

## Detailed Column Descriptions

### 1. `id`

- **Type:** Integer
- **Role:** Unique identifier
- **Description:** Unique TMDB identifier assigned to each movie.
- **Purpose:** Used to uniquely identify movie records and check for duplicate entries.
- **Data quality:** No duplicate IDs are present in the cleaned dataset.

### 2. `title`

- **Type:** Text
- **Role:** Movie identifier / descriptive field
- **Description:** Name or title of the movie.
- **Purpose:** Used to identify movies and present results in reports and visualizations.

### 3. `release_date`

- **Type:** Datetime
- **Role:** Temporal variable
- **Description:** Original release date of the movie.
- **Range:** 2000-01-01 to 2025-12-31.
- **Purpose:** Used for temporal analysis and for deriving the `release_year` variable.

### 4. `original_language`

- **Type:** Categorical
- **Role:** Categorical feature
- **Description:** Original language of the movie represented using an ISO 639-1 language code.
- **Unique categories:** 89 languages.
- **Distribution:** The top 10 languages account for 84.9% of all records.
- **Purpose:** Used for language-based exploratory analysis and categorical feature analysis.

### 5. `overview`

- **Type:** Text
- **Role:** Text feature
- **Description:** Plot summary or description of the movie obtained from TMDB.
- **Data quality:** No empty values remain after cleaning.
- **Purpose:** Used for text mining and can be used for techniques such as keyword analysis and text feature extraction.

### 6. `popularity`

- **Type:** Float
- **Role:** Numerical feature
- **Description:** TMDB popularity score associated with the movie.
- **Range:** 0.01–92.5.
- **Distribution:** Right-skewed.
- **Purpose:** Used to analyze movie popularity and its relationship with other variables such as ratings and vote count.

### 7. `vote_average`

- **Type:** Float
- **Role:** Numerical performance variable
- **Description:** Mean user rating assigned to the movie on TMDB.
- **Range:** 1.2–10.0.
- **Median:** 6.1.
- **Purpose:** Used as a primary movie-performance measure and for defining the high-rated movie target during predictive modelling.

### 8. `vote_count`

- **Type:** Integer
- **Role:** Numerical feature
- **Description:** Total number of user votes contributing to the movie's rating.
- **Range:** 10–34,747.
- **Median:** 30.
- **Purpose:** Used to measure the amount of voting evidence supporting a movie's rating and to identify movies with potentially noisy ratings.

### 9. `genres`

- **Type:** List
- **Role:** Multi-label categorical feature
- **Description:** Genre names associated with each movie. The original TMDB genre IDs were mapped to readable genre names.
- **Number of genres:** 19.
- **Structure:** Multi-label; a movie can belong to more than one genre.
- **Purpose:** Used for genre-based exploratory analysis and can be transformed into model-ready categorical features.

### 10. `release_year`

- **Type:** Integer
- **Role:** Derived temporal feature
- **Description:** Calendar year extracted from `release_date`.
- **Range:** 2000–2025.
- **Purpose:** Used for year-wise analysis, temporal trends, and feature engineering.

### 11. `low_votes`

- **Type:** Boolean
- **Role:** Derived data-quality indicator
- **Definition:** `vote_count < 20`
- **Meaning:**
  - `True` → Movie has fewer than 20 votes.
  - `False` → Movie has 20 or more votes.
- **Percentage of `True` records:** 34.5%.
- **Purpose:** Identifies movies whose ratings may be less reliable because they are based on a small number of votes.

> **Note:** `low_votes` is a data-quality indicator and should not be interpreted as an indicator of whether a movie is good or bad.

---

## Data Cleaning

The original dataset contained **15,555 records**. During data cleaning, **169 records were removed**, resulting in **15,386 final records**.

The cleaning process included:

- Removing records with empty movie overviews.
- Removing records with missing genre information.
- Removing records with missing release dates.
- Removing records containing invalid values.
- Checking for duplicate movie IDs.
- Validating numerical variables.
- Mapping TMDB genre IDs to readable genre names.
- Deriving `release_year` from `release_date`.
- Deriving `low_votes` using the `vote_count < 20` rule.

After cleaning:

- No duplicate movie IDs remain.
- No missing values remain.
- No empty overview values remain.
- The dataset contains 15,386 movie records.

---

## Dropped Fields

The following fields from the original dataset were removed because they were not required for the analytical objectives:

| Dropped Field | Reason |
|---|---|
| `adult` | Not required for the planned analysis |
| `backdrop_path` | Media/path information not required for analysis |
| `original_title` | Redundant with the retained movie title information |
| `poster_path` | Media/path information not required for analysis |
| `softcore` | Not required for the planned analysis |
| `video` | Not required for the planned analysis |

---

## Data Quality Summary

| Quality Check | Result |
|---|---|
| Final number of records | 15,386 |
| Records removed | 169 |
| Duplicate IDs | None |
| Missing values | None |
| Empty overviews | None |
| Number of languages | 89 |
| Number of genres | 19 |
| Top 10 language share | 84.9% |
| Low-vote records | 34.5% |
| Release period | 2000–2025 |

---

## Analytical Use of the Dataset

The cleaned dataset supports the following stages of the project:

### Exploratory Data Analysis

- Numerical analysis of `popularity`, `vote_average`, and `vote_count`
- Genre distribution analysis
- Language distribution analysis
- Release-year trends
- Relationship and correlation analysis

### Text Analysis

The `overview` column can be used for:

- Plot-summary analysis
- Keyword analysis
- Text preprocessing
- TF-IDF feature extraction
- Text-based feature engineering

### Feature Engineering

Potential features can be derived from:

- `release_date`
- `release_year`
- `original_language`
- `genres`
- `popularity`
- `vote_count`
- `overview`

### Predictive Modelling

The dataset can be filtered using the `low_votes` criterion to create a more reliable modelling population. The `vote_average` variable can then be used to define the project's rating-based target.

---

## Important Interpretation Notes

1. **Popularity is not the same as movie quality.** A movie may have high popularity without having a high audience rating.

2. **Vote count affects rating reliability.** Movies with very few votes may have less stable average ratings.

3. **Genres are multi-label.** A single movie can belong to multiple genres, so genre categories are not mutually exclusive.

4. **Language distribution is uneven.** The top 10 languages represent 84.9% of the dataset, so less common languages have smaller sample sizes.

5. **`low_votes` is not a quality label.** It only indicates that a movie has fewer than 20 votes.

6. **`release_year` is a derived variable.** It is extracted from `release_date` rather than directly collected as a separate source field.

7. **The dataset is observational.** Relationships found during analysis should be interpreted as associations rather than causal relationships.

---

## Dataset Summary

The final `tmdb_clean.csv` dataset provides a structured foundation for analyzing movie performance from 2000 to 2025. It combines movie metadata, temporal information, language and genre information, plot-summary text, popularity measures, audience ratings, and voting information.

The cleaned dataset contains **15,386 records and 11 analytical variables**, with **169 records removed during preprocessing**. The resulting dataset is suitable for numerical EDA, categorical EDA, relationship analysis, text mining, feature engineering, and predictive modelling.