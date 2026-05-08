import numpy as np
import pandas as pd
import pytest
from streamlit_app.utils.segmentation import segment_merchants, FEATURES


@pytest.fixture
def sample_df():
    rng = np.random.default_rng(0)
    n = 200
    return pd.DataFrame({
        "merchant_id": range(n),
        "merchant_name": [f"Merchant {i}" for i in range(n)],
        "category": rng.choice(["Retail", "Restaurant", "eCommerce"], size=n),
        "region": rng.choice(["North America", "Europe"], size=n),
        "integration_type": rng.choice(["Integrated", "Manual", "Semi-integrated"], size=n),
        "years_on_visa": rng.uniform(0.5, 12, size=n),
        "avg_monthly_volume_k": rng.uniform(10, 3000, size=n),
        "monthly_txn_count": rng.integers(100, 40000, size=n),
        "avg_txn_size": rng.uniform(5, 500, size=n),
        "dispute_rate_pct": rng.uniform(0.05, 4.0, size=n),
        "support_tickets_monthly": rng.integers(0, 15, size=n),
        "volume_trend_pct": rng.uniform(-40, 55, size=n),
        "churn_label": rng.integers(0, 2, size=n),
    })


def test_returns_dataframe(sample_df):
    result = segment_merchants(sample_df)
    assert isinstance(result, pd.DataFrame)


def test_adds_segment_columns(sample_df):
    result = segment_merchants(sample_df)
    assert "Segment" in result.columns
    assert "Segment_ID" in result.columns


def test_all_merchants_assigned(sample_df):
    result = segment_merchants(sample_df)
    assert result["Segment"].notna().all()
    assert result["Segment_ID"].notna().all()


def test_correct_number_of_segments(sample_df):
    result = segment_merchants(sample_df)
    assert result["Segment"].nunique() == 4


def test_segment_names_are_valid(sample_df):
    valid_names = {"Champions", "Growth Stars", "Stable Partners", "At-Risk"}
    result = segment_merchants(sample_df)
    assert set(result["Segment"].unique()).issubset(valid_names)


def test_row_count_preserved(sample_df):
    result = segment_merchants(sample_df)
    assert len(result) == len(sample_df)


def test_original_columns_preserved(sample_df):
    original_cols = list(sample_df.columns)
    result = segment_merchants(sample_df)
    for col in original_cols:
        assert col in result.columns


def test_deterministic(sample_df):
    r1 = segment_merchants(sample_df)
    r2 = segment_merchants(sample_df)
    assert list(r1["Segment"]) == list(r2["Segment"])
