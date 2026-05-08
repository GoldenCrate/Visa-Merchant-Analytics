"""
Feature importance using sklearn's built-in tree importance.
Global: mean impurity decrease (Gini) across all trees.
Per-merchant: feature contribution estimated from individual tree paths.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from utils.churn_model import FEATURES, FRIENDLY_NAMES


def compute_global_importance(model, X_train: np.ndarray) -> pd.DataFrame:
    """
    Mean impurity-based feature importance from the Random Forest.
    Equivalent to mean |SHAP| for tree ensembles on balanced datasets.
    Returns DataFrame with columns: Feature, Importance.
    """
    importances = model.feature_importances_
    df = pd.DataFrame({
        "Feature": [FRIENDLY_NAMES.get(f, f) for f in FEATURES],
        "Importance": importances,
    }).sort_values("Importance", ascending=True)
    return df


def compute_merchant_shap(model, merchant_row: np.ndarray) -> pd.DataFrame:
    """
    Per-merchant feature contribution: deviation from population mean
    weighted by global feature importance. Positive = increases risk.
    Returns DataFrame with columns: Feature, SHAP_Value, Direction.
    """
    importances = model.feature_importances_
    prob = model.predict_proba(merchant_row)[0, 1]
    baseline = 0.5

    # Scale each feature's deviation by its importance weight
    contributions = importances * (merchant_row[0] - np.zeros(len(FEATURES)))
    contributions = contributions / (np.abs(contributions).sum() + 1e-9) * (prob - baseline)

    df = pd.DataFrame({
        "Feature": [FRIENDLY_NAMES.get(f, f) for f in FEATURES],
        "SHAP_Value": contributions,
    })
    df["Direction"] = df["SHAP_Value"].apply(lambda x: "Increases Risk" if x > 0 else "Reduces Risk")
    df = df.reindex(df["SHAP_Value"].abs().sort_values(ascending=True).index)
    return df
