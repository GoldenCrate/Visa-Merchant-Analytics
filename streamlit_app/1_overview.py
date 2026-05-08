import streamlit as st
import altair as alt
import pandas as pd
from utils.data_loader import load_merchants

st.set_page_config(page_title="Merchant Analytics", layout="wide")
st.title("Visa Merchant Analytics Platform")
st.caption("A data scientist's toolkit for merchant segmentation, churn prediction, and model monitoring — built on 2,000 synthetic Visa merchant profiles.")

df = load_merchants()

# ── KPI cards ─────────────────────────────────────────────────────────────────
st.subheader("Portfolio Overview")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Merchants", f"{len(df):,}")
k2.metric("Avg Monthly Volume", f"${df['avg_monthly_volume_k'].mean():,.0f}K")
k3.metric("Churn Rate", f"{df['churn_label'].mean():.1%}")
k4.metric("Avg Dispute Rate", f"{df['dispute_rate_pct'].mean():.2f}%")
k5.metric("Avg Tenure", f"{df['years_on_visa'].mean():.1f} yrs")

st.divider()

left, right = st.columns(2)

# ── Volume distribution by category ───────────────────────────────────────────
with left:
    st.subheader("Monthly Volume by Category")
    vol_cat = (
        df.groupby("category")["avg_monthly_volume_k"]
        .median()
        .reset_index()
        .rename(columns={"avg_monthly_volume_k": "Median_Volume_K", "category": "Category"})
        .sort_values("Median_Volume_K", ascending=True)
    )
    bar = (
        alt.Chart(vol_cat)
        .mark_bar()
        .encode(
            y=alt.Y("Category:N", sort="-x", title=None),
            x=alt.X("Median_Volume_K:Q", title="Median Monthly Volume ($K)"),
            color=alt.Color("Category:N", legend=None),
            tooltip=["Category:N", alt.Tooltip("Median_Volume_K:Q", format="$,.0f", title="Median Volume ($K)")],
        )
        .properties(height=280)
    )
    st.altair_chart(bar, use_container_width=True)

# ── Churn rate by region ───────────────────────────────────────────────────────
with right:
    st.subheader("Churn Rate by Region")
    churn_reg = (
        df.groupby("region")["churn_label"]
        .mean()
        .reset_index()
        .rename(columns={"churn_label": "Churn_Rate", "region": "Region"})
        .sort_values("Churn_Rate", ascending=True)
    )
    churn_reg["Churn_Pct"] = (churn_reg["Churn_Rate"] * 100).round(1)
    churn_bar = (
        alt.Chart(churn_reg)
        .mark_bar()
        .encode(
            y=alt.Y("Region:N", sort="-x", title=None),
            x=alt.X("Churn_Pct:Q", title="Churn Rate (%)"),
            color=alt.condition(
                alt.datum.Churn_Pct > 20,
                alt.value("#c0392b"),
                alt.value("#d4850a"),
            ),
            tooltip=["Region:N", alt.Tooltip("Churn_Pct:Q", format=".1f", title="Churn Rate (%)")],
        )
        .properties(height=280)
    )
    st.altair_chart(churn_bar, use_container_width=True)

st.divider()

left2, right2 = st.columns(2)

# ── Dispute rate distribution ─────────────────────────────────────────────────
with left2:
    st.subheader("Dispute Rate Distribution")
    hist_df = df[["dispute_rate_pct"]].copy()
    hist = (
        alt.Chart(hist_df)
        .mark_bar(color="#1a7a4a")
        .encode(
            x=alt.X("dispute_rate_pct:Q", bin=alt.Bin(maxbins=30), title="Dispute Rate (%)"),
            y=alt.Y("count():Q", title="Merchant Count"),
            tooltip=[alt.Tooltip("dispute_rate_pct:Q", bin=True, title="Range"), "count()"],
        )
        .properties(height=260)
    )
    st.altair_chart(hist, use_container_width=True)

# ── Integration type breakdown ────────────────────────────────────────────────
with right2:
    st.subheader("Churn Rate by Integration Type")
    integ = (
        df.groupby("integration_type")["churn_label"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Churn_Rate", "count": "Count", "integration_type": "Integration"})
    )
    integ["Churn_Pct"] = (integ["Churn_Rate"] * 100).round(1)
    integ_bar = (
        alt.Chart(integ)
        .mark_bar()
        .encode(
            y=alt.Y("Integration:N", sort="-x", title=None),
            x=alt.X("Churn_Pct:Q", title="Churn Rate (%)"),
            color=alt.Color("Integration:N", scale=alt.Scale(
                domain=["Integrated", "Semi-integrated", "Manual"],
                range=["#1a7a4a", "#d4850a", "#c0392b"]
            ), legend=None),
            tooltip=["Integration:N", alt.Tooltip("Churn_Pct:Q", format=".1f", title="Churn (%)"), "Count:Q"],
        )
        .properties(height=180)
    )
    st.altair_chart(integ_bar, use_container_width=True)

st.divider()
st.caption("Data: 2,000 synthetic Visa merchant profiles. Loaded from Snowflake when credentials are available, local CSV otherwise.")
