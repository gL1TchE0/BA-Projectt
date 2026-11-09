"""TMDB Movie Analytics dashboard.
Run from the repo root:  streamlit run dashboard/app.py
Reads the CSV files created by the notebooks (data/processed, data/ts, data/text).

Layout: each tab shows only its headline charts. Secondary charts sit in collapsed
expanders ("Show: ...") and open on click."""
import ast
import html
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="TMDB Movie Analytics", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
HIGH = 6.5                                   # a movie is "high-rated" at this rating or above
BLUE, ORANGE, GREEN, RED, GREY = "#1f4e79", "#f28e2b", "#2e9e6b", "#d1495b", "#9aa5b1"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

dark_mode = True
BLUE = "#72b7e8"
theme_values = {
    "app_bg": "#101722",
    "app_gradient_end": "#172131",
    "header_bg": "rgba(16, 23, 34, 0.86)",
    "ink": "#f2f5f8",
    "muted": "#aab6c5",
    "navy": "#a9d4f5",
    "sky": "#1c344c",
    "line": "#2c3a4d",
    "surface": "#182333",
    "sidebar_start": "#152437",
    "sidebar_end": "#101722",
    "plot": "#182333",
}

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ink: __INK__;
        --muted: __MUTED__;
        --navy: __NAVY__;
        --sky: __SKY__;
        --line: __LINE__;
        --surface: __SURFACE__;
    }

    .stApp {
        background: linear-gradient(180deg, __APP_BG__ 0%, __APP_GRADIENT_END__ 360px);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }
    [data-testid="stHeader"] { background: __HEADER_BG__; }
    [data-testid="stMainBlockContainer"] { max-width: 1480px; padding-top: 2rem; }
    h1, h2, h3, h4, [data-testid="stMetricLabel"] {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--ink);
    }
    h1 { letter-spacing: -0.04em; font-size: 2.55rem !important; margin-bottom: 0.15rem !important; }
    h2 { letter-spacing: -0.025em; margin-top: 1.6rem !important; }
    h3 { letter-spacing: -0.02em; }
    p, li, .stCaption { color: var(--muted); }

    .app-kicker {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        color: var(--navy);
        background: var(--sky);
        border: 1px solid #d6e7f6;
        border-radius: 999px;
        padding: 0.32rem 0.72rem;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }
    .app-kicker::before {
        content: "●";
        color: #f28e2b;
        font-size: 0.65rem;
    }
    .hero-copy {
        font-size: 1.05rem;
        max-width: 760px;
        color: var(--muted);
        margin-top: -0.15rem;
        margin-bottom: 1.4rem;
    }

    /* Hide Streamlit Deploy button */
    .stAppDeployButton,
    [data-testid="stAppDeployButton"],
    .stDeployButton,
    [data-testid="stDeployButton"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 0.85rem 0.95rem;
        box-shadow: 0 6px 18px rgba(25, 59, 99, 0.05);
        min-width: 0 !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-size: 0.76rem !important;
        font-weight: 600;
        white-space: normal !important;
    }
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] label,
    [data-testid="stMetricLabel"] p {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        word-break: break-word !important;
        line-height: 1.25 !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--navy);
        font-size: 1.45rem !important;
        line-height: 1.2 !important;
    }
    [data-testid="stMetricValue"] > div {
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }

    [data-baseweb="tab-list"] {
        gap: 0.45rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.25rem;
    }
    [data-baseweb="tab"] {
        height: 3rem;
        border-radius: 10px 10px 0 0;
        padding: 0 1rem;
        color: var(--muted);
        font-weight: 600;
    }
    [aria-selected="true"] {
        color: var(--navy) !important;
        background: var(--sky);
    }
    [data-baseweb="tab-highlight"] { background-color: #f28e2b; height: 3px; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, __SIDEBAR_START__ 0%, __APP_BG__ 58%, __SIDEBAR_END__ 100%);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--navy);
    }
    [data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: color-mix(in srgb, var(--surface) 88%, transparent);
    }
    [data-testid="stPlotlyChart"] {
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 0.35rem;
        background: var(--surface);
        box-shadow: 0 6px 20px rgba(25, 59, 99, 0.045);
    }
    .stButton > button, .stDownloadButton > button {
        border-radius: 9px;
        border: 1px solid var(--line);
        color: var(--navy);
        font-weight: 600;
    }
    .insight-card {
        position: relative;
        overflow: hidden;
        min-height: 142px;
        padding: 1.15rem 1.25rem 1.2rem 1.35rem;
        margin: 0.5rem 0 0.85rem;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--surface);
        box-shadow: 0 7px 20px rgba(25, 59, 99, 0.06);
    }
    .insight-card::before {
        content: "";
        position: absolute;
        inset: 0 auto 0 0;
        width: 6px;
        background: var(--accent);
    }
    .insight-topline {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 0.65rem;
    }
    .insight-icon {
        display: grid;
        place-items: center;
        width: 2.35rem;
        height: 2.35rem;
        flex: 0 0 2.35rem;
        border-radius: 12px;
        background: var(--icon-bg);
        font-size: 1.2rem;
    }
    .insight-category {
        color: var(--accent);
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.09em;
        text-transform: uppercase;
    }
    .insight-title {
        margin: 0;
        color: var(--ink);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
    }
    .insight-copy {
        margin: 0;
        color: var(--muted);
        line-height: 1.65;
        font-size: 1.02rem;
    }
    .insight-label {
        color: var(--ink);
        font-size: 0.92rem;
        font-weight: 700;
    }
    .insight-stat {
        padding: 0.95rem 1rem;
        border-radius: 14px;
        border: 1px solid var(--line);
        background: var(--surface);
    }
    .insight-stat strong {
        display: block;
        color: var(--navy);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.45rem;
    }
    .insight-stat span {
        color: var(--muted);
        font-size: 0.9rem;
    }
    .tm-pill {
        display: inline-block;
        background: var(--sky);
        color: var(--navy);
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 0.15rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 600;
        margin: 0.15rem 0.25rem 0.15rem 0;
        letter-spacing: 0.02em;
    }
    
    /* --- Website & Presentation Styling --- */
    .hero-badge-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.4rem;
    }
    .web-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 4px 16px rgba(25, 59, 99, 0.045);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .web-card h4 {
        margin: 0 0 0.5rem 0 !important;
        font-size: 1.05rem !important;
        color: var(--navy);
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }
    .web-card p {
        font-size: 0.92rem;
        line-height: 1.55;
        color: var(--muted);
        margin: 0;
    }
    .scorecard-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0.8rem 0;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }
    .scorecard-table th {
        text-align: left;
        padding: 0.75rem 0.9rem;
        background: var(--sky);
        color: var(--navy);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        border-bottom: 2px solid var(--line);
    }
    .scorecard-table td {
        padding: 0.75rem 0.9rem;
        border-bottom: 1px solid var(--line);
        font-size: 0.88rem;
        color: var(--ink);
    }
    .scorecard-table tr:last-child td {
        border-bottom: none;
    }
    .scorecard-table tr:hover {
        background: rgba(255, 255, 255, 0.02);
    }
    .tag-pass {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: rgba(46, 158, 107, 0.15);
        color: #4ade80;
        border: 1px solid rgba(46, 158, 107, 0.35);
        border-radius: 999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.74rem;
        font-weight: 700;
        white-space: nowrap;
    }
    .team-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(215px, 1fr));
        gap: 0.75rem;
        margin-top: 0.85rem;
    }
    .team-item {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        border-top: 3px solid #72b7e8;
    }
    .team-name {
        font-weight: 700;
        font-size: 0.93rem;
        color: var(--ink);
        margin-bottom: 0.15rem;
    }
    .team-id {
        font-size: 0.76rem;
        color: #f28e2b;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .team-role {
        font-size: 0.8rem;
        color: var(--muted);
        line-height: 1.4;
    }

    </style>
    """.replace("__INK__", theme_values["ink"])
    .replace("__MUTED__", theme_values["muted"])
    .replace("__NAVY__", theme_values["navy"])
    .replace("__SKY__", theme_values["sky"])
    .replace("__LINE__", theme_values["line"])
    .replace("__SURFACE__", theme_values["surface"])
    .replace("__APP_BG__", theme_values["app_bg"])
    .replace("__APP_GRADIENT_END__", theme_values["app_gradient_end"])
    .replace("__HEADER_BG__", theme_values["header_bg"])
    .replace("__SIDEBAR_START__", theme_values["sidebar_start"])
    .replace("__SIDEBAR_END__", theme_values["sidebar_end"]),
    unsafe_allow_html=True,
)

# ---- EDIT THESE: recommendations shown on the last tab (add your time-series and text-mining ones) ----
RECS = [
    ("Use genre benchmarks when evaluating titles",
     "Documentary, Animation, History and Music titles have the strongest average ratings, while Horror and Thriller rank lower. "
     "Evaluate each title against the typical performance of its genre rather than against the catalogue-wide average."),
    ("Separate audience reach from perceived quality",
     "Popularity and rating show only a weak relationship, with a correlation of approximately 0.16. Use popularity to assess reach "
     "and ratings together with vote counts to assess audience reception."),
    ("Apply predictive modelling as an early screening tool",
     "The content-only model achieves an AUC of 0.785, compared with 0.500 for random classification. It can support early-stage "
     "prioritisation, but it should complement—not replace—creative and commercial judgement."),
    ("Use post-release engagement to update expectations",
     "Adding popularity and vote count increases model AUC to 0.836. Monitoring early audience engagement can therefore improve "
     "performance estimates after a title is released."),
    ("Evaluate international content with appropriate context",
     "Japanese and Korean titles that meet the 20-vote threshold have higher average ratings in this sample. Because this is a "
     "self-selected group, validate the pattern with broader audience and market data before making investment decisions."),
    ("Plan for stable ratings and competitive genre markets",
     "Average ratings remained close to 6.06 through 2019 and have been near 6.3 since 2020. The forecast suggests stability rather "
     "than continued growth. Horror and Thriller have expanded their genre share, while Drama has declined, increasing the need for "
     "clear differentiation and consistent execution."),
    ("Use plot language as a supplementary quality signal",
     "Higher-rated summaries more often use factual and historical language, while lower-rated summaries contain more formulaic crime "
     "and romance terms. Topic and wording analysis can inform early concept reviews, but these patterns should be treated as signals "
     "rather than definitive predictors."),
    ("Translate text-mining results into focused concept reviews",
     "Compare a proposed story with the themes and language associated with similar titles. Use the comparison to identify strengths, "
     "risks and opportunities for refinement before production."),
]

# ---- Predictive model results (static benchmarks) ----
METRICS = pd.DataFrame({
    "Model": ["Baseline (majority class)", "Random Forest, set A (content only)", "Random Forest, set B (+ popularity and votes)"],
    "Accuracy": [0.610, 0.736, 0.758], "Precision": [0.0, 0.720, 0.747], "Recall": [0.0, 0.527, 0.575],
    "F1": [0.0, 0.608, 0.650], "AUC": [0.5, 0.785, 0.836]})
CV = pd.DataFrame({"Set": ["B", "B", "A", "A"], "Model": ["XGBoost", "Random Forest", "XGBoost", "Random Forest"],
                   "CV AUC untuned": [0.798, 0.816, 0.728, 0.739], "CV AUC tuned": [0.815, 0.819, 0.757, 0.761]})
IMP_B = {"log_votes": .0658, "Documentary": .0490, "Horror": .0315, "English": .0307, "Animation": .0267,
         "release_year": .0237, "Drama": .0160, "log_popularity": .0143, "Thriller": .0130, "Japanese": .0102,
         "Comedy": .0074, "Korean": .0061, "French": .0033, "TV Movie": .0030, "Other language": .0025}
IMP_A = {"Documentary": .0487, "Horror": .0376, "Animation": .0369, "release_year": .0196, "Drama": .0164,
         "Thriller": .0135, "English": .0092, "Japanese": .0088, "Comedy": .0060, "Korean": .0059,
         "History": .0038, "French": .0033, "month": .0032, "overview_words": .0031, "Music": .0016}
INSIGHT_META = [
    ("01", "Choosing a movie", "#2e9e6b", "rgba(46, 158, 107, 0.14)"),
    ("02", "Popularity vs quality", "#f28e2b", "rgba(242, 142, 43, 0.15)"),
    ("03", "Before release", "#1f80c0", "rgba(31, 128, 192, 0.14)"),
    ("04", "After release", "#8a63d2", "rgba(138, 99, 210, 0.14)"),
    ("05", "Global audiences", "#d1495b", "rgba(209, 73, 91, 0.14)"),
    ("06", "Planning ahead", "#1f4e79", "rgba(31, 78, 121, 0.14)"),
    ("07", "Understanding stories", "#2e9e6b", "rgba(46, 158, 107, 0.14)"),
    ("08", "Next step", "#667085", "rgba(102, 112, 133, 0.14)"),
]


# ---------------- helpers ----------------
def show(fig):
    fig.update_layout(
        template="plotly_dark" if dark_mode else "plotly_white",
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="DM Sans, sans-serif", color=theme_values["ink"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=theme_values["plot"],
        title=dict(font=dict(family="Space Grotesk, sans-serif", size=17, color=theme_values["navy"])),
        legend=dict(
            bgcolor=theme_values["surface"],
            bordercolor=theme_values["line"],
            borderwidth=1,
            font=dict(color=theme_values["ink"]),
        ),
    )
    fig.update_xaxes(showgrid=True, gridcolor=theme_values["line"], zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=theme_values["line"], zeroline=False)
    try: st.plotly_chart(fig, width="stretch")
    except TypeError: st.plotly_chart(fig, use_container_width=True)

def table(df, **kw):
    try: st.dataframe(df, width="stretch", hide_index=True, **kw)
    except TypeError: st.dataframe(df, use_container_width=True, hide_index=True, **kw)

def more(label):
    """Collapsed section for secondary charts; click the header to show them."""
    return st.expander(f"Show: {label}", expanded=False)

def need(df, fname, notebook):
    if df is None:
        st.warning(f"Missing `{fname}`. Run the notebook `{notebook}` to create it. The other tabs still work.")
        return False
    return True

@st.cache_data
def read(rel, dates=None):
    p = DATA / rel
    if not p.exists(): return None
    return pd.read_csv(p, parse_dates=dates) if dates else pd.read_csv(p)

@st.cache_data
def load_clean():
    df = read("processed/tmdb_clean.csv", ["release_date"])
    if df is None: return None
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df["high_rated"] = (df["vote_average"] >= HIGH).astype(int)
    df["decade"] = (df["release_year"] // 10 * 10).astype(str) + "s"
    return df

@st.cache_data
def load_text():
    df = read("text/text_movie_level.csv")
    if df is None: return None
    df["genres"] = df["genres"].fillna("").str.split("|")
    return df

def filt(df, y0, y1, gsel, lsel, minv):
    m = df["release_year"].between(y0, y1) & (df["vote_count"] >= minv)
    if lsel: m &= df["original_language"].isin(lsel)
    if gsel: m &= df["genres"].apply(lambda l: any(g in l for g in gsel))
    return df[m]


# ---------------- data and sidebar ----------------
clean, text = load_clean(), load_text()
base = clean if clean is not None else text
if base is None:
    st.error("No data found. Run the notebooks first (data/processed/tmdb_clean.csv is required).")
    st.stop()

st.markdown('<div class="app-kicker">TMDB intelligence workspace</div>', unsafe_allow_html=True)
st.title("Movie Performance Analytics")
st.markdown(
    '<div class="hero-copy">Explore what shapes movie ratings across 15,000+ titles — from genre patterns and audience engagement to forecasts and plot themes.</div>',
    unsafe_allow_html=True,
)
with st.expander("About the data and how to read this dashboard"):
    st.markdown(
        "- The data is a **sample** of about 600 movies per release year (random pages from the TMDB API), so we do not chart the "
        "number of releases per year as a trend.\n"
        "- TMDB **popularity** is a recent-activity score. Ratings from movies with fewer than 20 votes are noisy.\n"
        "- Forecast bands for the Holt and naive models are approximate. The newest 12 months are not modelled (few votes).\n"
        "- **Sentiment** is the tone of the plot summary (TextBlob), not audience opinion. Topic names come from the team.\n"
        "- All findings are **associations, not causes**.\n"
        f"- High-rated means a rating of {HIGH} or more.\n"
        "- Each tab shows its main charts. Click a **Show:** section to open the extra charts.")

ge = base.explode("genres")["genres"].dropna()
all_genres = sorted(ge[ge != ""].unique())
langs = base["original_language"].value_counts().head(15).index.tolist()
ymin, ymax = int(base["release_year"].min()), int(base["release_year"].max())

st.sidebar.markdown("### Explore the catalogue")
st.sidebar.caption("Refine the analysis below. Your selections flow through the Overview, EDA and Text mining tabs.")
st.sidebar.header("Filters")
yr = st.sidebar.slider("Release year", ymin, ymax, (ymin, ymax))
gsel = st.sidebar.multiselect("Genre (empty = all)", all_genres)
lsel = st.sidebar.multiselect("Original language (empty = all)", langs)
minv = st.sidebar.slider("Minimum votes", 10, 200, 20, step=5)
st.sidebar.caption("Filters apply to the Overview, EDA and Text mining tabs. Time-series files are already aggregated "
                   "(only the year range applies to the yearly charts).")

f = filt(clean, *yr, gsel, lsel, minv) if clean is not None else None
ft = filt(text, *yr, gsel, lsel, max(minv, 20)) if text is not None else None
tabs = st.tabs(["Project & Data", "Overview", "EDA", "Predict a movie", "Time series", "Text mining", "Insights"])

# ================= 0. Project & Data =================
with tabs[0]:
    st.subheader("Project Overview & Business Problem")
    st.caption("Executive context, analytical objectives, and decision framework for movie performance analysis.")

    bcol1, bcol2, bcol3 = st.columns(3)
    with bcol1:
        st.markdown(
            """
            <div class="web-card">
                <h4>The Business Problem</h4>
                <p>Studios, production companies, and streaming platforms face high capital risk when deciding which titles to greenlight, acquire, or promote. Audience reception varies widely across genres, languages, and time periods, with little certainty on pre-release returns.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with bcol2:
        st.markdown(
            """
            <div class="web-card">
                <h4>Core Objectives</h4>
                <p><strong>1. Binary Classification:</strong> Predict high-rated titles (rating ≥ 6.5) with target AUC > 0.75 using pre-release metadata.<br>
                <strong>2. Time-Series Dynamics:</strong> Forecast macro rating stability and track shifting genre shares.<br>
                <strong>3. NLP Plot Mining:</strong> Extract high-rated story themes and wording patterns.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with bcol3:
        st.markdown(
            """
            <div class="web-card">
                <h4>Decision Impact</h4>
                <p><strong>Concept Screening:</strong> Prioritise pitch decks using data-driven signals.<br>
                <strong>Portfolio Allocation:</strong> Balance genre exposure against expanding vs saturated market segments.<br>
                <strong>Post-Release Tracking:</strong> Rapidly update rating expectations once early audience engagement surfaces.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<hr class="tm-divider" style="margin:1.8rem 0 1.2rem;">', unsafe_allow_html=True)
    st.subheader("Dataset Architecture & Collection Pipeline")
    st.caption("Data was harvested directly from the TMDB API v3 (/discover/movie, /genre/movie/list) across release years 2000 to 2025. No pre-built dataset was used.")

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Raw Harvested", "15,555", help="30 random pages per year fetched directly from TMDB API v3.")
    p2.metric("Cleaned / Dropped", "169", help="105 blank summaries + 64 invalid/empty genre records.")
    p3.metric("Verified Clean", "15,386", help="Clean master records covering 2000–2025 with 0 missing values.")
    p4.metric("Core Modeling Set", "10,078", help="Reliable titles with 20+ votes used for machine learning and NLP.")

    st.markdown('<hr class="tm-divider" style="margin:1.8rem 0 1.2rem;">', unsafe_allow_html=True)
    st.subheader("Data Validation & Preprocessing Scorecard")
    st.caption("Comprehensive data audit confirming cleanliness, consistency, and feature readiness before modeling.")

    scorecard_html = """
    <table class="scorecard-table">
        <thead>
            <tr>
                <th style="width:22%;">Audit Dimension</th>
                <th style="width:33%;">Finding / Raw State</th>
                <th style="width:32%;">Action Taken / Engineering</th>
                <th style="width:13%;">Validation</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Missing Values & Duplicates</strong></td>
                <td>0 null values in core numeric fields; 0 duplicate TMDB IDs; 105 blank overview texts.</td>
                <td>Dropped 105 rows with empty overviews. Final dataset has 0 missing values across all 11 variables.</td>
                <td><span class="tag-pass">Passed: 0 NaN / Dups</span></td>
            </tr>
            <tr>
                <td><strong>Data Types & Integrity</strong></td>
                <td>Genres provided as JSON-like ID lists; release dates formatted as strings; 64 invalid rows.</td>
                <td>Parsed dates to datetime; mapped genre IDs to names; bounded ratings within [0, 10]; purged 64 invalid rows.</td>
                <td><span class="tag-pass">Passed: Schema Valid</span></td>
            </tr>
            <tr>
                <td><strong>Outlier Strategy</strong></td>
                <td>Extreme values in popularity (up to 88.5) and vote count (up to 34,700).</td>
                <td>Retained real blockbusters (authentic market distribution); applied log transformations (log_popularity, log_votes).</td>
                <td><span class="tag-pass">Passed: Log-Scaled</span></td>
            </tr>
            <tr>
                <td><strong>Categorical Encoding</strong></td>
                <td>19 movie genres (multi-label) and 89 distinct original languages.</td>
                <td>Multi-hot binary encoding for 19 genres; one-hot encoding for top-10 languages + "Other".</td>
                <td><span class="tag-pass">Passed: One-Hot Enc</span></td>
            </tr>
            <tr>
                <td><strong>Noise Threshold & Target</strong></td>
                <td>Small-sample ratings (< 20 votes) exhibit heavy variance and artificial 10.0 ratings.</td>
                <td>Set 20-vote minimum cutoff. Defined high_rated target as vote_average ≥ 6.5 (39% positive class).</td>
                <td><span class="tag-pass">Passed: Balanced (39%)</span></td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(scorecard_html, unsafe_allow_html=True)

    with st.expander("Inspect sample records from the clean master catalogue"):
        if clean is not None:
            preview_df = clean[["title", "release_year", "original_language", "vote_average", "vote_count", "popularity", "genres"]].head(50)
            st.dataframe(preview_df, use_container_width=True, hide_index=True)
            st.caption("Showing 50 sample titles from data/processed/tmdb_clean.csv (15,386 total titles).")

    


# ================= 1. Overview =================
with tabs[1]:
    if not need(clean, "data/processed/tmdb_clean.csv", "Review1_TMDB_Final.ipynb"): pass
    elif f.empty: st.warning("No movies match the current filters.")
    else:
        k = st.columns(5)
        k[0].metric("Movies", f"{len(f):,}")
        k[1].metric("Average rating", f"{f['vote_average'].mean():.2f}")
        k[2].metric("High-rated share", f"{f['high_rated'].mean():.0%}",
                    help="Percentage of movies with vote_average ≥ 6.5 (reliable titles with 20+ votes).")
        k[3].metric("Avg popularity", f"{f['popularity'].mean():.2f}",
                    help="TMDB activity score based on daily views, searches, and user watchlist additions.")
        k[4].metric("Years covered", f"{f['release_year'].min()}–{f['release_year'].max()}")
        g = f.explode("genres")
        gs = g.groupby("genres").agg(movies=("id", "size"), rating=("vote_average", "mean")).reset_index()
        ya = f.groupby("release_year")["vote_average"].mean().reset_index()
        fig = px.line(ya, x="release_year", y="vote_average", markers=True, title="Average rating by release year",
                      labels={"release_year": "Year", "vote_average": "Average rating"}, color_discrete_sequence=[BLUE])
        show(fig)

        fig = px.bar(gs.sort_values("movies").tail(12), x="movies", y="genres", orientation="h", color="rating",
                     color_continuous_scale="RdYlGn", title="Movies per genre (colour = average rating)",
                     labels={"movies": "Movies", "genres": "", "rating": "Avg rating"})
        show(fig)
        with more("distribution of ratings"):
            fig = px.histogram(f, x="vote_average", nbins=40, title="Distribution of ratings", color_discrete_sequence=[BLUE],
                               labels={"vote_average": "Rating"})
            fig.add_vline(x=HIGH, line_dash="dash", line_color=RED, annotation_text=f"high-rated from {HIGH}")
            show(fig)
            st.caption(f"Ratings are centred near {f['vote_average'].median():.1f}; {f['high_rated'].mean():.0%} of the selected "
                       f"movies are rated {HIGH} or more.")


# ================= 2. EDA =================
with tabs[2]:
    if not need(clean, "data/processed/tmdb_clean.csv", "Review1_TMDB_Final.ipynb"): pass
    elif f.empty: st.warning("No movies match the current filters.")
    else:
        g = f.explode("genres")
        gs = g.groupby("genres").agg(movies=("id", "size"), rating=("vote_average", "mean"),
                                     pop=("popularity", "mean")).query("movies >= 30").reset_index()
        metric = st.radio("Compare genres by", ["Average rating", "Average popularity"], horizontal=True)
        mcol, mcolor = ("rating", ORANGE) if metric == "Average rating" else ("pop", GREEN)
        
        if gs.empty:
            st.info("No genres have 30 or more movies under the current filter selection. Broaden your year range or genre filters to view rankings.")
        else:
            fig = px.bar(gs.sort_values(mcol), x=mcol, y="genres", orientation="h", color_discrete_sequence=[mcolor],
                         title=f"{metric} by genre", labels={mcol: metric, "genres": ""}, hover_data={"movies": True})
            show(fig)
            if len(gs) > 1:
                hi_, lo_ = gs.loc[gs["rating"].idxmax()], gs.loc[gs["rating"].idxmin()]
                st.caption(f"Highest rated genre: {hi_['genres']} ({hi_['rating']:.2f}). Lowest: {lo_['genres']} ({lo_['rating']:.2f}). "
                           "Genres with fewer than 30 movies are hidden.")
            elif len(gs) == 1:
                st.caption(f"Only one genre ({gs['genres'].iloc[0]}) meets the 30-movie threshold in this selection.")
        with more("rating by language and by decade"):
            ls = (f.groupby("original_language").agg(movies=("id", "size"), rating=("vote_average", "mean"))
                    .sort_values("movies", ascending=False).head(10).reset_index().sort_values("rating"))
            fig = px.bar(ls, x="rating", y="original_language", orientation="h", color_discrete_sequence=[BLUE],
                         title="Average rating by language (10 most common)", hover_data={"movies": True},
                         labels={"rating": "Average rating", "original_language": "Language"})
            show(fig)

            fig = px.box(f.sort_values("decade"), x="decade", y="vote_average", color_discrete_sequence=[BLUE],
                         title="Rating by decade", labels={"decade": "Decade", "vote_average": "Rating"})
            show(fig)
        with more("rating vs popularity (scatter)"):
            s = f.sample(min(3000, len(f)), random_state=1).assign(
                group=lambda d: np.where(d["high_rated"] == 1, "High-rated", "Not high-rated"))
            fig = px.scatter(s, x="popularity", y="vote_average", color="group", log_x=True, opacity=0.5, hover_name="title",
                             color_discrete_map={"High-rated": GREEN, "Not high-rated": RED},
                             title="Rating vs popularity (log scale, sample of up to 3,000 movies)",
                             labels={"popularity": "Popularity (log)", "vote_average": "Rating"})
            show(fig)
            r = f[["vote_average", "popularity", "vote_count"]].corr(method="spearman")
            r_pop = r.loc["vote_average", "popularity"]
            r_cnt = r.loc["vote_average", "vote_count"]
            
            def _eval_corr(v):
                if pd.isna(v): return "negligible"
                av = abs(v)
                if av < 0.30: return "weak"
                if av < 0.50: return "moderate"
                return "strong"

            s_pop, s_cnt = _eval_corr(r_pop), _eval_corr(r_cnt)
            if s_pop == s_cnt:
                desc = f"Both show a {s_pop} relationship."
            else:
                desc = f"Popularity is {s_pop}, while vote count is {s_cnt}."
            st.caption(f"Spearman correlation with rating: popularity {r_pop:.2f}, vote count {r_cnt:.2f}. {desc}")


# ================= 3. Predict a movie =================
with tabs[3]:
    st.subheader("Pre-Release Movie Success Predictor")
    st.caption("Estimate the likelihood of high audience ratings (≥ 6.5) for a movie concept before production using the trained Random Forest classifier.")

    pcol1, pcol2 = st.columns(2)
    with pcol1:
        sim_genres = st.multiselect(
            "Select Genre(s)",
            [
                "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
                "Drama", "Family", "Fantasy", "History", "Horror", "Music", "Mystery",
                "Romance", "Science Fiction", "TV Movie", "Thriller", "War", "Western"
            ],
            default=["Animation", "Adventure"]
        )
        sim_lang = st.selectbox(
            "Original Language",
            ["English", "Japanese", "French", "Spanish", "German", "Italian", "Korean", "Hindi", "Russian", "Chinese", "Other"],
            index=0
        )
    with pcol2:
        sim_year = st.slider("Target Release Year", 2000, 2030, 2025)
        sim_month = st.selectbox("Target Release Month", list(range(1, 13)), format_func=lambda m: MONTHS[m - 1], index=10)
        sim_words = st.slider("Synopsis Length (word count)", 10, 150, 50)

    model_path = ROOT / "models" / "RandForest_A.pkl"
    if model_path.exists():
        import joblib
        try:
            rf_model = joblib.load(model_path)
            feats = rf_model.feature_names_in_
            row = pd.DataFrame([{f: 0 for f in feats}])
            row["release_year"] = sim_year
            row["month"] = sim_month
            row["ov_words"] = sim_words
            row["n_genres"] = len(sim_genres)
            for g in sim_genres:
                g_col = f"g_{g}"
                if g_col in row.columns:
                    row[g_col] = 1
            lang_map = {
                "English": "l_en", "Japanese": "l_ja", "French": "l_fr", "Spanish": "l_es",
                "German": "l_de", "Italian": "l_it", "Korean": "l_ko", "Hindi": "l_hi",
                "Russian": "l_ru", "Chinese": "l_zh", "Other": "l_other"
            }
            l_col = lang_map.get(sim_lang, "l_other")
            if l_col in row.columns:
                row[l_col] = 1

            if not sim_genres:
                st.warning("Please select at least one genre to get a prediction.")
            else:
                prob = rf_model.predict_proba(row)[0, 1]
                is_high = prob >= 0.5
                badge_color = "#2e9e6b" if is_high else "#d1495b"
                badge_title = "HIGH-RATED (≥ 6.5)" if is_high else "NOT HIGH-RATED (< 6.5)"

                st.markdown(
                    f'''
                    <div style="background:var(--surface); border:1px solid var(--line); border-left:5px solid {badge_color}; border-radius:12px; padding:1.1rem 1.3rem; margin-top:0.8rem;">
                        <span style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; font-weight:700; color:{badge_color};">ML Classification Output</span>
                        <h3 style="margin:0.2rem 0 0.4rem; color:var(--ink);">{badge_title} · {prob:.1%} Probability</h3>
                        <p style="margin:0; font-size:0.92rem; color:var(--muted); line-height:1.5;">
                            Evaluated using pre-release metadata ({len(sim_genres)} genre(s), {sim_lang} language, {MONTHS[sim_month-1]} {sim_year} release).
                            {"This concept aligns with characteristics of historically well-received titles." if is_high else "This concept faces higher odds of receiving average or polarized reviews based on historical benchmarks."}
                        </p>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
        except Exception as e:
            st.caption(f"Simulator error: {e}")

    st.markdown('<hr class="tm-divider" style="margin:2rem 0 1.2rem;">', unsafe_allow_html=True)
    st.subheader("Model Performance & Benchmarks")
    st.caption(f"Target: rating of {HIGH} or more, for movies with 20 or more votes (10,078 movies, 39% high-rated). "
               "Stratified 80/20 split: 8,062 training and 2,016 test movies. Evaluated on the held-out test set.")
    table(METRICS.style.format({c: "{:.3f}" for c in METRICS.columns[1:]}))

    st.markdown("**Robustness:** with at least 50 votes (5,717 movies) the AUC is 0.841, so the results do not depend on the 20-vote cut-off.")
    st.info("Set B uses popularity and votes (known only after release), while Set A is the pre-release version used in the predictor above. "
            "Feature importance reflects what the model relies on, not direct cause and effect.")

    with more("cross-validation AUC before and after tuning"):
        table(CV)

    with more("top 15 features for set A and set B"):
        for name, imp, colr in [("Set B (with popularity and votes)", IMP_B, BLUE), ("Set A (content only)", IMP_A, ORANGE)]:
            d = pd.Series(imp).sort_values().reset_index(); d.columns = ["feature", "importance"]
            fig = px.bar(d, x="importance", y="feature", orientation="h", color_discrete_sequence=[colr],
                         title=f"Top 15 features, {name}", labels={"importance": "Drop in AUC when shuffled", "feature": ""})
            show(fig)


# ================= 4. Time series =================
with tabs[4]:
    ms, fo = read("ts/monthly_series.csv", ["month"]), read("ts/forecast.csv", ["month"])
    mc, se = read("ts/model_comparison.csv"), read("ts/seasonality.csv")
    gc = read("ts/genre_share_change.csv")
    nb = "Review2_TimeSeries.ipynb"
    if need(ms, "data/ts/monthly_series.csv", nb):
        st.subheader("Trend")
        what = st.radio("Series", ["Average rating", "Average popularity"], horizontal=True)
        col = "rating" if what == "Average rating" else "pop"
        r12 = ms[col].rolling(12).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ms["month"], y=ms[col], name="Monthly", line=dict(color=BLUE, width=1), opacity=0.4))
        fig.add_trace(go.Scatter(x=ms["month"], y=r12, name="12-month mean", line=dict(color=ORANGE, width=3)))
        if "used" in ms and (~ms["used"]).any():
            x0 = ms.loc[~ms["used"], "month"].min()
            fig.add_shape(type="rect", xref="x", yref="paper", x0=x0, x1=ms["month"].max(), y0=0, y1=1,
                          fillcolor=GREY, opacity=0.25, line_width=0)
            fig.add_annotation(x=x0, y=1, yref="paper", text="Recent months (few votes, not modelled)",
                               showarrow=False, xanchor="left", yanchor="bottom", font=dict(size=11, color="#555"))
        fig.update_layout(title=f"{what} by release month", yaxis_title=what, xaxis_title="Month")
        show(fig)
        u = ms[ms["used"]] if "used" in ms else ms
        per = [(a, b) for a, b in [(2000, 2009), (2010, 2019), (2020, 2100)]]
        vals = [u[u["month"].dt.year.between(a, b)][col].mean() for a, b in per]
        st.caption("Average by period: " + ", ".join(f"{n} {v:.2f}" for n, v in zip(["2000s", "2010s", "2020s"], vals) if pd.notna(v)))

        st.subheader("Forecast")
        if need(fo, "data/ts/forecast.csv", nb):
            hist = u[["month", "rating"]].tail(96)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist["month"], y=hist["rating"], name="Actual", line=dict(color=BLUE)))
            fig.add_trace(go.Scatter(x=pd.concat([fo["month"], fo["month"][::-1]]), y=pd.concat([fo["hi"], fo["lo"][::-1]]),
                                     fill="toself", fillcolor="rgba(242,142,43,0.25)", line=dict(width=0), name="95% band"))
            fig.add_trace(go.Scatter(x=fo["month"], y=fo["forecast"], name="Forecast", line=dict(color=ORANGE, width=3)))
            fig.update_layout(title=f"Average rating: next {len(fo)} months ({fo['model'].iloc[0]})", yaxis_title="Average rating")
            show(fig)
            st.caption(f"Forecast average {fo['forecast'].mean():.2f} against {u['rating'].tail(12).mean():.2f} over the last 12 modelled "
                       "months. The band is wide, so read the forecast as 'about the same level', not a precise number.")
        if need(mc, "data/ts/model_comparison.csv", nb):
            st.markdown("**Model comparison on the held-out months** (lower error is better; best row highlighted)")
            sty = mc.style.highlight_min(subset=["RMSE"], color="rgba(46, 158, 107, 0.3)").format(
                {c: "{:.4f}" for c in ["MAE", "RMSE"]} | ({"RMSE vs naive (%)": "{:+.1f}"} if "RMSE vs naive (%)" in mc else {}))
            table(sty)
            best = mc.loc[mc["RMSE"].idxmin(), "model"]
            st.caption(f"Best model on the test months: {best}." + (" No model beat the naive baseline, so the series has little "
                       "predictable structure beyond its recent level." if str(best).startswith("Naive") else ""))
        with more("seasonality and change in genre share"):
            if need(se, "data/ts/seasonality.csv", nb):
                se = se.assign(m=lambda d: d["month_of_year"].map(lambda i: MONTHS[int(i) - 1]))
                fig = px.bar(se, x="m", y="avg_rating", color_discrete_sequence=[GREEN], title="Average rating by release month",
                             labels={"m": "Month", "avg_rating": "Average rating"})
                fig.update_yaxes(range=[se["avg_rating"].min() - 0.1, se["avg_rating"].max() + 0.1])
                show(fig)
                st.caption(f"Highest in {se.loc[se['avg_rating'].idxmax(), 'm']}, lowest in {se.loc[se['avg_rating'].idxmin(), 'm']}; "
                           f"the whole range is only {se['avg_rating'].max() - se['avg_rating'].min():.2f} rating points.")

            if need(gc, "data/ts/genre_share_change.csv", nb):
                cc = gc.columns[1]
                fig = px.bar(gc.sort_values(cc), x=cc, y="genre", orientation="h", title="Change in genre share (percentage points)",
                             color=gc.sort_values(cc)[cc] > 0, color_discrete_map={True: GREEN, False: RED},
                             labels={cc: "Change (pp)", "genre": ""})
                fig.update_layout(showlegend=False); show(fig)
                st.caption(f"Biggest rise: {gc.loc[gc[cc].idxmax(), 'genre']} ({gc[cc].max():+.1f} pp). "
                           f"Biggest fall: {gc.loc[gc[cc].idxmin(), 'genre']} ({gc[cc].min():+.1f} pp), "
                           "first five years vs last five modelled years.")


# ================= 5. Text mining =================
with tabs[5]:
    nb = "TextMining.ipynb"
    if not need(text, "data/text/text_movie_level.csv", nb): pass
    elif ft.empty: st.warning("No movies match the current filters (text mining uses movies with 20 or more votes).")
    else:
        # ---- section-level CSS for text mining tab ----
        st.markdown("""
        <style>
        .tm-section-header {
            display: flex; align-items: center; gap: 0.6rem;
            margin: 1.6rem 0 0.6rem; padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--line);
        }
        .tm-section-header .tm-icon {
            display: grid; place-items: center;
            width: 2.1rem; height: 2.1rem; border-radius: 10px;
            font-size: 1.1rem;
        }
        .tm-section-header h3 {
            margin: 0 !important; font-size: 1.25rem !important;
            letter-spacing: -0.02em;
        }
        .tm-kpi { text-align: center; padding: 0.7rem 0.5rem; }
        .tm-kpi strong {
            display: block; font-family: 'Space Grotesk', sans-serif;
            font-size: 1.55rem; color: var(--navy);
        }
        .tm-kpi span { font-size: 0.82rem; color: var(--muted); }
        .tm-topic-card {
            padding: 1rem 1.15rem; border: 1px solid var(--line);
            border-radius: 14px; background: var(--surface);
            box-shadow: 0 4px 14px rgba(25,59,99,0.045);
            margin-bottom: 0.5rem;
        }
        .tm-topic-name {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700; font-size: 1rem; color: var(--ink);
            margin-bottom: 0.25rem;
        }
        .tm-topic-words {
            font-size: 0.82rem; color: var(--muted);
            line-height: 1.5; margin-bottom: 0.55rem;
        }
        .tm-topic-stats {
            display: flex; gap: 1rem; flex-wrap: wrap;
        }
        .tm-topic-stat {
            font-size: 0.78rem; color: var(--muted);
        }
        .tm-topic-stat strong {
            color: var(--navy); font-family: 'Space Grotesk', sans-serif;
            font-size: 0.95rem;
        }
        .tm-divider {
            border: none; border-top: 1px solid var(--line);
            margin: 1.2rem 0;
        }
        
    /* --- Website & Presentation Styling --- */
    .hero-badge-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.4rem;
    }
    .web-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 4px 16px rgba(25, 59, 99, 0.045);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .web-card h4 {
        margin: 0 0 0.5rem 0 !important;
        font-size: 1.05rem !important;
        color: var(--navy);
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }
    .web-card p {
        font-size: 0.92rem;
        line-height: 1.55;
        color: var(--muted);
        margin: 0;
    }
    .scorecard-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0.8rem 0;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }
    .scorecard-table th {
        text-align: left;
        padding: 0.75rem 0.9rem;
        background: var(--sky);
        color: var(--navy);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        border-bottom: 2px solid var(--line);
    }
    .scorecard-table td {
        padding: 0.75rem 0.9rem;
        border-bottom: 1px solid var(--line);
        font-size: 0.88rem;
        color: var(--ink);
    }
    .scorecard-table tr:last-child td {
        border-bottom: none;
    }
    .scorecard-table tr:hover {
        background: rgba(255, 255, 255, 0.02);
    }
    .tag-pass {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: rgba(46, 158, 107, 0.15);
        color: #4ade80;
        border: 1px solid rgba(46, 158, 107, 0.35);
        border-radius: 999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.74rem;
        font-weight: 700;
        white-space: nowrap;
    }
    .team-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(215px, 1fr));
        gap: 0.75rem;
        margin-top: 0.85rem;
    }
    .team-item {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        border-top: 3px solid #72b7e8;
    }
    .team-name {
        font-weight: 700;
        font-size: 0.93rem;
        color: var(--ink);
        margin-bottom: 0.15rem;
    }
    .team-id {
        font-size: 0.76rem;
        color: #f28e2b;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .team-role {
        font-size: 0.8rem;
        color: var(--muted);
        line-height: 1.4;
    }

    </style>
        """, unsafe_allow_html=True)

        # ---- KPI row ----
        avg_pol = ft["polarity"].mean()
        dominant_topic = ft["topic_name"].value_counts().idxmax()
        kc = st.columns(4)
        kc[0].metric("Movies analysed", f"{len(ft):,}")
        kc[1].metric("Average rating", f"{ft['vote_average'].mean():.2f}")
        kc[2].metric("Average polarity", f"{avg_pol:.3f}",
                     help="Plot summary sentiment score: -1.0 (negative/dark) to +1.0 (positive/joyful). 0.0 is neutral.")
        kc[3].metric("Most common topic", dominant_topic)

        st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

        # ---- Topics ----
        st.markdown(
            '<div class="tm-section-header">'
            '<div class="tm-icon" style="background:rgba(31,128,192,0.12); font-weight:700; color:var(--navy); font-size:0.85rem;">01</div>'
            '<h3>Topic analysis</h3></div>', unsafe_allow_html=True)
        st.caption("Topics extracted using LDA on plot overviews. Each movie belongs to the topic with the highest probability.")

        tsum = read("text/topics_summary.csv")
        tt = ft.groupby(["topic", "topic_name"]).agg(movies=("id", "size"), avg_rating=("vote_average", "mean"),
                                                     high_rated=("high_rated", "mean"), avg_popularity=("popularity", "mean")).reset_index()
        if tsum is not None: tt = tt.merge(tsum[["topic", "top_words", "coherence"]], on="topic", how="left")
        tt["high_rated"] = (tt["high_rated"] * 100).round(1)

        # topic cards (2 per row with pill badges)
        tt_sorted = tt.sort_values("avg_rating", ascending=False)
        for row_start in range(0, len(tt_sorted), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                idx = row_start + j
                if idx >= len(tt_sorted):
                    break
                r = tt_sorted.iloc[idx]
                raw_words = [w.strip() for w in str(r.get("top_words", "")).split(",") if w.strip()][:7]
                pills_html = "".join([f'<span class="tm-pill">#{html.escape(w)}</span>' for w in raw_words])
                col.markdown(
                    f'<div class="tm-topic-card">'
                    f'<div class="tm-topic-name">{html.escape(str(r["topic_name"]))}</div>'
                    f'<div class="tm-topic-words" style="margin: 0.35rem 0 0.65rem;">{pills_html}</div>'
                    f'<div class="tm-topic-stats">'
                    f'<div class="tm-topic-stat"><strong>{int(r["movies"]):,}</strong> movies</div>'
                    f'<div class="tm-topic-stat"><strong>{r["avg_rating"]:.2f}</strong> avg rating</div>'
                    f'<div class="tm-topic-stat"><strong>{r["high_rated"]:.0f}%</strong> high-rated</div>'
                    f'<div class="tm-topic-stat"><strong>{r["avg_popularity"]:.1f}</strong> popularity</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

        with more("full topic table"):
            table(tt.round(3).rename(columns={"high_rated": "high_rated_%"}))

        best = tt.loc[tt["avg_rating"].idxmax()]; worst = tt.loc[tt["avg_rating"].idxmin()]
        st.caption(f"Highest rated topic: {best['topic_name']} ({best['avg_rating']:.2f}). Lowest: {worst['topic_name']} "
                   f"({worst['avg_rating']:.2f}). Rating differences between topics are small, so describe them as tendencies.")

        st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

        # ---- Word associations ----
        ge2 = ft.explode("genres").reset_index(drop=True)

        tw = read("text/terms_association.csv")
        if need(tw, "data/text/terms_association.csv", nb):
            st.markdown(
                '<div class="tm-section-header">'
                '<div class="tm-icon" style="background:rgba(46,158,107,0.12); font-weight:700; color:var(--navy); font-size:0.85rem;">02</div>'
                '<h3>Word associations</h3></div>', unsafe_allow_html=True)
            st.caption("Words that appear significantly more often in high-rated vs low-rated movie overviews (chi-square, Bonferroni corrected).")
            sg = tw[tw["significant"]]
            n = st.slider("Words per side", 5, 20, 12)
            pk = pd.concat([sg.nlargest(n, "diff"), sg.nsmallest(n, "diff")]).drop_duplicates("term").sort_values("diff")
            if pk.empty: st.info("No significant words found.")
            else:
                fig = px.bar(pk, x=pk["diff"] * 100, y="term", orientation="h", color="direction",
                             color_discrete_map={"high-rated": GREEN, "low-rated": RED},
                             title="Words linked to high-rated (right) vs low-rated (left) movies",
                             labels={"x": "Difference in share of movies (percentage points)", "term": ""})
                show(fig)

        st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

        # ---- Key Text Insights (Topic & Sentiment) ----
        st.markdown(
            '<div class="tm-section-header">'
            '<div class="tm-icon" style="background:rgba(138,99,210,0.12); font-weight:700; color:var(--navy); font-size:0.85rem;">03</div>'
            '<h3>Topic & sentiment insights</h3></div>', unsafe_allow_html=True)

        with more("genre-by-topic distribution heatmap"):
            top8 = ge2["genres"].value_counts().head(8).index
            sub = ge2[ge2["genres"].isin(top8)]
            hm = pd.crosstab(sub["genres"], sub["topic_name"], normalize="index")
            fig = px.imshow(hm.round(2), text_auto=True, color_continuous_scale="YlOrRd", aspect="auto",
                            title="Share of each genre\'s movies by topic", labels={"x": "Topic", "y": "Genre", "color": "Share"})
            show(fig)
            st.caption("Confirms how unsupervised LDA topics map directly to standard movie genres.")

        with more("sentiment of plot summaries by rating"):
            sr = ft.assign(group=np.where(ft["high_rated"] == 1, "High-rated", "Low-rated")).groupby("group")[["polarity", "subjectivity"]].mean().reset_index()
            fig = px.bar(sr.melt("group"), x="group", y="value", color="variable", barmode="group",
                         title="Polarity and subjectivity by rating group", labels={"value": "Average score", "group": "", "variable": ""})
            show(fig)
            rr = ft[["polarity", "vote_average"]].corr(method="spearman").iloc[0, 1]
            st.caption(f"Polarity vs rating (Spearman correlation): r = {rr:.3f}. "
                       "Overview sentiment does not drive or predict audience rating; it only reflects summary tone.")

        st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

        # ---- Movie explorer (with weighted rating fix) ----
        st.markdown(
            '<div class="tm-section-header">'
            '<div class="tm-icon" style="background:rgba(242,142,43,0.12); font-weight:700; color:var(--navy); font-size:0.85rem;">04</div>'
            '<h3>Movie explorer</h3></div>', unsafe_allow_html=True)

        # Rating adjustment for credibility based on vote count
        m_votes = ft["vote_count"].quantile(0.70)
        C_mean = ft["vote_average"].mean()
        ft_ex = ft.copy()
        ft_ex["rating"] = (
            (ft_ex["vote_count"] / (ft_ex["vote_count"] + m_votes)) * ft_ex["vote_average"]
            + (m_votes / (ft_ex["vote_count"] + m_votes)) * C_mean
        )

        q = st.text_input("Search title or overview", placeholder="e.g. Spirited Away, war, family...")
        sc1, sc2 = st.columns([2, 2])
        with sc1:
            topic_opts = ["All topics"] + sorted([str(t) for t in ft_ex["topic_name"].dropna().unique()])
            sel_topic = st.selectbox("Filter by topic", topic_opts)
        with sc2:
            sort_by = st.selectbox("Sort by", ["Rating", "Raw vote average", "Vote count", "Popularity", "Release year"],
                                   help="Rating adjusts for vote volume so titles with very few votes don't dominate the top rankings.")
        sort_map = {"Rating": "rating", "Raw vote average": "vote_average",
                    "Vote count": "vote_count", "Popularity": "popularity", "Release year": "release_year"}

        ex = ft_ex.assign(genres=ft_ex["genres"].apply(", ".join))
        if sel_topic != "All topics":
            ex = ex[ex["topic_name"] == sel_topic]
        if q: ex = ex[ex["title"].str.contains(q, case=False, na=False) | ex["overview"].str.contains(q, case=False, na=False)]
        ex = ex[["title", "release_year", "genres", "topic_name", "polarity",
                 "rating", "vote_average", "vote_count", "overview"]]
        ex = ex.sort_values(sort_map[sort_by], ascending=False)

        st.caption(f"{len(ex):,} movies · showing top 300 · sorted by {sort_by.lower()}")
        table(ex.head(300).round(3))
        st.download_button("Download the filtered movies (CSV)", ex.to_csv(index=False).encode("utf-8"), "filtered_movies.csv", "text/csv")


# ================= 6. Insights =================
with tabs[6]:
    st.subheader("Core Strategic Insights")
    st.caption("Key takeaways mapping directly across our four analytical stages.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '''
            <div class="web-card" style="margin-bottom:0.85rem;">
                <h4>01 · Pre-Release Concept Screening (Predictive ML)</h4>
                <p><strong>Finding:</strong> Content features (genre mix, language, month) classify high-rated titles with <strong>0.785 AUC</strong> before production begins.<br>
                <strong>Action:</strong> Evaluate scripts against genre baselines (Documentary/Animation lead; Horror trails) rather than a single catalogue-wide average.</p>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        st.markdown(
            '''
            <div class="web-card">
                <h4>03 · Market Saturation & Steady Ratings (Time Series)</h4>
                <p><strong>Finding:</strong> Historical ratings stabilized near <strong>6.36</strong> since 2020. Horror (+3.8 pp) and Thriller (+3.3 pp) shares expanded, while Drama contracted (-7.2 pp).<br>
                <strong>Action:</strong> Plan for stable catalogue quality rather than continued growth. Given crowded thriller markets, focus capital on distinct creative execution.</p>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '''
            <div class="web-card" style="margin-bottom:0.85rem;">
                <h4>02 · Reach vs. Quality Reception (EDA)</h4>
                <p><strong>Finding:</strong> Popularity and ratings share a weak correlation (<strong>r = 0.16</strong>). High commercial buzz does not guarantee audience acclaim.<br>
                <strong>Action:</strong> Treat reach and quality as separate investment KPIs. Adding early post-release vote engagement raises predictive AUC to <strong>0.836</strong>.</p>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        st.markdown(
            '''
            <div class="web-card">
                <h4>04 · Narrative Vocabulary & Tropes (Text Mining)</h4>
                <p><strong>Finding:</strong> Factual, historical plot terms (<em>documentary, war, history</em>) associate with higher ratings, while formulaic tropes (<em>killer, serial, boyfriend</em>) associate with lower ratings.<br>
                <strong>Action:</strong> Use plot vocabulary screening to flag formulaic fatigue during early pitch deck reviews.</p>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="tm-divider" style="margin:1.6rem 0 1.2rem;">', unsafe_allow_html=True)

    # Project Summary & Limitations
    st.subheader("Project Summary & Future Scope")
    ccol1, ccol2, ccol3 = st.columns(3)
    with ccol1:
        st.markdown(
            '''
            <div class="web-card">
                <h4>Core Conclusions</h4>
                <p>• Genre is the single strongest pre-release signal.<br>
                • Macro ratings have plateaued at ~6.3 since 2020.<br>
                • Random Forest Set A (AUC 0.785) provides effective screening.<br>
                • Plot vocabulary acts as a reliable qualitative check.</p>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with ccol2:
        st.markdown(
            '''
            <div class="web-card">
                <h4>Methodological Limitations</h4>
                <p>• TMDB sample (~600 titles/year); not a complete census.<br>
                • Recent 12 months excluded due to vote maturation lag.<br>
                • TextBlob measures plot tone, not audience sentiment.<br>
                • Content-only model recall is 0.527.</p>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with ccol3:
        st.markdown(
            '''
            <div class="web-card">
                <h4>Future Scope</h4>
                <p>• Ingest budget, marketing spend, and box office revenue.<br>
                • Incorporate director and lead cast star-power weights.<br>
                • Upgrade from TextBlob to transformer sentence embeddings.<br>
                • Deploy automated periodic API ingestion via cloud CI/CD.</p>
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown('<div style="margin-top:1.8rem;"></div>', unsafe_allow_html=True)
    with st.expander("Project details & contributors"):
        st.caption("Course: 23CSE452 Business Analytics · Faculty Guide: Prof. Rohini S")
        st.markdown(
            '''
            <div style="display:flex; flex-wrap:wrap; gap:0.65rem; margin-top:0.4rem;">
                <div style="background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:0.5rem 0.85rem;">
                    <strong style="color:var(--ink); font-size:0.88rem;">Soundarya Satalgoan</strong>
                    <span style="color:var(--muted); font-size:0.78rem; margin-left:0.35rem;">CB.SC.U4CSE23447</span>
                </div>
                <div style="background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:0.5rem 0.85rem;">
                    <strong style="color:var(--ink); font-size:0.88rem;">Balaji N</strong>
                    <span style="color:var(--muted); font-size:0.78rem; margin-left:0.35rem;">CB.SC.U4CSE23011</span>
                </div>
                <div style="background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:0.5rem 0.85rem;">
                    <strong style="color:var(--ink); font-size:0.88rem;">Parvathy Krishna A</strong>
                    <span style="color:var(--muted); font-size:0.78rem; margin-left:0.35rem;">CB.SC.U4CSE23739</span>
                </div>
                <div style="background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:0.5rem 0.85rem;">
                    <strong style="color:var(--ink); font-size:0.88rem;">Venkata Kanna Bhavan Surya Addap</strong>
                    <span style="color:var(--muted); font-size:0.78rem; margin-left:0.35rem;">CB.SC.U4CSE23467</span>
                </div>
                <div style="background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:0.5rem 0.85rem;">
                    <strong style="color:var(--ink); font-size:0.88rem;">Dareddy Tejeswara Reddy</strong>
                    <span style="color:var(--muted); font-size:0.78rem; margin-left:0.35rem;">CB.SC.U4CSE23614</span>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
