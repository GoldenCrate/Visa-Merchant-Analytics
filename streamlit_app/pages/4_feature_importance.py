import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
from utils.data_loader import load_merchants
from utils.churn_model import train_churn_model, predict_merchant_churn, FEATURES, FRIENDLY_NAMES
from utils.shap_explainer import compute_global_importance, compute_merchant_shap

st.set_page_config(page_title="Feature Importance", layout="wide")
st.title("SHAP Feature Importance")
st.caption("SHAP (SHapley Additive exPlanations) explains exactly which factors drive churn risk — globally across all merchants and for any individual merchant.")

df = load_merchants()

INTEGRATION_MAP = {"Integrated": 0, "Manual": 1, "Semi-integrated": 2}
CATEGORY_MAP = {"Entertainment": 0, "Restaurant": 1, "Retail": 2, "Services": 3, "Travel": 4, "eCommerce": 5}
REGION_MAP = {"Asia Pacific": 0, "Europe": 1, "LAC": 2, "MEA": 3, "North America": 4}


def _row_to_array(row) -> np.ndarray:
    return np.array([[
        row["avg_monthly_volume_k"],
        row["monthly_txn_count"],
        row["avg_txn_size"],
        row["dispute_rate_pct"],
        row["support_tickets_monthly"],
        row["volume_trend_pct"],
        row["years_on_visa"],
        INTEGRATION_MAP.get(row["integration_type"], 0),
        CATEGORY_MAP.get(row["category"], 2),
        REGION_MAP.get(row["region"], 4),
    ]])


@st.cache_resource(show_spinner="Training model...")
def get_model(_df):
    return train_churn_model(_df)


@st.cache_data(show_spinner="Computing SHAP values...")
def get_global_importance(_model, _X_train):
    return compute_global_importance(_model, _X_train)


model, X_train, X_test, y_test, feature_names, metrics = get_model(df)
global_imp = get_global_importance(model, X_train)

# ── Global importance chart ────────────────────────────────────────────────────
st.subheader("Global Feature Importance (Mean |SHAP|)")
st.markdown("Average absolute SHAP value across all merchants — the higher the bar, the more that feature drives churn predictions overall.")

global_bar = (
    alt.Chart(global_imp)
    .mark_bar(color="#2471a3")
    .encode(
        y=alt.Y("Feature:N", sort="-x", title=None),
        x=alt.X("Importance:Q", title="Mean |SHAP Value|"),
        tooltip=["Feature:N", alt.Tooltip("Importance:Q", format=".4f", title="Mean |SHAP|")],
    )
    .properties(height=340)
)
st.altair_chart(global_bar, use_container_width=True)
st.caption("SHAP values are computed using TreeExplainer on the trained Random Forest.")

st.divider()

# ── Per-merchant SHAP waterfall ────────────────────────────────────────────────
st.subheader("Individual Merchant Explanation")
st.markdown("Select a merchant to see exactly why the model assigned their churn score.")

sample = df.sample(min(50, len(df)), random_state=1).sort_values("churn_label", ascending=False)
selected_name = st.selectbox("Select merchant", sample["merchant_name"].tolist())
selected_row = sample[sample["merchant_name"] == selected_name].iloc[0]

merchant_arr = _row_to_array(selected_row)
shap_df = compute_merchant_shap(model, merchant_arr)
churn_result = predict_merchant_churn(model, selected_row.to_dict())

m1, m2, m3 = st.columns(3)
m1.metric("Churn Probability", f"{churn_result['churn_probability']:.1%}")
m2.metric("Risk Tier", churn_result["risk_tier"])
m3.metric("Dispute Rate", f"{selected_row['dispute_rate_pct']:.2f}%")

waterfall = (
    alt.Chart(shap_df)
    .mark_bar()
    .encode(
        y=alt.Y("Feature:N", sort=list(shap_df["Feature"]), title=None),
        x=alt.X("SHAP_Value:Q", title="SHAP Value (positive = increases churn risk)"),
        color=alt.Color("Direction:N", scale=alt.Scale(
            domain=["Increases Risk", "Reduces Risk"],
            range=["#c0392b", "#1a7a4a"]
        )),
        tooltip=["Feature:N", alt.Tooltip("SHAP_Value:Q", format=".4f", title="SHAP Value"), "Direction:N"],
    )
    .properties(height=340)
)
zero_line = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="#888").encode(x="x:Q")
st.altair_chart(waterfall + zero_line, use_container_width=True)
st.caption("Red bars = features that increase this merchant's churn probability. Green = features that reduce it.")

st.divider()
st.subheader("Translating SHAP to Business Language")
c1, c2 = st.columns(2)
with c1:
    st.info(
        "SHAP turns a black-box model into a conversation. Instead of saying "
        "\"the model says this merchant will churn,\" you can say: "
        "\"dispute rate is 3× the portfolio average and their volume has declined 18% YoY — "
        "those two factors alone account for 60% of their risk score.\""
    )
with c2:
    st.warning(
        "**Action Triggers**\n\n"
        "- Dispute Rate > 2%: Escalate to dispute resolution team\n"
        "- Volume Trend < −10%: Proactive outreach from relationship manager\n"
        "- Support Tickets > 8/month: Flag for integration health review"
    )
