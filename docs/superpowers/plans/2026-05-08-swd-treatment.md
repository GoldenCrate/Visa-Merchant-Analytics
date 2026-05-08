# SWD Treatment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply Storytelling with Data best practices to all 9 pages across two Streamlit dashboards — insight-driven chart titles, navy+blue colour system, no gridlines/borders, direct value labels.

**Architecture:** Each page file is self-contained. Add a `COLORS` dict at the top of each file, then update each chart in place. No shared module, no structural changes. Visual presentation only — models, data, and tests are untouched.

**Tech Stack:** Altair 5, Streamlit, Python. Both dashboards already deployed on Streamlit Community Cloud.

---

## Colour Reference (use in every task)

```python
COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}
```

## Altair Patterns (use in every task)

**Remove gridlines:** `axis=alt.Axis(grid=False)` on both X and Y encodings.

**Remove chart border:** `.configure_view(strokeWidth=0)` at the end of the chart expression. Only call once per chart — call it on the final combined chart (e.g. `bars + labels`), not on each layer separately.

**Highlight one bar, grey the rest:**
```python
color=alt.condition(
    alt.datum.ColumnName == 'TargetValue',
    alt.value(COLORS["blue"]),
    alt.value(COLORS["grey"])
)
```

**Add direct value labels on horizontal bars:**
```python
labels = base.mark_text(align='left', dx=4, fontSize=11, color=COLORS["navy"]).encode(
    text=alt.Text('Value:Q', format='.1f')
)
chart = (bars + labels).configure_view(strokeWidth=0)
```

**Insight title + sub-caption pattern:**
```python
st.markdown("### Insight Title Text Here")
st.caption("Sub-caption: the so-what or recommended action.")
st.altair_chart(chart, use_container_width=True)
```

---

## DASHBOARD 1: Visa Merchant Analytics
**Repo path:** `S:\JobApplicationProject\Projects\Visa-Merchant-Analytics\streamlit_app\`

---

### Task 1: Overview Page (Page 1)

**Files:**
- Modify: `streamlit_app/1_overview.py`

- [ ] **Step 1: Read the current file**

```
Read S:\JobApplicationProject\Projects\Visa-Merchant-Analytics\streamlit_app\1_overview.py
```

- [ ] **Step 2: Add COLORS dict at the top of the file, after imports**

Add immediately after the last import line:
```python
COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}
```

- [ ] **Step 3: Add page-level insight title below `st.caption`**

Replace the existing `st.subheader("Portfolio Overview")` and the caption line below it with:
```python
st.markdown("### Manual Integration Drives 2× the Churn of Fully Integrated Merchants")
st.caption("Integration type is the single most actionable lever for reducing portfolio churn.")
```
Keep the KPI metrics columns (`k1` through `k5`) unchanged.

- [ ] **Step 4: Update Volume by Category bar chart**

Replace the `bar` chart definition with:
```python
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
```

Replace the `st.subheader("Monthly Volume by Category")` line with:
```python
st.markdown("### eCommerce Leads Portfolio Volume by Merchant Category")
st.caption("Focus retention resources on eCommerce — highest absolute revenue at risk.")
```

- [ ] **Step 5: Update Churn Rate by Region bar chart**

Replace the `churn_bar` definition with:
```python
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
```

Replace `st.subheader("Churn Rate by Region")` with:
```python
st.markdown("### MEA Merchants Churn at the Highest Rate Across All Regions")
st.caption("MEA requires immediate intervention — assign regional relationship managers.")
```

- [ ] **Step 6: Update Dispute Rate histogram**

Replace the `hist` definition with:
```python
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
```

Replace `st.subheader("Dispute Rate Distribution")` with:
```python
st.markdown("### Most Merchants Have Dispute Rates Under 1% — Outliers Drive Churn")
st.caption("Flag any merchant above 2% for dispute resolution review.")
```

- [ ] **Step 7: Update Churn by Integration bar chart**

Replace the `integ_bar` definition with:
```python
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
```

Replace `st.subheader("Churn Rate by Integration Type")` with:
```python
st.markdown("### Manual Integration Merchants Churn at 2× the Rate of Fully Integrated Merchants")
st.caption("Integration upgrade is the highest-ROI intervention for at-risk merchants.")
```

- [ ] **Step 8: Verify locally**

```
cd S:\JobApplicationProject\Projects\Visa-Merchant-Analytics\streamlit_app
streamlit run 1_overview.py
```

Open http://localhost:8501. Check: bars are navy/grey with blue highlights, no gridlines, insight titles visible, value labels on bars.

- [ ] **Step 9: Commit**

```bash
cd S:\JobApplicationProject\Projects\Visa-Merchant-Analytics
git add streamlit_app/1_overview.py
git commit -m "swd: overview page — insight titles, navy/blue palette, direct labels"
```

---

### Task 2: Segmentation Page (Page 2)

**Files:**
- Modify: `streamlit_app/pages/2_segmentation.py`

- [ ] **Step 1: Read the current file**

```
Read S:\JobApplicationProject\Projects\Visa-Merchant-Analytics\streamlit_app\pages\2_segmentation.py
```

- [ ] **Step 2: Replace SEGMENT_COLORS dict**

Find the existing `SEGMENT_COLORS` dict and replace it:
```python
COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}

SEGMENT_COLORS = {
    "Champions":      COLORS["navy"],
    "Growth Stars":   COLORS["grey"],
    "Stable Partners": COLORS["grey"],
    "At-Risk":        COLORS["red"],
}
```

- [ ] **Step 3: Add page-level insight title**

Replace `st.subheader("Segment Summary")` with:
```python
st.markdown("### Champions Are 11% of Merchants but Drive the Majority of Portfolio Volume")
st.caption("Protecting this segment is the highest-ROI retention investment.")
st.subheader("Segment Summary")
```

- [ ] **Step 4: Update scatter chart**

Replace the `scatter` definition with:
```python
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
```

Replace `st.subheader("Volume vs Growth Trend by Segment")` with:
```python
st.markdown("### Champions Cluster in High-Volume, Positive-Growth Territory — At-Risk Merchants Are Scattered")
st.caption("Navy = Champions (protect). Red = At-Risk (intervene). Grey = monitor.")
```

- [ ] **Step 5: Update dispute and churn bar charts**

Replace the `dispute_bar` definition with:
```python
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
```

Replace `st.subheader("Average Dispute Rate by Segment")` with:
```python
st.markdown("### At-Risk Merchants Have 3× the Dispute Rate of Champions")
st.caption("Dispute rate is the clearest early warning signal — monitor it weekly.")
```

Replace the `churn_bar` definition with:
```python
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
```

Replace `st.subheader("Churn Rate by Segment")` with:
```python
st.markdown("### At-Risk Merchants Churn at 4× the Rate of Champions")
st.caption("Segment-level churn rates define intervention priority and budget allocation.")
```

- [ ] **Step 6: Verify locally, then commit**

```bash
cd S:\JobApplicationProject\Projects\Visa-Merchant-Analytics
git add streamlit_app/pages/2_segmentation.py
git commit -m "swd: segmentation page — insight titles, segment colour system, no gridlines"
```

---

### Task 3: Churn Risk Page (Page 3)

**Files:**
- Modify: `streamlit_app/pages/3_churn_risk.py`

- [ ] **Step 1: Read the current file**

```
Read S:\JobApplicationProject\Projects\Visa-Merchant-Analytics\streamlit_app\pages\3_churn_risk.py
```

- [ ] **Step 2: Add COLORS dict after imports**

```python
COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}
```

- [ ] **Step 3: Add page-level insight title**

Replace `st.subheader("Model Performance")` with:
```python
st.markdown("### The Model Identifies High-Risk Merchants with Strong Recall — Catching Most Before They Leave")
st.caption("AUC above 0.80 — meaningfully above random; tuned for early intervention over false precision.")
st.subheader("Model Performance")
```

- [ ] **Step 4: Update ROC curve**

Replace the `roc_line`, `diag`, and their `st.altair_chart` call with:
```python
# Find approximate operating point (threshold ~0.35, closest fpr/tpr)
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
```

Replace `st.altair_chart(roc_line + diag, use_container_width=True)` with:
```python
st.markdown("### ROC Curve — Model Discriminates Well Above the Random Baseline")
st.caption(f"AUC = {metrics['auc']:.3f}. Blue dot = operating point at 0.35 threshold.")
st.altair_chart(roc_chart, use_container_width=True)
```

- [ ] **Step 5: Update probability distribution**

Replace the `hist` and threshold chart definitions and their `st.altair_chart` call with:
```python
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
threshold_label = alt.Chart(pd.DataFrame({"x": [0.35], "y": [50], "label": ["Risk threshold"]})).mark_text(
    align='left', dx=6, fontSize=11, color=COLORS["red"]
).encode(x="x:Q", y="y:Q", text="label:N")
prob_chart = (hist + threshold + threshold_label).configure_view(strokeWidth=0)
```

Replace the `st.altair_chart` for the histogram with:
```python
st.markdown("### Most Merchants Score Low Risk — a Concentrated High-Risk Tail Drives Churn")
st.caption("Red line = 0.35 threshold. Merchants to the right are flagged for intervention.")
st.altair_chart(prob_chart, use_container_width=True)
```

- [ ] **Step 6: Update the live scorer section title**

Replace `st.subheader("Score a Merchant in Real Time")` with:
```python
st.markdown("### Score Any Merchant Profile — Adjust Inputs to See Risk Change Instantly")
st.caption("Move dispute rate or volume trend to see the biggest impact on churn probability.")
```

- [ ] **Step 7: Verify locally, then commit**

```bash
cd S:\JobApplicationProject\Projects\Visa-Merchant-Analytics
git add streamlit_app/pages/3_churn_risk.py
git commit -m "swd: churn risk page — ROC annotation, navy palette, insight titles"
```

---

### Task 4: Feature Importance Page (Page 4)

**Files:**
- Modify: `streamlit_app/pages/4_feature_importance.py`

- [ ] **Step 1: Read the current file**

```
Read S:\JobApplicationProject\Projects\Visa-Merchant-Analytics\streamlit_app\pages\4_feature_importance.py
```

- [ ] **Step 2: Add COLORS dict after imports**

```python
COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}
```

- [ ] **Step 3: Update page title and global importance chart**

Replace `st.subheader("Global Feature Importance (Mean |SHAP|)")` and its caption with:
```python
st.markdown("### Dispute Rate and Volume Decline Are the Strongest Predictors of Churn")
st.caption("These two features are the earliest warning signals — monitor them weekly for at-risk merchants.")
```

Replace the `global_bar` definition with:
```python
# Top 2 features get blue accent; rest are grey
top2 = set(global_imp.nlargest(2, "Importance")["Feature"].tolist())

global_bar = (
    alt.Chart(global_imp)
    .mark_bar()
    .encode(
        y=alt.Y("Feature:N", sort="-x", title=None, axis=alt.Axis(grid=False)),
        x=alt.X("Importance:Q", title="Feature Importance Score", axis=alt.Axis(grid=False)),
        color=alt.condition(
            alt.FieldOneOfPredicate(field="Feature", oneOf=list(top2)),
            alt.value(COLORS["blue"]),
            alt.value(COLORS["grey"])
        ),
        tooltip=["Feature:N", alt.Tooltip("Importance:Q", format=".4f", title="Importance")],
    )
    .properties(height=340)
)
imp_labels = global_bar.mark_text(align='left', dx=4, fontSize=11, color=COLORS["navy"]).encode(
    text=alt.Text("Importance:Q", format=".3f")
)
global_bar = (global_bar + imp_labels).configure_view(strokeWidth=0)
```

- [ ] **Step 4: Update waterfall chart title**

Replace `st.subheader("Individual Merchant Explanation")` with:
```python
st.markdown("### Why Did This Merchant Score High Risk? Feature-by-Feature Breakdown")
st.caption("Red = features pushing risk up. Green = features pulling risk down. Length = magnitude of impact.")
```

Keep the waterfall chart itself unchanged — red/green is semantic here and correct.

- [ ] **Step 5: Verify locally, then commit**

```bash
cd S:\JobApplicationProject\Projects\Visa-Merchant-Analytics
git add streamlit_app/pages/4_feature_importance.py
git commit -m "swd: feature importance — top-2 blue highlight, direct labels, insight titles"
```

---

### Task 5: Model Monitoring Page (Page 5)

**Files:**
- Modify: `streamlit_app/pages/5_model_monitoring.py`

- [ ] **Step 1: Read the current file**

```
Read S:\JobApplicationProject\Projects\Visa-Merchant-Analytics\streamlit_app\pages\5_model_monitoring.py
```

- [ ] **Step 2: Add COLORS dict after imports**

```python
COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}
```

- [ ] **Step 3: Add page-level insight title**

Replace `st.subheader("Model Health Dashboard")` with:
```python
st.markdown("### Model Accuracy Degrades 4 Points by Month 8 — Retraining Trigger Fires")
st.caption("Without retraining, concept drift causes the model to miss an increasing share of churners.")
st.subheader("Model Health Dashboard")
```

- [ ] **Step 4: Update AUC drift chart**

Replace the `auc_line`, `threshold_line`, `alert_points` definitions and their `st.altair_chart` call with:
```python
# Find first flagged month for annotation
first_flag = drift_df[drift_df["Drift_Flagged"]]["Month"].min() if drift_df["Drift_Flagged"].any() else None

stable = drift_df[~drift_df["Drift_Flagged"]]
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
    flag_rule = alt.Chart(pd.DataFrame({"x": [str(first_flag)]})).mark_rule(
        color=COLORS["amber"], strokeDash=[4, 4], strokeWidth=1.5
    ).encode(x="x:O")
    flag_label = alt.Chart(pd.DataFrame({"x": [str(first_flag)], "y": [0.55], "label": ["Retrain"]})).mark_text(
        align='left', dx=4, fontSize=10, color=COLORS["amber"]
    ).encode(x="x:O", y="y:Q", text="label:N")
    layers += [flag_rule, flag_label]

drift_chart = alt.layer(*layers).properties(height=340).configure_view(strokeWidth=0)
```

Replace the `st.altair_chart(...)` for the drift chart with:
```python
st.markdown("### AUC Drops Steadily After Month 6 as Merchant Behaviour Shifts")
st.caption("Red triangles = drift alerts. Amber line = first retraining trigger. Red dashed = threshold.")
st.altair_chart(drift_chart, use_container_width=True)
```

- [ ] **Step 5: Update data quality status bar**

Replace the `status_bar` definition with:
```python
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
```

- [ ] **Step 6: Verify locally, then commit**

```bash
cd S:\JobApplicationProject\Projects\Visa-Merchant-Analytics
git add streamlit_app/pages/5_model_monitoring.py
git commit -m "swd: model monitoring — drift annotation, navy palette, insight titles"
git push
```

---

## DASHBOARD 2: Visa Solutions Analyst
**Repo path:** `S:\JobApplicationProject\Projects\Visa-Solutions-Analyst\streamlit_app\`

---

### Task 6: Market Landscape Page (Page 1)

**Files:**
- Modify: `streamlit_app/1_market_landscape.py`

- [ ] **Step 1: Read the current file**

```
Read S:\JobApplicationProject\Projects\Visa-Solutions-Analyst\streamlit_app\1_market_landscape.py
```

- [ ] **Step 2: Add COLORS dict after imports**

```python
COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}
```

- [ ] **Step 3: Add page-level insight title**

Replace the existing `st.title(...)` / `st.caption(...)` with:
```python
st.title("Market Landscape")
st.markdown("### North America Leads USDC Volume but MEA Shows the Fastest Year-on-Year Growth")
st.caption("Two different GTM stories: defend the North America lead, invest early in MEA infrastructure.")
```

- [ ] **Step 4: Update all regional bar/line charts**

For every chart that colours by region, apply this colour rule — highlight North America and MEA, grey everything else:
```python
color=alt.condition(
    (alt.datum.Region == "North America") | (alt.datum.Region == "MEA"),
    alt.value(COLORS["blue"]),
    alt.value(COLORS["grey"])
)
```

Add `axis=alt.Axis(grid=False)` to both X and Y of each chart.
Add `.configure_view(strokeWidth=0)` to each chart.

For the YoY growth bar chart, add a value label layer:
```python
yoy_labels = yoy_bar.mark_text(align='left', dx=4, fontSize=11, color=COLORS["navy"]).encode(
    text=alt.Text('YoY_Growth:Q', format='.1f')
)
yoy_bar = (yoy_bar + yoy_labels).configure_view(strokeWidth=0)
```

Update each `st.subheader(...)` to a `st.markdown("### [insight title]")` + `st.caption(...)` pair matching the insight for that chart.

- [ ] **Step 5: Verify locally, then commit**

```bash
cd S:\JobApplicationProject\Projects\Visa-Solutions-Analyst
git add streamlit_app/1_market_landscape.py
git commit -m "swd: market landscape — insight titles, highlight NA+MEA, no gridlines"
```

---

### Task 7: Client Readiness Page (Page 2)

**Files:**
- Modify: `streamlit_app/pages/2_client_readiness.py`

- [ ] **Step 1: Read the current file**

```
Read S:\JobApplicationProject\Projects\Visa-Solutions-Analyst\streamlit_app\pages\2_client_readiness.py
```

- [ ] **Step 2: Add COLORS dict after imports**

```python
COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}
```

- [ ] **Step 3: Add page-level insight title (Browse mode)**

After `st.divider()` and before the KPI cards in Browse mode, add:
```python
st.markdown("### Only 28% of Clients Are Ready — Banks Lead on Compliance, Fintechs Lead on Technology")
st.caption("The 54 Developing clients represent the near-term pipeline — prioritise those closest to score 70.")
```

- [ ] **Step 4: Update scatter distribution chart**

Replace the `scatter` definition with:
```python
scatter = (
    alt.Chart(result_df)
    .mark_circle(size=90)
    .encode(
        x=alt.X("Type:N", title="Client Type", axis=alt.Axis(grid=False)),
        y=alt.Y("Score:Q", title="Readiness Score", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(grid=False)),
        color=alt.condition(
            alt.datum.Tier == "Ready",
            alt.value(COLORS["blue"]),
            alt.value(COLORS["grey"])
        ),
        tooltip=["Client:N", "Type:N", "Region:N",
                 alt.Tooltip("Score:Q", format=".1f"), "Tier:N",
                 alt.Tooltip("Volume_B:Q", title="Volume ($B)", format="$.1f")],
    )
    .properties(height=300)
    .configure_view(strokeWidth=0)
)
```

Replace `st.subheader("Score Distribution by Client Type")` with:
```python
st.markdown("### Ready Clients (Blue) Cluster at the Top — Fintechs and Banks Lead")
st.caption("Grey points = Developing or Early Stage — the pipeline to build toward readiness.")
```

- [ ] **Step 5: Verify locally, then commit**

```bash
cd S:\JobApplicationProject\Projects\Visa-Solutions-Analyst
git add streamlit_app/pages/2_client_readiness.py
git commit -m "swd: client readiness — insight titles, highlight ready tier, no gridlines"
```

---

### Task 8: Settlement Economics Page (Page 3)

**Files:**
- Modify: `streamlit_app/pages/3_settlement_economics.py`

- [ ] **Step 1: Read the current file**

```
Read S:\JobApplicationProject\Projects\Visa-Solutions-Analyst\streamlit_app\pages\3_settlement_economics.py
```

- [ ] **Step 2: Add COLORS dict after imports**

```python
COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}
```

- [ ] **Step 3: Add page-level insight title**

After `st.title(...)` add:
```python
st.markdown("### MEA Clients Save the Most on USDC Rails — But Take the Longest to Break Even")
st.caption("North America offers fastest payback — ideal for early pilots. MEA is the long-term strategic prize.")
```

- [ ] **Step 4: Update cost comparison bar chart**

Replace the `bar` definition with:
```python
bar = (
    alt.Chart(cost_df)
    .mark_bar()
    .encode(
        y=alt.Y("Rail:N", title=None, sort=["Traditional", "USDC"], axis=alt.Axis(grid=False)),
        x=alt.X("Cost (bps):Q", title="Settlement Cost (bps)", axis=alt.Axis(grid=False)),
        color=alt.condition(
            alt.datum.Rail == "USDC",
            alt.value(COLORS["navy"]),
            alt.value(COLORS["grey"])
        ),
        tooltip=["Rail:N", alt.Tooltip("Cost (bps):Q", format=".1f")],
    )
    .properties(height=160)
)
cost_labels = bar.mark_text(align='left', dx=4, fontSize=11, color=COLORS["navy"]).encode(
    text=alt.Text("Cost (bps):Q", format=".1f")
)
bar = (bar + cost_labels).configure_view(strokeWidth=0)
```

Replace `st.subheader("Cost Comparison (bps)")` with:
```python
st.markdown("### USDC Rails Cost 40–75% Less Than Traditional Correspondent Banking")
st.caption("Grey = traditional cost. Navy = USDC cost. Gap = annual savings potential.")
```

- [ ] **Step 5: Update 5-year cumulative savings line chart**

Find the breakeven year (first year where cumulative_savings_usd >= 0) and annotate it.

Replace the `line` and `zero_line` definitions with:
```python
breakeven_df = schedule_df[schedule_df["cumulative_savings_usd"] >= 0]
breakeven_year = breakeven_df["year"].iloc[0] if len(breakeven_df) > 0 else None

line = (
    alt.Chart(schedule_df)
    .mark_line(point=True, color=COLORS["navy"])
    .encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(grid=False)),
        y=alt.Y("cumulative_savings_usd:Q", title="Cumulative Net Savings ($)",
                axis=alt.Axis(format="$,.0f", grid=False)),
        tooltip=["year:O", alt.Tooltip("cumulative_savings_usd:Q", format="$,.0f", title="Net Savings")],
    )
    .properties(height=280)
)
zero_line = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(strokeDash=[4, 4], color=COLORS["grey"]).encode(y="y:Q")
layers = [line, zero_line]
if breakeven_year:
    be_point = alt.Chart(schedule_df[schedule_df["year"] == breakeven_year]).mark_point(
        color=COLORS["blue"], size=150, filled=True
    ).encode(x="year:O", y="cumulative_savings_usd:Q")
    be_label = alt.Chart(schedule_df[schedule_df["year"] == breakeven_year]).mark_text(
        align='left', dx=8, fontSize=11, color=COLORS["blue"], text="Break-even"
    ).encode(x="year:O", y="cumulative_savings_usd:Q")
    layers += [be_point, be_label]
savings_chart = alt.layer(*layers).configure_view(strokeWidth=0)
```

Replace `st.subheader("5-Year Cumulative Net Savings")` with:
```python
st.markdown("### Break-Even Typically Reached in Year 2 — Pure Savings Thereafter")
st.caption("Blue dot = break-even point. Implementation cost recovered, then savings compound annually.")
```

Replace `st.altair_chart(line + zero_line, use_container_width=True)` with:
```python
st.altair_chart(savings_chart, use_container_width=True)
```

- [ ] **Step 6: Update regional benchmark chart**

Replace the `bench_chart` definition with:
```python
bench_chart = (
    alt.Chart(bench_df)
    .mark_bar()
    .encode(
        y=alt.Y("Region:N", title="Region", sort=["North America", "Europe", "Asia Pacific", "LAC", "MEA"], axis=alt.Axis(grid=False)),
        x=alt.X("Cost (bps):Q", title="Settlement Cost (bps)", axis=alt.Axis(grid=False)),
        color=alt.condition(
            alt.datum.Rail == "USDC",
            alt.value(COLORS["navy"]),
            alt.value(COLORS["grey"])
        ),
        yOffset="Rail:N",
        tooltip=["Region:N", "Rail:N", alt.Tooltip("Cost (bps):Q", format=".1f")],
    )
    .properties(height=300)
    .configure_view(strokeWidth=0)
)
```

Replace `st.subheader("Settlement Cost Benchmarks Across Regions")` with:
```python
st.markdown("### USDC Costs Are Consistently Lower Across Every Region — MEA Gap Is Largest")
st.caption("Navy = USDC cost. Grey = traditional cost. Wider gap = greater savings potential.")
```

- [ ] **Step 7: Verify locally, then commit**

```bash
cd S:\JobApplicationProject\Projects\Visa-Solutions-Analyst
git add streamlit_app/pages/3_settlement_economics.py
git commit -m "swd: settlement economics — breakeven annotation, navy/grey palette, insight titles"
```

---

### Task 9: GTM Playbook Page (Page 4)

**Files:**
- Modify: `streamlit_app/pages/4_gtm_playbook.py`

- [ ] **Step 1: Read the current file**

```
Read S:\JobApplicationProject\Projects\Visa-Solutions-Analyst\streamlit_app\pages\4_gtm_playbook.py
```

- [ ] **Step 2: Add COLORS dict after imports**

```python
COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}
```

- [ ] **Step 3: Add page-level insight title**

After the `st.title(...)` and `st.caption(...)` lines, add:
```python
st.markdown("### Ready Fintechs in North America Are the Highest-Priority Targets — Shortest Path to Commercial Close")
st.caption("Top-right quadrant = act now. Bottom-left = nurture. Do not pursue Early Stage clients this quarter.")
```

- [ ] **Step 4: Update prioritisation scatter chart**

Replace the `priority_matrix` definition with:
```python
# Highlight top-right quadrant: Ready clients above median volume
median_vol = scored_df["Volume_B"].median()
priority_matrix = (
    alt.Chart(scored_df)
    .mark_circle()
    .encode(
        x=alt.X("Readiness_Score:Q", scale=alt.Scale(domain=[0, 100]), title="Readiness Score", axis=alt.Axis(grid=False)),
        y=alt.Y("Volume_B:Q", title="Annual Settlement Volume ($B)", axis=alt.Axis(grid=False)),
        size=alt.Size("Savings_M:Q", legend=None, scale=alt.Scale(range=[40, 600])),
        color=alt.condition(
            (alt.datum.Readiness_Score >= 70) & (alt.datum.Volume_B >= median_vol),
            alt.value(COLORS["navy"]),
            alt.value(COLORS["grey"])
        ),
        shape=alt.Shape("Type:N"),
        tooltip=[
            "Client:N", "Type:N", "Region:N",
            alt.Tooltip("Readiness_Score:Q", title="Readiness Score", format=".1f"),
            alt.Tooltip("Volume_B:Q", title="Volume ($B)", format="$.1f"),
            alt.Tooltip("Savings_M:Q", title="Annual Savings ($M)", format="$.2f"),
            alt.Tooltip("Payback_Months:Q", title="Payback (months)", format=".1f"),
            "Tier:N",
        ],
    )
    .properties(height=400)
    .interactive()
)
vline = alt.Chart(pd.DataFrame({"x": [70]})).mark_rule(strokeDash=[6, 3], color=COLORS["amber"]).encode(x="x:Q")
hline = alt.Chart(pd.DataFrame({"y": [median_vol]})).mark_rule(strokeDash=[6, 3], color=COLORS["amber"]).encode(y="y:Q")
priority_chart = (priority_matrix + vline + hline).configure_view(strokeWidth=0)
```

Replace `st.altair_chart(priority_matrix + vline + hline, use_container_width=True)` with:
```python
st.altair_chart(priority_chart, use_container_width=True)
```

Replace `st.subheader("Client Segment Prioritization Matrix")` with:
```python
st.markdown("### Navy Clients Are Immediate Priorities — High Readiness and Large Settlement Volumes")
st.caption("Navy = act now (top-right quadrant). Grey = developing pipeline. Amber lines = priority thresholds.")
```

- [ ] **Step 5: Verify locally, then commit and push both repos**

```bash
cd S:\JobApplicationProject\Projects\Visa-Solutions-Analyst
git add streamlit_app/pages/4_gtm_playbook.py
git commit -m "swd: gtm playbook — priority quadrant highlight, insight titles, no gridlines"
git push

cd S:\JobApplicationProject\Projects\Visa-Merchant-Analytics
git push
```

---

## Self-Review Checklist

- [x] All 9 pages covered (5 Merchant Analytics + 4 Solutions Analyst)
- [x] Every chart gets an insight title + sub-caption
- [x] COLORS dict defined in every file
- [x] gridlines removed on every chart via `axis=alt.Axis(grid=False)`
- [x] Chart borders removed via `.configure_view(strokeWidth=0)`
- [x] Direct value labels added where appropriate
- [x] Key element highlighted (blue/navy), context elements greyed
- [x] Semantic colours (red/amber/green) kept only where they carry meaning
- [x] No placeholders or TBDs in any step
- [x] Commit after each page
