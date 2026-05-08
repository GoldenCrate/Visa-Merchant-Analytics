"""
Model monitoring utilities — drift simulation and data quality checks.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


def simulate_model_drift(model, X_test: np.ndarray, y_test: np.ndarray, n_periods: int = 12, rng_seed: int = 42) -> pd.DataFrame:
    """
    Simulates monthly AUC decay: concept drift degrades performance over time.
    Returns DataFrame with columns: Month, AUC, Drift_Flagged.
    """
    rng = np.random.default_rng(rng_seed)
    records = []
    base_prob = model.predict_proba(X_test)[:, 1]
    base_auc = roc_auc_score(y_test, base_prob)

    for month in range(1, n_periods + 1):
        # Inject increasing noise to simulate distribution shift
        noise_scale = 0.02 * (month - 1)
        noisy_prob = (base_prob + rng.normal(0, noise_scale, size=len(base_prob))).clip(0, 1)
        auc = roc_auc_score(y_test, noisy_prob)
        records.append({
            "Month": month,
            "AUC": round(auc, 4),
            "Drift_Flagged": auc < (base_auc - 0.03),
        })

    return pd.DataFrame(records)


def check_data_quality(df: pd.DataFrame) -> dict:
    """
    Runs lightweight data quality checks on the merchant DataFrame.
    Returns a summary dict with per-column and overall quality scores.
    """
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    total_cells = len(df) * len(numeric_cols)
    missing_count = df[numeric_cols].isna().sum().sum()
    missing_pct = missing_count / total_cells if total_cells > 0 else 0

    outlier_count = 0
    for col in numeric_cols:
        s = df[col].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        outlier_count += int(((s < q1 - 3 * iqr) | (s > q3 + 3 * iqr)).sum())

    quality_score = max(0, 100 - missing_pct * 200 - outlier_count / len(df) * 10)

    col_quality = []
    for col in numeric_cols:
        s = df[col].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        col_outliers = int(((s < q1 - 3 * iqr) | (s > q3 + 3 * iqr)).sum())
        col_missing = int(df[col].isna().sum())
        col_quality.append({
            "Column": col,
            "Missing": col_missing,
            "Outliers": col_outliers,
            "Status": "OK" if col_missing == 0 and col_outliers < 10 else "Warning",
        })

    return {
        "missing_pct": round(missing_pct * 100, 2),
        "outlier_count": outlier_count,
        "quality_score": round(quality_score, 1),
        "col_quality": pd.DataFrame(col_quality),
    }
