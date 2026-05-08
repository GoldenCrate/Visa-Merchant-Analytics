"""
K-Means merchant segmentation — pure function, no Streamlit dependency.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "avg_monthly_volume_k",
    "monthly_txn_count",
    "dispute_rate_pct",
    "support_tickets_monthly",
    "volume_trend_pct",
    "years_on_visa",
]

SEGMENT_NAMES = {
    0: "Champions",
    1: "Growth Stars",
    2: "Stable Partners",
    3: "At-Risk",
}


def _assign_names(df: pd.DataFrame, labels: np.ndarray) -> dict[int, str]:
    """
    Map raw cluster IDs to business names based on centroid traits.
    Champions: highest volume. At-Risk: highest dispute rate.
    Growth Stars: highest volume trend. Stable Partners: remainder.
    """
    centroids = pd.DataFrame({"label": labels})
    centroids["volume"] = df["avg_monthly_volume_k"].values
    centroids["dispute"] = df["dispute_rate_pct"].values
    centroids["trend"] = df["volume_trend_pct"].values

    by_label = centroids.groupby("label").mean()
    champion = int(by_label["volume"].idxmax())
    at_risk = int(by_label["dispute"].idxmax())
    remaining = [i for i in by_label.index if i not in (champion, at_risk)]
    growth = int(by_label.loc[remaining, "trend"].idxmax())
    stable = [i for i in remaining if i != growth][0]

    return {
        champion: "Champions",
        growth: "Growth Stars",
        stable: "Stable Partners",
        at_risk: "At-Risk",
    }


def segment_merchants(df: pd.DataFrame, n_clusters: int = 4, random_state: int = 42) -> pd.DataFrame:
    """
    Returns df with two new columns: Segment_ID (int) and Segment (str).
    """
    X = df[FEATURES].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = km.fit_predict(X_scaled)

    name_map = _assign_names(df, labels)
    out = df.copy()
    out["Segment_ID"] = labels
    out["Segment"] = [name_map[l] for l in labels]
    return out
