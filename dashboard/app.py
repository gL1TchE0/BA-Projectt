"""TMDB Movie Analytics dashboard (Review 2).
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

st.set_page_config(page_title="TMDB Movie Analytics", page_icon="🎬", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
HIGH = 6.5                                   # a movie is "high-rated" at this rating or above
BLUE, ORANGE, GREEN, RED, GREY = "#1f4e79", "#f28e2b", "#2e9e6b", "#d1495b", "#9aa5b1"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

if "theme" not in st.session_state:
    st.session_state.theme = "Light"
theme = st.sidebar.radio("Appearance", ["Light", "Dark"], horizontal=True, key="theme")
dark_mode = theme == "Dark"
theme_values = {
    "app_bg": "#101722" if dark_mode else "#f7f9fc",
    "app_gradient_end": "#172131" if dark_mode else "#ffffff",
    "header_bg": "rgba(16, 23, 34, 0.86)" if dark_mode else "rgba(247, 249, 252, 0.86)",
    "ink": "#f2f5f8" if dark_mode else "#172033",
    "muted": "#aab6c5" if dark_mode else "#667085",
    "navy": "#a9d4f5" if dark_mode else "#193b63",
    "sky": "#1c344c" if dark_mode else "#eaf3fb",
    "line": "#2c3a4d" if dark_mode else "#e5eaf1",
    "surface": "#182333" if dark_mode else "#ffffff",
    "sidebar_start": "#152437" if dark_mode else "#f1f6fb",
    "sidebar_end": "#101722" if dark_mode else "#ffffff",
    "plot": "#182333" if dark_mode else "#ffffff",
}
if dark_mode:
    BLUE = "#72b7e8"

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

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1.05rem 1.15rem;
        box-shadow: 0 8px 24px rgba(25, 59, 99, 0.06);
    }
    [data-testid="stMetricLabel"] { color: var(--muted); font-size: 0.78rem; font-weight: 600; }
    [data-testid="stMetricValue"] { color: var(--navy); font-size: 1.65rem; }

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
        font-size: 1.02rem;
        font-weight: 700;
    }
    .insight-copy {
        margin: 0;
        color: var(--muted);
        line-height: 1.55;
        font-size: 0.92rem;
    }
    .insight-label {
        color: var(--ink);
        font-size: 0.78rem;
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
        font-size: 0.78rem;
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
    ("Plan by genre expectations",
     "Documentary, Animation, History and Music movies are rated highest on average, Horror and Thriller lowest. "
     "Judge a title against its own genre's usual rating, not against the whole catalogue."),
    ("Do not read popularity as quality",
     "Popularity and rating are only weakly related (correlation about 0.16). Popularity shows reach, so use ratings "
     "and vote counts together when deciding what to keep or promote."),
    ("Use content to screen ideas before release",
     "A model using only content (genre, language, year, text length) reaches AUC 0.785 against 0.50 for guessing. "
     "It is a useful first filter, but it misses about half of the eventually high-rated movies, so use it as one input."),
    ("Track early audience engagement after release",
     "Adding popularity and vote count lifts the model to AUC 0.836. Monitor early votes to update expectations."),
    ("Look at non-English catalogue",
     "Japanese and Korean movies that reach 20 votes average higher ratings. They are a self-selected group, so test "
     "this with your own audience data before acting on it."),
    ("Expect stable ratings and a crowded horror and thriller market",
     "Average rating was flat at about 6.06 until 2019 and has sat near 6.3 since 2020. The forecast stays around 6.4 "
     "with a wide band, so plan for a steady level, not further growth. Release month matters little (seasonal strength 0.07). "
     "Horror and Thriller gained 3.8 and 3.3 points of genre share since the early 2000s while Drama lost 7.2, and these two "
     "genres have the lowest average ratings, so they need clear quality differentiation."),
    ("Use plot wording as an early quality signal",
     "Plot summaries of high-rated movies lean on factual and historical words (documentary, war, history, music, journey), "
     "while low-rated ones lean on formulaic crime and romance words (killer, evil, boyfriend, Christmas). The topic model finds "
     "four broad themes: youth and war, love and family, work and power, and crime and murder. Use theme and wording to check a "
     "pitch against how similar plots have been rated, and treat the differences as tendencies, not rules."),
    ("[Add a recommendation from the text-mining topics]", "Edit RECS at the top of dashboard/app.py."),
]

# ---- Review 1 results (static, taken from the notebook) ----
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
    ("🎬", "Choosing a movie", "#2e9e6b", "rgba(46, 158, 107, 0.14)"),
    ("📣", "Popularity vs quality", "#f28e2b", "rgba(242, 142, 43, 0.15)"),
    ("🔎", "Before release", "#1f80c0", "rgba(31, 128, 192, 0.14)"),
    ("📈", "After release", "#8a63d2", "rgba(138, 99, 210, 0.14)"),
    ("🌍", "Global audiences", "#d1495b", "rgba(209, 73, 91, 0.14)"),
    ("🗓️", "Planning ahead", "#1f4e79", "rgba(31, 78, 121, 0.14)"),
    ("📝", "Understanding stories", "#2e9e6b", "rgba(46, 158, 107, 0.14)"),
    ("💡", "Next step", "#667085", "rgba(102, 112, 133, 0.14)"),
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
tabs = st.tabs(["Overview", "EDA", "Time series", "Text mining", "Model results", "Insights"])

# ================= 1. Overview =================
with tabs[0]:
    if not need(clean, "data/processed/tmdb_clean.csv", "Review1_TMDB_Final.ipynb"): pass
    elif f.empty: st.warning("No movies match the current filters.")
    else:
        k = st.columns(5)
        k[0].metric("Movies", f"{len(f):,}")
        k[1].metric("Average rating", f"{f['vote_average'].mean():.2f}")
        k[2].metric("High-rated share", f"{f['high_rated'].mean():.0%}")
        k[3].metric("Average popularity", f"{f['popularity'].mean():.2f}")
        k[4].metric("Years covered", f"{f['release_year'].min()} to {f['release_year'].max()}")
        g = f.explode("genres")
        gs = g.groupby("genres").agg(movies=("id", "size"), rating=("vote_average", "mean")).reset_index()
        c1, c2 = st.columns(2)
        with c1:
            ya = f.groupby("release_year")["vote_average"].mean().reset_index()
            fig = px.line(ya, x="release_year", y="vote_average", markers=True, title="Average rating by release year",
                          labels={"release_year": "Year", "vote_average": "Average rating"}, color_discrete_sequence=[BLUE])
            show(fig)
        with c2:
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
with tabs[1]:
    if not need(clean, "data/processed/tmdb_clean.csv", "Review1_TMDB_Final.ipynb"): pass
    elif f.empty: st.warning("No movies match the current filters.")
    else:
        g = f.explode("genres")
        gs = g.groupby("genres").agg(movies=("id", "size"), rating=("vote_average", "mean"),
                                     pop=("popularity", "mean")).query("movies >= 30").reset_index()
        metric = st.radio("Compare genres by", ["Average rating", "Average popularity"], horizontal=True)
        mcol, mcolor = ("rating", ORANGE) if metric == "Average rating" else ("pop", GREEN)
        fig = px.bar(gs.sort_values(mcol), x=mcol, y="genres", orientation="h", color_discrete_sequence=[mcolor],
                     title=f"{metric} by genre", labels={mcol: metric, "genres": ""}, hover_data={"movies": True})
        show(fig)
        if len(gs) > 1:
            hi_, lo_ = gs.loc[gs["rating"].idxmax()], gs.loc[gs["rating"].idxmin()]
            st.caption(f"Highest rated genre: {hi_['genres']} ({hi_['rating']:.2f}). Lowest: {lo_['genres']} ({lo_['rating']:.2f}). "
                       "Genres with fewer than 30 movies are hidden.")
        with more("rating by language and by decade"):
            c3, c4 = st.columns(2)
            with c3:
                ls = (f.groupby("original_language").agg(movies=("id", "size"), rating=("vote_average", "mean"))
                        .sort_values("movies", ascending=False).head(10).reset_index().sort_values("rating"))
                fig = px.bar(ls, x="rating", y="original_language", orientation="h", color_discrete_sequence=[BLUE],
                             title="Average rating by language (10 most common)", hover_data={"movies": True},
                             labels={"rating": "Average rating", "original_language": "Language"})
                show(fig)
            with c4:
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
            st.caption(f"Spearman correlation with rating: popularity {r.loc['vote_average', 'popularity']:.2f}, "
                       f"vote count {r.loc['vote_average', 'vote_count']:.2f}. Both are weak.")

# ================= 3. Time series =================
with tabs[2]:
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
            sty = mc.style.highlight_min(subset=["RMSE"], color="#c8e6c9").format(
                {c: "{:.4f}" for c in ["MAE", "RMSE"]} | ({"RMSE vs naive (%)": "{:+.1f}"} if "RMSE vs naive (%)" in mc else {}))
            table(sty)
            best = mc.loc[mc["RMSE"].idxmin(), "model"]
            st.caption(f"Best model on the test months: {best}." + (" No model beat the naive baseline, so the series has little "
                       "predictable structure beyond its recent level." if str(best).startswith("Naive") else ""))
        with more("seasonality and change in genre share"):
            c1, c2 = st.columns(2)
            with c1:
                if need(se, "data/ts/seasonality.csv", nb):
                    se = se.assign(m=lambda d: d["month_of_year"].map(lambda i: MONTHS[int(i) - 1]))
                    fig = px.bar(se, x="m", y="avg_rating", color_discrete_sequence=[GREEN], title="Average rating by release month",
                                 labels={"m": "Month", "avg_rating": "Average rating"})
                    fig.update_yaxes(range=[se["avg_rating"].min() - 0.1, se["avg_rating"].max() + 0.1])
                    show(fig)
                    st.caption(f"Highest in {se.loc[se['avg_rating'].idxmax(), 'm']}, lowest in {se.loc[se['avg_rating'].idxmin(), 'm']}; "
                               f"the whole range is only {se['avg_rating'].max() - se['avg_rating'].min():.2f} rating points.")
            with c2:
                if need(gc, "data/ts/genre_share_change.csv", nb):
                    cc = gc.columns[1]
                    fig = px.bar(gc.sort_values(cc), x=cc, y="genre", orientation="h", title="Change in genre share (percentage points)",
                                 color=gc.sort_values(cc)[cc] > 0, color_discrete_map={True: GREEN, False: RED},
                                 labels={cc: "Change (pp)", "genre": ""})
                    fig.update_layout(showlegend=False); show(fig)
                    st.caption(f"Biggest rise: {gc.loc[gc[cc].idxmax(), 'genre']} ({gc[cc].max():+.1f} pp). "
                               f"Biggest fall: {gc.loc[gc[cc].idxmin(), 'genre']} ({gc[cc].min():+.1f} pp), "
                               "first five years vs last five modelled years.")

# ================= 4. Text mining =================
with tabs[3]:
    nb = "Text_Mining_Revised.ipynb"
    if not need(text, "data/text/text_movie_level.csv", nb): pass
    elif ft.empty: st.warning("No movies match the current filters (text mining uses movies with 20 or more votes).")
    else:
        st.caption(f"{len(ft):,} movies selected. Topics come from LDA on the plot overviews.")
        tsum = read("text/topics_summary.csv")
        tt = ft.groupby(["topic", "topic_name"]).agg(movies=("id", "size"), avg_rating=("vote_average", "mean"),
                                                     high_rated=("high_rated", "mean"), avg_popularity=("popularity", "mean")).reset_index()
        if tsum is not None: tt = tt.merge(tsum[["topic", "top_words", "coherence"]], on="topic", how="left")
        tt["high_rated"] = (tt["high_rated"] * 100).round(1)
        st.subheader("Topics")
        table(tt.round(3).rename(columns={"high_rated": "high_rated_%"}))
        best = tt.loc[tt["avg_rating"].idxmax()]; worst = tt.loc[tt["avg_rating"].idxmin()]
        st.caption(f"Highest rated topic: {best['topic_name']} ({best['avg_rating']:.2f}). Lowest: {worst['topic_name']} "
                   f"({worst['avg_rating']:.2f}). Rating differences between topics are small, so describe them as tendencies.")

        ge2 = ft.explode("genres").reset_index(drop=True)

        tw = read("text/terms_association.csv")
        if need(tw, "data/text/terms_association.csv", nb):
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
                st.caption("Significant words only (chi-square with Bonferroni correction). Not affected by the sidebar filters.")

        with more("topic share by year and genre-by-topic heatmap"):
            c1, c2 = st.columns(2)
            with c1:
                ty = pd.crosstab(ft["release_year"], ft["topic_name"], normalize="index").reset_index().melt("release_year", value_name="share")
                fig = px.area(ty, x="release_year", y="share", color="topic_name", title="Topic share by release year",
                              labels={"release_year": "Year", "share": "Share of movies", "topic_name": "Topic"})
                show(fig)
            with c2:
                top8 = ge2["genres"].value_counts().head(8).index
                sub = ge2[ge2["genres"].isin(top8)]
                hm = pd.crosstab(sub["genres"], sub["topic_name"], normalize="index")
                fig = px.imshow(hm.round(2), text_auto=True, color_continuous_scale="YlOrRd", aspect="auto",
                                title="Share of each genre's movies by topic", labels={"x": "Topic", "y": "Genre", "color": "Share"})
                show(fig)

        with more("sentiment of plot summaries"):
            s1, s2, s3 = st.columns(3)
            with s1:
                sg_ = ge2.groupby("genres").agg(movies=("id", "size"), polarity=("polarity", "mean")).query("movies >= 30")
                fig = px.bar(sg_.sort_values("polarity").tail(10).reset_index(), x="polarity", y="genres", orientation="h",
                             color_discrete_sequence=[BLUE], title="Average polarity by genre", labels={"polarity": "Polarity", "genres": ""})
                show(fig)
            with s2:
                sy = ft.groupby("release_year")["polarity"].mean().reset_index()
                fig = px.line(sy, x="release_year", y="polarity", title="Average polarity by year", color_discrete_sequence=[ORANGE],
                              labels={"release_year": "Year", "polarity": "Polarity"})
                show(fig)
            with s3:
                sr = ft.assign(group=np.where(ft["high_rated"] == 1, "High-rated", "Low-rated")).groupby("group")[["polarity", "subjectivity"]].mean().reset_index()
                fig = px.bar(sr.melt("group"), x="group", y="value", color="variable", barmode="group",
                             title="Polarity and subjectivity by rating group", labels={"value": "Average score", "group": "", "variable": ""})
                show(fig)
            rr = ft[["polarity", "vote_average"]].corr(method="spearman").iloc[0, 1]
            st.caption(f"Polarity vs rating (Spearman): {rr:.3f}. Sentiment of the plot summary says very little about the rating. "
                       "It is the tone of the description, not audience opinion.")

        st.subheader("Movie explorer")
        q = st.text_input("Search title or overview")
        ex = ft.assign(genres=ft["genres"].apply(", ".join))
        if q: ex = ex[ex["title"].str.contains(q, case=False, na=False) | ex["overview"].str.contains(q, case=False, na=False)]
        ex = ex[["title", "release_year", "genres", "topic_name", "polarity", "vote_average", "vote_count", "overview"]]
        ex = ex.sort_values("vote_average", ascending=False)
        st.write(f"{len(ex):,} movies (showing the top 300 by rating)")
        table(ex.head(300).round(3))
        st.download_button("Download the filtered movies (CSV)", ex.to_csv(index=False).encode("utf-8"), "filtered_movies.csv", "text/csv")

# ================= 5. Model results =================
with tabs[4]:
    st.subheader("Predicting high-rated movies (Review 1)")
    st.caption(f"Target: rating of {HIGH} or more, for movies with 20 or more votes (10,078 movies, 39% high-rated). "
               "Stratified 80/20 split: 8,062 training and 2,016 test movies. Results are on the test set.")
    table(METRICS.style.format({c: "{:.3f}" for c in METRICS.columns[1:]}))
    c1, c2 = st.columns(2)
    with c1:
        cm = pd.DataFrame([[1077, 153], [334, 452]], index=["Actual: not high", "Actual: high"], columns=["Predicted: not high", "Predicted: high"])
        fig = px.imshow(cm, text_auto=True, color_continuous_scale="Blues", title="Confusion matrix, Random Forest set B")
        show(fig)
    with c2:
        st.markdown("**Robustness:** with at least 50 votes (5,717 movies) the AUC is 0.841, so the results do not depend on the 20-vote cut-off.")
        st.info("Set B uses popularity and votes, which are known only after release, so it explains ratings but cannot forecast a new film. "
                "Set A is the pre-release version. Importance shows what the model uses, not cause and effect.")
    with more("cross-validation AUC before and after tuning"):
        table(CV)
    with more("top 15 features for set A and set B"):
        c3, c4 = st.columns(2)
        for col, name, imp, colr in [(c3, "Set B (with popularity and votes)", IMP_B, BLUE), (c4, "Set A (content only)", IMP_A, ORANGE)]:
            with col:
                d = pd.Series(imp).sort_values().reset_index(); d.columns = ["feature", "importance"]
                fig = px.bar(d, x="importance", y="feature", orientation="h", color_discrete_sequence=[colr],
                             title=f"Top 15 features, {name}", labels={"importance": "Drop in AUC when shuffled", "feature": ""})
                show(fig)

# ================= 6. Insights =================
with tabs[5]:
    st.subheader("The big picture, in plain English")
    st.caption("These are practical takeaways from the movie data. They describe patterns, not guarantees.")
    for i, (h, t) in enumerate(RECS):
        icon, category, accent, icon_bg = INSIGHT_META[i]
        st.markdown(
            f"""
            <div class="insight-card" style="--accent:{accent};--icon-bg:{icon_bg};">
                <div class="insight-topline">
                    <div class="insight-icon">{icon}</div>
                    <div>
                        <div class="insight-category">{html.escape(category)}</div>
                        <p class="insight-title">{html.escape(h)}</p>
                    </div>
                </div>
                <p class="insight-copy"><span class="insight-label">What this means: </span>{html.escape(t)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if clean is not None and f is not None and not f.empty:
        g = f.explode("genres").groupby("genres").agg(movies=("id", "size"), rating=("vote_average", "mean")).query("movies >= 30")
        if len(g) > 1:
            st.subheader("Your selected catalogue at a glance")
            st.caption("These numbers update when you change the filters in the sidebar.")
            s1, s2, s3 = st.columns(3)
            with s1:
                st.markdown(
                    f'<div class="insight-stat"><strong>{g["rating"].idxmax()}</strong><span>Highest-rated genre · {g["rating"].max():.2f} average</span></div>',
                    unsafe_allow_html=True,
                )
            with s2:
                st.markdown(
                    f'<div class="insight-stat"><strong>{g["rating"].idxmin()}</strong><span>Lowest-rated genre · {g["rating"].min():.2f} average</span></div>',
                    unsafe_allow_html=True,
                )
            with s3:
                st.markdown(
                    f'<div class="insight-stat"><strong>{f["high_rated"].mean():.0%}</strong><span>Of {len(f):,} selected movies rated {HIGH}+</span></div>',
                    unsafe_allow_html=True,
                )
    st.caption("Findings are associations in a sample of TMDB movies, not proof of cause.")