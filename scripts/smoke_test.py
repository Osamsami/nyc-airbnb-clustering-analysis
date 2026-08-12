"""Smoke test for the NYC Airbnb clustering pipeline.

Re-runs the core clustering steps from Notebooks/notebooks_03_clustering.ipynb
against data/airbnb_cleaned.csv and asserts the pipeline still produces a
sane K=4 clustering solution. Used by CI to catch broken data/paths/deps
without needing to execute the full notebook.
"""

import sys
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "airbnb_cleaned.csv"
CLUSTERED_DATA_PATH = REPO_ROOT / "data" / "airbnb_with_clusters.csv"

FEATURES = [
    "log_price",
    "minimum_nights",
    "number_of_reviews",
    "reviews_per_month",
    "availability_365",
    "calculated_host_listings_count",
    "neighbourhood_group",
    "room_type",
]


def main() -> None:
    print(f"Loading dataset from {DATA_PATH} ...")
    assert DATA_PATH.exists(), f"Missing dataset: {DATA_PATH}"
    df = pd.read_csv(DATA_PATH)
    assert len(df) > 0, "Dataset is empty"
    for col in FEATURES:
        assert col in df.columns, f"Expected column '{col}' missing from dataset"

    df_cluster = df[FEATURES].copy()
    le = LabelEncoder()
    df_cluster["neighbourhood_group"] = le.fit_transform(df_cluster["neighbourhood_group"])
    df_cluster["room_type"] = le.fit_transform(df_cluster["room_type"])

    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_cluster)

    k = 4
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(df_scaled)
    score = silhouette_score(df_scaled, labels)

    print(f"K={k} silhouette score: {score:.4f}")
    assert len(set(labels)) == k, "Expected exactly K clusters to be produced"
    assert 0.0 < score < 1.0, "Silhouette score out of expected range"
    # The notebook reports ~0.262 for K=4; allow a generous tolerance since
    # KMeans initialisation can shift the score slightly across sklearn versions.
    assert score > 0.15, f"Silhouette score {score:.4f} is lower than expected (>0.15)"

    if CLUSTERED_DATA_PATH.exists():
        clustered = pd.read_csv(CLUSTERED_DATA_PATH)
        assert "cluster" in clustered.columns, "Precomputed cluster file missing 'cluster' column"
        assert clustered["cluster"].nunique() == k, "Precomputed cluster file has unexpected cluster count"

    print("Smoke test passed.")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"Smoke test FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
