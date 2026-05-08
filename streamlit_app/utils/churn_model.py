"""
Random Forest churn classifier — pure function, no Streamlit dependency.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, recall_score, accuracy_score
from sklearn.preprocessing import LabelEncoder

FEATURES = [
    "avg_monthly_volume_k",
    "monthly_txn_count",
    "avg_txn_size",
    "dispute_rate_pct",
    "support_tickets_monthly",
    "volume_trend_pct",
    "years_on_visa",
    "integration_encoded",
    "category_encoded",
    "region_encoded",
]

FRIENDLY_NAMES = {
    "avg_monthly_volume_k": "Avg Monthly Volume ($K)",
    "monthly_txn_count": "Monthly Transaction Count",
    "avg_txn_size": "Avg Transaction Size ($)",
    "dispute_rate_pct": "Dispute Rate (%)",
    "support_tickets_monthly": "Support Tickets / Month",
    "volume_trend_pct": "Volume Trend (YoY %)",
    "years_on_visa": "Years on Visa",
    "integration_encoded": "Integration Type",
    "category_encoded": "Merchant Category",
    "region_encoded": "Region",
}


def _encode(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col, src in [
        ("integration_encoded", "integration_type"),
        ("category_encoded", "category"),
        ("region_encoded", "region"),
    ]:
        le = LabelEncoder()
        out[col] = le.fit_transform(out[src].astype(str))
    return out


def train_churn_model(df: pd.DataFrame, random_state: int = 42):
    """
    Returns (model, X_train, X_test, y_test, feature_names, metrics).
    """
    df_enc = _encode(df)
    X = df_enc[FEATURES].values
    y = df_enc["churn_label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=random_state, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200, max_depth=8, random_state=random_state, n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "auc": round(roc_auc_score(y_test, y_prob), 3),
        "accuracy": round(accuracy_score(y_test, y_pred), 3),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 3),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 3),
    }

    return model, X_train, X_test, y_test, FEATURES, metrics


def predict_merchant_churn(model, merchant: dict) -> dict:
    """
    Score a single merchant dict. Returns probability and risk tier.
    """
    integration_map = {"Integrated": 0, "Manual": 1, "Semi-integrated": 2}
    category_map = {"Entertainment": 0, "Restaurant": 1, "Retail": 2, "Services": 3, "Travel": 4, "eCommerce": 5}
    region_map = {"Asia Pacific": 0, "Europe": 1, "LAC": 2, "MEA": 3, "North America": 4}

    row = np.array([[
        merchant.get("avg_monthly_volume_k", 500),
        merchant.get("monthly_txn_count", 5000),
        merchant.get("avg_txn_size", 100),
        merchant.get("dispute_rate_pct", 0.5),
        merchant.get("support_tickets_monthly", 2),
        merchant.get("volume_trend_pct", 5),
        merchant.get("years_on_visa", 3),
        integration_map.get(merchant.get("integration_type", "Integrated"), 0),
        category_map.get(merchant.get("category", "Retail"), 2),
        region_map.get(merchant.get("region", "North America"), 4),
    ]])

    prob = float(model.predict_proba(row)[0, 1])
    tier = "High Risk" if prob > 0.6 else "Medium Risk" if prob > 0.35 else "Low Risk"
    return {"churn_probability": prob, "risk_tier": tier}
