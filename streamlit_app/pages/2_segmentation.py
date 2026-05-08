import streamlit as st
import altair as alt
import pandas as pd
from utils.data_loader import load_merchants
from utils.segmentation import segment_merchants

st.set_page_config(page_title="Merchant Segmentation", layout="wide")
st.title("Merchant Segmentation")
st.caption("K-Means clustering groups 2,000 merchants into four behavioural segments — the foundation for targeted account management and GTM prioritization.")

df = load_merchants()


@st.cache_data(show_spinner="Running K-Means segmentation...")
def get_segmented(_df):
    return segment_merchants(_df)


segmented = get_segmented(df)

COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}

SEGMENT_COLORS = {
    "Champions":       COLORS["navy"],
    "Growth Stars":    COLORS["grey"],
    "Stable Partners": COLORS["grey"],
    "At-Risk":         COLORS["red"],
}

# ── Segment summary KPIs ───────────────────────────────────────────────────────
st.markdown("### Champions Are 11% of Merchants but Drive the Majority of Portfolio Volume")
st.caption("Protecting this segment is the highest-ROI retention investment.")
st.subheader("Segment Summary")
seg_summary = (
    segmented.groupby("Segment")
    .agg(
        Count=("merchant_id", "count"),
        Avg_Volume=("avg_monthly_volume_k", "mean"),
        Avg_Dispute=("dispute_rate_pct", "mean"),
        Churn_Rate=("churn_label", "mean"),
        Avg_Trend=("volume_trend_pct", "mean"),
    )
    .reset_index()
)

cols = st.columns(4)
for col, (_, row) in zip(cols, seg_summary.iterrows()):
    with col:
        color = SEGMENT_COLORS.get(row["Segment"], "#333")
        st.markdown(f"<h4 style='color:{color}'>{row['Segment']}</h4>", unsafe_allow_html=True)
        st.metric("Merchants", f"{row['Count']:,}")
        st.metric("Avg Volume", f"${row['Avg_Volume']:,.0f}K")
        st.metric("Churn Rate", f"{row['Churn_Rate']:.1%}")

st.divider()

left, right = st.columns(2)

# ── Scatter: volume vs trend colored by segment ────────────────────────────────
with left:
    st.markdown("### Champions Cluster in High-Volume, Positive-Growth Territory — At-Risk Merchants Are Scattered")
    st.caption("Navy = Champions (protect). Red = At-Risk (intervene). Grey = monitor.")
    scatter = (
        alt.Chart(segmented.sample(min(600, len(segmented)), random_state=42))
        .mark_circle(opacity=0.65, size=60)
        .encode(
            x=alt.X("volume_trend_pct:Q", title="Volume Trend YoY (%)", scale=alt.Scale(domain=[-50, 65]), axis=alt.Axis(grid=False)),
            y=alt.Y("avg_monthly_volume_k:Q", title="Avg Monthly Volume ($K)", scale=alt.Scale(type="log"), axis=alt.Axis(grid=False)),
            color=alt.Color("Segment:N", scale=alt.Scale(
                domain=list(SEGMENT_COLORS.keys()), range=list(SEGMENT_COLORS.values())
            ), legend=None),
            tooltip=[
                "merchant_name:N", "Segment:N", "category:N",
                alt.Tooltip("avg_monthly_volume_k:Q", format="$,.0f", title="Volume ($K)"),
                alt.Tooltip("volume_trend_pct:Q", format=".1f", title="Trend (%)"),
                alt.Tooltip("dispute_rate_pct:Q", format=".2f", title="Dispute Rate (%)"),
            ],
        )
        .properties(height=380)
        .configure_view(strokeWidth=0)
        .interactive()
    )
    st.altair_chart(scatter, use_container_width=True)

# ── Segment profile bars ───────────────────────────────────────────────────────
with right:
    st.markdown("### At-Risk Merchants Have 3× the Dispute Rate of Champions")
    st.caption("Dispute rate is the clearest early warning signal — monitor it weekly.")
    dispute_bar = (
        alt.Chart(seg_summary)
        .mark_bar()
        .encode(
            y=alt.Y("Segment:N", sort="-x", title=None, axis=alt.Axis(grid=False)),
            x=alt.X("Avg_Dispute:Q", title="Avg Dispute Rate (%)", axis=alt.Axis(grid=False)),
            color=alt.Color("Segment:N", scale=alt.Scale(
                domain=list(SEGMENT_COLORS.keys()), range=list(SEGMENT_COLORS.values())
            ), legend=None),
            tooltip=["Segment:N", alt.Tooltip("Avg_Dispute:Q", format=".2f", title="Avg Dispute (%)")],
        )
        .properties(height=180)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(dispute_bar, use_container_width=True)

    st.markdown("### At-Risk Merchants Churn at 4× the Rate of Champions")
    st.caption("Segment-level churn rates define intervention priority and budget allocation.")
    churn_pct_df = seg_summary.copy()
    churn_pct_df["Churn_Pct"] = (churn_pct_df["Churn_Rate"] * 100).round(1)
    churn_bar = (
        alt.Chart(churn_pct_df)
        .mark_bar()
        .encode(
            y=alt.Y("Segment:N", sort="-x", title=None, axis=alt.Axis(grid=False)),
            x=alt.X("Churn_Pct:Q", title="Churn Rate (%)", axis=alt.Axis(grid=False)),
            color=alt.Color("Segment:N", scale=alt.Scale(
                domain=list(SEGMENT_COLORS.keys()), range=list(SEGMENT_COLORS.values())
            ), legend=None),
            tooltip=["Segment:N", alt.Tooltip("Churn_Pct:Q", format=".1f", title="Churn (%)")],
        )
        .properties(height=180)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(churn_bar, use_container_width=True)

st.divider()

# ── Segment breakdown table ────────────────────────────────────────────────────
st.subheader("Segment Profiles")
display = seg_summary.copy()
display["Avg_Volume"] = display["Avg_Volume"].round(0)
display["Avg_Dispute"] = display["Avg_Dispute"].round(2)
display["Churn_Rate"] = (display["Churn_Rate"] * 100).round(1)
display["Avg_Trend"] = display["Avg_Trend"].round(1)
display.columns = ["Segment", "Count", "Avg Volume ($K)", "Avg Dispute Rate (%)", "Churn Rate (%)", "Avg Volume Trend (%)"]
st.dataframe(display.set_index("Segment"), use_container_width=True)

st.divider()
st.subheader("Segment Definitions")
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown("**Champions**")
    st.success("Highest volume, low churn risk. Protect and grow. Offer premium features and dedicated relationship management.")
with s2:
    st.markdown("**Growth Stars**")
    st.info("Strong positive volume trend. Invest in onboarding and integration upgrades to lock in loyalty.")
with s3:
    st.markdown("**Stable Partners**")
    st.warning("Moderate volume, flat growth. Upsell opportunity — introduce new Visa products to re-engage.")
with s4:
    st.markdown("**At-Risk**")
    st.error("High dispute rates and declining volumes. Immediate intervention: assign relationship manager and resolve disputes.")
