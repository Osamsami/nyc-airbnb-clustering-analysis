"""Interactive Streamlit demo for exploring the NYC Airbnb K-Means clusters.

Loads data/airbnb_with_clusters.csv (produced by
notebooks/notebooks_03_clustering.ipynb) and lets the user filter listings
by borough, room type, and price range, then view the resulting cluster
distribution, per-cluster summary stats, and a scatter map of listings
colored by cluster.

Run with: streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent
DATA_PATH = REPO_ROOT / "data" / "airbnb_with_clusters.csv"

# Human-readable labels for each cluster, derived from the profiling done in
# notebooks/notebooks_03_clustering.ipynb and reports/analysis.md.
CLUSTER_LABELS = {
    0: "Mid-Range Mixed",
    1: "High-Value Entire Homes",
    2: "Budget Private Rooms",
    3: "Long-Stay Luxury Apts",
}
CLUSTER_COLORS = {
    0: "#4C72B0",
    1: "#DD8452",
    2: "#55A868",
    3: "#C44E52",
}

st.set_page_config(
    page_title="NYC Airbnb Cluster Explorer",
    page_icon="🗽",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(
            f"Could not find {DATA_PATH}. Run the clustering notebook "
            "(notebooks/notebooks_03_clustering.ipynb) first to generate it."
        )
        st.stop()
    df = pd.read_csv(DATA_PATH)
    df["cluster_label"] = df["cluster"].map(CLUSTER_LABELS).fillna(df["cluster"].astype(str))
    return df


df = load_data()

st.title("NYC Airbnb Cluster Explorer")
st.caption(
    "Explore the four K-Means market segments identified in the NYC Airbnb "
    "2019 listings dataset. Use the filters in the sidebar to narrow down "
    "by borough, room type, and price."
)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

boroughs = sorted(df["neighbourhood_group"].dropna().unique().tolist())
selected_boroughs = st.sidebar.multiselect(
    "Borough", options=boroughs, default=boroughs
)

room_types = sorted(df["room_type"].dropna().unique().tolist())
selected_room_types = st.sidebar.multiselect(
    "Room type", options=room_types, default=room_types
)

price_min, price_max = int(df["price"].min()), int(df["price"].max())
selected_price_range = st.sidebar.slider(
    "Price range ($ / night)",
    min_value=price_min,
    max_value=price_max,
    value=(price_min, min(500, price_max)),
    step=10,
)

st.sidebar.caption(
    f"Full dataset price range: ${price_min}–${price_max}. Defaulting the "
    "upper bound to $500 to avoid a small number of high-price outliers "
    "compressing the slider — drag it up to see the full range."
)

filtered = df[
    df["neighbourhood_group"].isin(selected_boroughs)
    & df["room_type"].isin(selected_room_types)
    & df["price"].between(*selected_price_range)
]

if filtered.empty:
    st.warning("No listings match the current filters. Try widening them.")
    st.stop()

# ---------------------------------------------------------------------------
# Top-line metrics
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Listings shown", f"{len(filtered):,}")
col2.metric("Avg price", f"${filtered['price'].mean():,.0f}")
col3.metric("Median price", f"${filtered['price'].median():,.0f}")
col4.metric("Clusters represented", filtered["cluster"].nunique())

st.divider()

# ---------------------------------------------------------------------------
# Cluster distribution
# ---------------------------------------------------------------------------
st.subheader("Cluster distribution")

cluster_counts = (
    filtered["cluster_label"].value_counts().reindex(
        [CLUSTER_LABELS[c] for c in sorted(CLUSTER_LABELS) if CLUSTER_LABELS[c] in filtered["cluster_label"].unique()]
    )
)
left, right = st.columns([2, 3])
with left:
    st.bar_chart(cluster_counts)
with right:
    summary = (
        filtered.groupby("cluster_label")
        .agg(
            listings=("cluster", "size"),
            avg_price=("price", "mean"),
            median_price=("price", "median"),
            pct_entire_home=("room_type", lambda s: (s == "Entire home/apt").mean() * 100),
            pct_private_room=("room_type", lambda s: (s == "Private room").mean() * 100),
            avg_min_nights=("minimum_nights", "mean"),
        )
        .round(1)
        .sort_values("avg_price")
    )
    st.dataframe(summary, use_container_width=True)
