"""
Generates synthetic merchant transaction dataset (2 000 merchants).
Churn labels are correlated with dispute rate, support tickets,
volume decline, and integration type — realistic enough to train on.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

CATEGORIES = ["Retail", "Restaurant", "eCommerce", "Travel", "Entertainment", "Services"]
REGIONS = ["North America", "Europe", "Asia Pacific", "LAC", "MEA"]
INTEGRATION = ["Integrated", "Semi-integrated", "Manual"]

ADJECTIVES = ["Global", "Prime", "Direct", "Express", "Smart", "Digital", "Swift", "Peak"]
NOUNS = ["Commerce", "Pay", "Market", "Shop", "Transact", "Payments", "Trade", "Hub"]


def _name(i: int) -> str:
    return f"{RNG.choice(ADJECTIVES)} {RNG.choice(NOUNS)} {i}"


def generate_merchants(n: int = 2000) -> pd.DataFrame:
    categories = RNG.choice(CATEGORIES, size=n)
    regions = RNG.choice(REGIONS, size=n)
    integration = RNG.choice(INTEGRATION, size=n, p=[0.50, 0.35, 0.15])

    years_on_visa = RNG.uniform(0.5, 12, size=n).round(1)
    avg_monthly_volume_k = np.exp(RNG.normal(6.5, 1.4, size=n)).clip(10, 8000).round(1)
    monthly_txn_count = (avg_monthly_volume_k * RNG.uniform(0.5, 3.0, size=n)).astype(int).clip(50, 80000)
    avg_txn_size = (avg_monthly_volume_k * 1000 / monthly_txn_count).round(2)

    dispute_rate_pct = (RNG.exponential(0.6, size=n)).clip(0.05, 5.0).round(2)
    support_tickets_monthly = RNG.integers(0, 18, size=n)
    volume_trend_pct = RNG.normal(8, 20, size=n).clip(-45, 60).round(1)

    # Churn probability model (logistic-ish)
    churn_score = (
        0.30 * (dispute_rate_pct / 5.0)
        + 0.25 * (support_tickets_monthly / 18.0)
        + 0.20 * (-volume_trend_pct / 60.0 + 0.5)
        + 0.15 * (1 - years_on_visa / 12.0)
        + 0.10 * np.where(integration == "Manual", 1, np.where(integration == "Semi-integrated", 0.5, 0))
        + RNG.normal(0, 0.08, size=n)
    ).clip(0, 1)
    churn_label = (churn_score > 0.45).astype(int)

    df = pd.DataFrame({
        "merchant_id": range(1, n + 1),
        "merchant_name": [_name(i) for i in range(1, n + 1)],
        "category": categories,
        "region": regions,
        "integration_type": integration,
        "years_on_visa": years_on_visa,
        "avg_monthly_volume_k": avg_monthly_volume_k,
        "monthly_txn_count": monthly_txn_count,
        "avg_txn_size": avg_txn_size,
        "dispute_rate_pct": dispute_rate_pct,
        "support_tickets_monthly": support_tickets_monthly,
        "volume_trend_pct": volume_trend_pct,
        "churn_label": churn_label,
    })
    return df


if __name__ == "__main__":
    df = generate_merchants()
    df.to_csv("data/merchants.csv", index=False)
    print(f"Generated {len(df)} merchants — churn rate: {df['churn_label'].mean():.1%}")
    print(df.head())
