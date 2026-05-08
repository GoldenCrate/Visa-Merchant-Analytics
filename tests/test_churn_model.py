import numpy as np
import pandas as pd
import pytest
from streamlit_app.utils.churn_model import train_churn_model, predict_merchant_churn


@pytest.fixture
def sample_df():
    rng = np.random.default_rng(1)
    n = 300
    volume = rng.uniform(10, 3000, size=n)
    txn = rng.integers(100, 40000, size=n)
    dispute = rng.uniform(0.05, 4.0, size=n)
    trend = rng.uniform(-40, 55, size=n)
    tickets = rng.integers(0, 15, size=n)
    score = 0.4 * (dispute / 4.0) + 0.3 * (-trend / 40 + 0.5) + 0.2 * (tickets / 15) + rng.normal(0, 0.1, size=n)
    churn = (score > np.median(score)).astype(int)
    return pd.DataFrame({
        "merchant_id": range(n),
        "merchant_name": [f"Merchant {i}" for i in range(n)],
        "category": rng.choice(["Retail", "Restaurant", "eCommerce", "Travel", "Entertainment", "Services"], size=n),
        "region": rng.choice(["North America", "Europe", "Asia Pacific", "LAC", "MEA"], size=n),
        "integration_type": rng.choice(["Integrated", "Manual", "Semi-integrated"], size=n),
        "years_on_visa": rng.uniform(0.5, 12, size=n),
        "avg_monthly_volume_k": volume,
        "monthly_txn_count": txn,
        "avg_txn_size": (volume * 1000 / txn).round(2),
        "dispute_rate_pct": dispute,
        "support_tickets_monthly": tickets,
        "volume_trend_pct": trend,
        "churn_label": churn,
    })


@pytest.fixture
def trained(sample_df):
    return train_churn_model(sample_df)


def test_returns_five_elements(trained):
    assert len(trained) == 6


def test_model_has_predict_proba(trained):
    model = trained[0]
    assert hasattr(model, "predict_proba")


def test_auc_above_chance(trained):
    metrics = trained[5]
    assert metrics["auc"] > 0.50


def test_accuracy_reasonable(trained):
    metrics = trained[5]
    assert 0.40 < metrics["accuracy"] < 1.0


def test_metrics_keys(trained):
    metrics = trained[5]
    for key in ("auc", "accuracy", "precision", "recall"):
        assert key in metrics


def test_x_test_shape(trained, sample_df):
    _, X_train, X_test, y_test, _, _ = trained
    assert X_test.shape[1] == 10
    assert len(X_test) == len(y_test)


def test_predict_returns_probability(trained):
    model = trained[0]
    result = predict_merchant_churn(model, {
        "avg_monthly_volume_k": 500,
        "monthly_txn_count": 5000,
        "avg_txn_size": 100,
        "dispute_rate_pct": 1.0,
        "support_tickets_monthly": 3,
        "volume_trend_pct": 5.0,
        "years_on_visa": 3.0,
        "integration_type": "Integrated",
        "category": "Retail",
        "region": "North America",
    })
    assert 0.0 <= result["churn_probability"] <= 1.0


def test_predict_returns_risk_tier(trained):
    model = trained[0]
    result = predict_merchant_churn(model, {})
    assert result["risk_tier"] in ("High Risk", "Medium Risk", "Low Risk")


def test_high_dispute_raises_risk(trained):
    model = trained[0]
    low = predict_merchant_churn(model, {"dispute_rate_pct": 0.1, "avg_monthly_volume_k": 1000, "volume_trend_pct": 20})
    high = predict_merchant_churn(model, {"dispute_rate_pct": 4.9, "avg_monthly_volume_k": 1000, "volume_trend_pct": 20})
    assert high["churn_probability"] > low["churn_probability"]


def test_predict_proba_sums_to_one(trained):
    model = trained[0]
    _, _, X_test, _, _, _ = trained
    proba = model.predict_proba(X_test)
    assert np.allclose(proba.sum(axis=1), 1.0)
