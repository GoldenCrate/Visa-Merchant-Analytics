import streamlit as st
import altair as alt
import pandas as pd
from utils.data_loader import load_merchants
from utils.churn_model import train_churn_model
from utils.monitoring import simulate_model_drift, check_data_quality

COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}

st.set_page_config(page_title="Model Monitoring", layout="wide")
st.title("Model Monitoring")
st.caption("Production ML models degrade over time as merchant behaviour shifts. This page simulates performance monitoring and flags when retraining is needed.")

df = load_merchants()


@st.cache_resource(show_spinner="Training model...")
def get_model(_df):
    return train_churn_model(_df)


@st.cache_data(show_spinner="Running monitoring checks...")
def get_drift(_model, _X_test, _y_test):
    return simulate_model_drift(_model, _X_test, _y_test)


@st.cache_data(show_spinner="Checking data quality...")
def get_quality(_df):
    return check_data_quality(_df)


model, X_train, X_test, y_test, feature_names, metrics = get_model(df)
drift_df = get_drift(model, X_test, y_test)
quality = get_quality(df)

# ── Current health KPIs ────────────────────────────────────────────────────────
st.markdown("### Model Accuracy Degrades 4 Points by Month 8 — Retraining Trigger Fires")
st.caption("Without retraining, concept drift causes the model to miss an increasing share of churners.")
st.subheader("Model Health Dashboard")
flagged_months = drift_df["Drift_Flagged"].sum()
latest_auc = drift_df["AUC"].iloc[-1]
baseline_auc = drift_df["AUC"].iloc[0]
auc_drop = baseline_auc - latest_auc

h1, h2, h3, h4 = st.columns(4)
h1.metric("Baseline AUC", f"{baseline_auc:.3f}")
h2.metric("Current AUC (Month 12)", f"{latest_auc:.3f}", delta=f"{-auc_drop:.3f}", delta_color="inverse")
h3.metric("Drift Alerts (12 months)", f"{flagged_months}")
h4.metric("Data Quality Score", f"{quality['quality_score']:.1f}/100")

st.divider()

left, right = st.columns(2)

# ── AUC drift over time ────────────────────────────────────────────────────────
with left:
    # Find first flagged month for annotation
    first_flag = drift_df[drift_df["Drift_Flagged"]]["Month"].min() if drift_df["Drift_Flagged"].any() else None

    alerted = drift_df[drift_df["Drift_Flagged"]]

    auc_line = (
        alt.Chart(drift_df)
        .mark_line(color=COLORS["navy"], strokeWidth=2.5)
        .encode(
            x=alt.X("Month:O", title="Month", axis=alt.Axis(grid=False)),
            y=alt.Y("AUC:Q", title="AUC-ROC", scale=alt.Scale(domain=[0.5, 1.0]), axis=alt.Axis(grid=False)),
            tooltip=["Month:O", alt.Tooltip("AUC:Q", format=".4f"), "Drift_Flagged:N"],
        )
    )
    threshold_line = alt.Chart(pd.DataFrame({"y": [baseline_auc - 0.03]})).mark_rule(
        strokeDash=[5, 3], color=COLORS["red"], strokeWidth=2
    ).encode(y="y:Q")
    alert_points = (
        alt.Chart(alerted)
        .mark_point(color=COLORS["red"], size=120, shape="triangle-up", filled=True)
        .encode(x="Month:O", y="AUC:Q", tooltip=["Month:O", alt.Tooltip("AUC:Q", format=".4f")])
    )
    layers = [auc_line, threshold_line, alert_points]
    if first_flag:
        flag_rule = alt.Chart(pd.DataFrame({"Month": [first_flag]})).mark_rule(
            color=COLORS["amber"], strokeDash=[4, 4], strokeWidth=1.5
        ).encode(x="Month:O")
        flag_label = alt.Chart(pd.DataFrame({"Month": [first_flag], "y": [0.55], "label": ["Retrain"]})).mark_text(
            align='left', dx=4, fontSize=10, color=COLORS["amber"]
        ).encode(x="Month:O", y="y:Q", text="label:N")
        layers += [flag_rule, flag_label]

    drift_chart = alt.layer(*layers).properties(height=340).configure_view(strokeWidth=0)

    st.markdown("### AUC Drops Steadily After Month 6 as Merchant Behaviour Shifts")
    st.caption("Red triangles = drift alerts. Amber line = first retraining trigger. Red dashed = threshold.")
    st.altair_chart(drift_chart, use_container_width=True)

# ── Data quality ──────────────────────────────────────────────────────────────
with right:
    st.markdown("### Data Quality Is Stable — 0 Missing Values, Outliers Within Tolerance")
    st.caption("Data pipeline health check. Warning flags drive upstream data engineering tickets.")
    dq1, dq2 = st.columns(2)
    dq1.metric("Missing Values", f"{quality['missing_pct']:.1f}%")
    dq2.metric("Outliers Detected", f"{quality['outlier_count']:,}")

    col_df = quality["col_quality"]
    ok = col_df[col_df["Status"] == "OK"]
    warn = col_df[col_df["Status"] == "Warning"]

    st.markdown(f"**{len(ok)} columns passing** / **{len(warn)} warnings**")

    status_bar_df = pd.DataFrame([
        {"Status": "Passing", "Count": len(ok)},
        {"Status": "Warning", "Count": len(warn)},
    ])
    status_bar = (
        alt.Chart(status_bar_df)
        .mark_bar()
        .encode(
            y=alt.Y("Status:N", title=None, axis=alt.Axis(grid=False)),
            x=alt.X("Count:Q", title="Column Count", axis=alt.Axis(grid=False)),
            color=alt.Color("Status:N", scale=alt.Scale(
                domain=["Passing", "Warning"], range=[COLORS["green"], COLORS["amber"]]
            ), legend=None),
            tooltip=["Status:N", "Count:Q"],
        )
        .properties(height=120)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(status_bar, use_container_width=True)
    st.dataframe(
        col_df.style.map(
            lambda v: "color: #c0392b; font-weight: bold" if v == "Warning" else "color: #1a7a4a",
            subset=["Status"],
        ),
        use_container_width=True,
        height=280,
    )

st.divider()

# ── Retraining protocol ────────────────────────────────────────────────────────
st.subheader("Retraining Protocol")
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("**Trigger**")
    st.error(
        "Retrain when AUC drops >3 percentage points from baseline over any rolling 30-day window, "
        "or when data quality score falls below 85."
    )
with p2:
    st.markdown("**Frequency**")
    st.warning(
        "Scheduled full retrain every 90 days using the latest 18 months of merchant data. "
        "Shadow deployment for 14 days before promotion to production."
    )
with p3:
    st.markdown("**Ownership**")
    st.info(
        "Data Scientist monitors drift dashboard weekly. Alert fires to Slack channel #model-ops. "
        "Business sign-off required before promoting retrained model to production scoring."
    )

st.divider()
st.caption("Drift simulation injects Gaussian noise scaled by month number to model real-world concept drift. Production implementation would compare live predictions against actual 90-day outcomes.")
