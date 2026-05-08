"""
SHAP feature importance — builds Altair-friendly DataFrames from TreeExplainer.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import shap
from utils.churn_model import FEATURES, FRIENDLY_NAMES


def compute_global_importance(model, X_train: np.ndarray) -> pd.DataFrame:
    """
    Mean absolute SHAP values across training set — global feature importance.
    Returns DataFrame with columns: Feature, Importance.
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_train)
    # shap_values is list [class0, class1] for RF classifiers
    sv = shap_values[1] if isinstance(shap_values, list) else shap_values
    mean_abs = np.abs(sv).mean(axis=0)
    df = pd.DataFrame({
        "Feature": [FRIENDLY_NAMES.get(f, f) for f in FEATURES],
        "Importance": mean_abs,
    }).sort_values("Importance", ascending=True)
    return df


def compute_merchant_shap(model, merchant_row: np.ndarray) -> pd.DataFrame:
    """
    Per-merchant SHAP waterfall data.
    merchant_row: shape (1, n_features).
    Returns DataFrame with columns: Feature, SHAP_Value, Direction.
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(merchant_row)
    sv = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]
    df = pd.DataFrame({
        "Feature": [FRIENDLY_NAMES.get(f, f) for f in FEATURES],
        "SHAP_Value": sv,
    })
    df["Direction"] = df["SHAP_Value"].apply(lambda x: "Increases Risk" if x > 0 else "Reduces Risk")
    df = df.reindex(df["SHAP_Value"].abs().sort_values(ascending=True).index)
    return df
