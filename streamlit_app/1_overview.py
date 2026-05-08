import streamlit as st
import altair as alt
import pandas as pd
from utils.data_loader import load_merchants

COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}

st.set_page_config(page_title="Merchant Analytics", layout="wide")
st.title("Visa Merchant Analytics Platform")
st.caption("A data scientist's toolkit for merchant segmentation, churn prediction, and model monitoring — built on 2,000 synthetic Visa merchant profiles.")

df = load_merchants()

# ── KPI cards ─────────────────────────────────────────────────────────────────
st.markdown("### Manual Integration Drives 2× the Churn of Fully Integrated Merchants")
st.caption("Integration type is the single most actionable lever for reducing portfolio churn.")
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
    st.markdown("### eCommerce Leads Portfolio Volume by Merchant Category")
    st.caption("Focus retention resources on eCommerce — highest absolute revenue at risk.")
    vol_cat = (
        df.groupby("category")["avg_monthly_volume_k"]
        .median()
        .reset_index()
        .rename(columns={"avg_monthly_volume_k": "Median_Volume_K", "category": "Category"})
        .sort_values("Median_Volume_K", ascending=True)
    )
    # Identify highest-volume category for highlighting
    top_cat = vol_cat.loc[vol_cat["Median_Volume_K"].idxmax(), "Category"]

    bar = (
        alt.Chart(vol_cat)
        .mark_bar()
        .encode(
            y=alt.Y("Category:N", sort="-x", title=None, axis=alt.Axis(grid=False)),
            x=alt.X("Median_Volume_K:Q", title="Median Monthly Volume ($K)", axis=alt.Axis(grid=False)),
            color=alt.condition(
                alt.datum.Category == top_cat,
                alt.value(COLORS["blue"]),
                alt.value(COLORS["grey"])
            ),
            tooltip=["Category:N", alt.Tooltip("Median_Volume_K:Q", format="$,.0f", title="Median Volume ($K)")],
        )
        .properties(height=280)
    )
    labels = bar.mark_text(align='left', dx=4, fontSize=11, color=COLORS["navy"]).encode(
        text=alt.Text("Median_Volume_K:Q", format=",.0f")
    )
    bar = (bar + labels).configure_view(strokeWidth=0)
    st.altair_chart(bar, use_container_width=True)

# ── Churn rate by region ───────────────────────────────────────────────────────
with right:
    st.markdown("### MEA Merchants Churn at the Highest Rate Across All Regions")
    st.caption("MEA requires immediate intervention — assign regional relationship managers.")
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
            y=alt.Y("Region:N", sort="-x", title=None, axis=alt.Axis(grid=False)),
            x=alt.X("Churn_Pct:Q", title="Churn Rate (%)", axis=alt.Axis(grid=False)),
            color=alt.condition(
                alt.datum.Region == "MEA",
                alt.value(COLORS["blue"]),
                alt.value(COLORS["grey"])
            ),
            tooltip=["Region:N", alt.Tooltip("Churn_Pct:Q", format=".1f", title="Churn Rate (%)")],
        )
        .properties(height=280)
    )
    churn_labels = churn_bar.mark_text(align='left', dx=4, fontSize=11, color=COLORS["navy"]).encode(
        text=alt.Text("Churn_Pct:Q", format=".1f")
    )
    churn_bar = (churn_bar + churn_labels).configure_view(strokeWidth=0)
    st.altair_chart(churn_bar, use_container_width=True)

st.divider()

left2, right2 = st.columns(2)

# ── Dispute rate distribution ─────────────────────────────────────────────────
with left2:
    st.markdown("### Most Merchants Have Dispute Rates Under 1% — Outliers Drive Churn")
    st.caption("Flag any merchant above 2% for dispute resolution review.")
    hist_df = df[["dispute_rate_pct"]].copy()
    hist = (
        alt.Chart(hist_df)
        .mark_bar(color=COLORS["navy"])
        .encode(
            x=alt.X("dispute_rate_pct:Q", bin=alt.Bin(maxbins=30), title="Dispute Rate (%)", axis=alt.Axis(grid=False)),
            y=alt.Y("count():Q", title="Merchant Count", axis=alt.Axis(grid=False)),
            tooltip=[alt.Tooltip("dispute_rate_pct:Q", bin=True, title="Range"), "count()"],
        )
        .properties(height=260)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(hist, use_container_width=True)

# ── Integration type breakdown ────────────────────────────────────────────────
with right2:
    st.markdown("### Manual Integration Merchants Churn at 2× the Rate of Fully Integrated Merchants")
    st.caption("Integration upgrade is the highest-ROI intervention for at-risk merchants.")
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
            y=alt.Y("Integration:N", sort="-x", title=None, axis=alt.Axis(grid=False)),
            x=alt.X("Churn_Pct:Q", title="Churn Rate (%)", axis=alt.Axis(grid=False)),
            color=alt.condition(
                alt.datum.Integration == "Manual",
                alt.value(COLORS["red"]),
                alt.condition(
                    alt.datum.Integration == "Semi-integrated",
                    alt.value(COLORS["amber"]),
                    alt.value(COLORS["green"])
                )
            ),
            tooltip=["Integration:N", alt.Tooltip("Churn_Pct:Q", format=".1f", title="Churn (%)"), "Count:Q"],
        )
        .properties(height=180)
    )
    integ_labels = integ_bar.mark_text(align='left', dx=4, fontSize=11, color=COLORS["navy"]).encode(
        text=alt.Text("Churn_Pct:Q", format=".1f")
    )
    integ_bar = (integ_bar + integ_labels).configure_view(strokeWidth=0)
    st.altair_chart(integ_bar, use_container_width=True)

st.divider()
st.caption("Data: 2,000 synthetic Visa merchant profiles. Loaded from Snowflake when credentials are available, local CSV otherwise.")
