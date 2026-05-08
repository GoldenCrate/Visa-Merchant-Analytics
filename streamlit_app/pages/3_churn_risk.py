import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve
from utils.data_loader import load_merchants
from utils.churn_model import train_churn_model, predict_merchant_churn, FEATURES, FRIENDLY_NAMES

COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}

st.set_page_config(page_title="Churn Risk", layout="wide")
st.title("Churn Risk Classifier")
st.caption("A Random Forest model trained on 1,500 merchants predicts 90-day churn risk. Score any merchant in real time using the inputs below.")

df = load_merchants()


@st.cache_resource(show_spinner="Training churn model...")
def get_model(_df):
    return train_churn_model(_df)


model, X_train, X_test, y_test, feature_names, metrics = get_model(df)

# ── Model performance KPIs ────────────────────────────────────────────────────
st.markdown("### The Model Identifies High-Risk Merchants with Strong Recall — Catching Most Before They Leave")
st.caption("AUC above 0.80 — meaningfully above random; tuned for early intervention over false precision.")
st.subheader("Model Performance")
m1, m2, m3, m4 = st.columns(4)
m1.metric("AUC-ROC", f"{metrics['auc']:.3f}")
m2.metric("Accuracy", f"{metrics['accuracy']:.1%}")
m3.metric("Precision", f"{metrics['precision']:.1%}")
m4.metric("Recall", f"{metrics['recall']:.1%}")

st.divider()

left, right = st.columns([1, 1])

# ── ROC Curve ─────────────────────────────────────────────────────────────────
with left:
    y_prob = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_df = pd.DataFrame({"FPR": fpr, "TPR": tpr})

    # Find approximate operating point
    op_idx = int(len(fpr) * 0.25)
    op_df = pd.DataFrame({"FPR": [fpr[op_idx]], "TPR": [tpr[op_idx]]})

    roc_line = (
        alt.Chart(roc_df)
        .mark_line(color=COLORS["navy"], strokeWidth=2.5)
        .encode(
            x=alt.X("FPR:Q", title="False Positive Rate", axis=alt.Axis(grid=False)),
            y=alt.Y("TPR:Q", title="True Positive Rate", axis=alt.Axis(grid=False)),
            tooltip=[
                alt.Tooltip("FPR:Q", format=".2f", title="FPR"),
                alt.Tooltip("TPR:Q", format=".2f", title="TPR"),
            ],
        )
        .properties(height=320)
    )
    diag = alt.Chart(pd.DataFrame({"x": [0, 1], "y": [0, 1]})).mark_line(
        strokeDash=[4, 4], color=COLORS["grey"]
    ).encode(x="x:Q", y="y:Q")
    op_point = alt.Chart(op_df).mark_point(
        color=COLORS["blue"], size=120, filled=True
    ).encode(x="FPR:Q", y="TPR:Q")
    op_label = alt.Chart(op_df).mark_text(
        align='left', dx=8, fontSize=11, color=COLORS["navy"], text="Operating point"
    ).encode(x="FPR:Q", y="TPR:Q")
    roc_chart = (roc_line + diag + op_point + op_label).configure_view(strokeWidth=0)

    st.markdown("### ROC Curve — Model Discriminates Well Above the Random Baseline")
    st.caption(f"AUC = {metrics['auc']:.3f}. Blue dot = operating point. Dashed line = random baseline.")
    st.altair_chart(roc_chart, use_container_width=True)

# ── Churn probability distribution ────────────────────────────────────────────
with right:
    train_prob = model.predict_proba(X_train)[:, 1]
    prob_df = pd.DataFrame({"Churn_Probability": np.concatenate([y_prob, train_prob])})
    hist = (
        alt.Chart(prob_df)
        .mark_bar(color=COLORS["navy"], opacity=0.8)
        .encode(
            x=alt.X("Churn_Probability:Q", bin=alt.Bin(maxbins=30), title="Predicted Churn Probability", axis=alt.Axis(grid=False)),
            y=alt.Y("count():Q", title="Merchant Count", axis=alt.Axis(grid=False)),
        )
        .properties(height=320)
    )
    threshold = alt.Chart(pd.DataFrame({"x": [0.35]})).mark_rule(
        strokeDash=[5, 3], color=COLORS["red"], strokeWidth=2
    ).encode(x="x:Q")
    label_y = int(np.histogram(prob_df["Churn_Probability"], bins=30)[0].max() * 0.6)
    threshold_label = alt.Chart(pd.DataFrame({"x": [0.35], "y": [label_y], "label": ["Risk threshold"]})).mark_text(
        align='left', dx=6, fontSize=11, color=COLORS["red"]
    ).encode(x="x:Q", y="y:Q", text="label:N")
    prob_chart = (hist + threshold + threshold_label).configure_view(strokeWidth=0)

    st.markdown("### Most Merchants Score Low Risk — a Concentrated High-Risk Tail Drives Churn")
    st.caption("Red line = 0.35 threshold. Merchants to the right are flagged for intervention.")
    st.altair_chart(prob_chart, use_container_width=True)

st.divider()

# ── Real-time merchant scorer ─────────────────────────────────────────────────
st.markdown("### Score Any Merchant Profile — Adjust Inputs to See Risk Change Instantly")
st.caption("Move dispute rate or volume trend to see the biggest impact on churn probability.")

c1, c2, c3 = st.columns(3)
with c1:
    volume = st.slider("Avg Monthly Volume ($K)", 10, 5000, 500, step=10)
    dispute = st.slider("Dispute Rate (%)", 0.05, 5.0, 0.8, step=0.05)
    trend = st.slider("Volume Trend YoY (%)", -45, 60, 5, step=1)
with c2:
    txn_count = st.slider("Monthly Transaction Count", 50, 50000, 5000, step=100)
    support = st.slider("Support Tickets / Month", 0, 18, 2)
    years = st.slider("Years on Visa", 0.5, 12.0, 3.0, step=0.5)
with c3:
    integration = st.selectbox("Integration Type", ["Integrated", "Semi-integrated", "Manual"])
    category = st.selectbox("Merchant Category", ["Retail", "Restaurant", "eCommerce", "Travel", "Entertainment", "Services"])
    region = st.selectbox("Region", ["North America", "Europe", "Asia Pacific", "LAC", "MEA"])

avg_txn = round((volume * 1000) / max(txn_count, 1), 2)

merchant_input = {
    "avg_monthly_volume_k": volume,
    "monthly_txn_count": txn_count,
    "avg_txn_size": avg_txn,
    "dispute_rate_pct": dispute,
    "support_tickets_monthly": support,
    "volume_trend_pct": trend,
    "years_on_visa": years,
    "integration_type": integration,
    "category": category,
    "region": region,
}

result = predict_merchant_churn(model, merchant_input)
prob = result["churn_probability"]
tier = result["risk_tier"]

RISK_COLORS = {"High Risk": COLORS["red"], "Medium Risk": COLORS["amber"], "Low Risk": COLORS["green"]}
color = RISK_COLORS[tier]

st.divider()
r1, r2, r3 = st.columns(3)
r1.metric("Churn Probability", f"{prob:.1%}")
r2.metric("Risk Tier", tier)
r3.metric("Avg Transaction Size", f"${avg_txn:,.2f}")
st.markdown(f"<h4 style='color:{color}'>⬤ {tier}</h4>", unsafe_allow_html=True)
if tier == "High Risk":
    st.error("Immediate intervention recommended. Assign relationship manager and review dispute resolution process.")
elif tier == "Medium Risk":
    st.warning("Monitor closely. Initiate proactive outreach and review integration support options.")
else:
    st.success("Low churn risk. Standard account management. Consider upsell opportunities.")
