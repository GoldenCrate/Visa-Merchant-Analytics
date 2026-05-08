# SWD Treatment — Both Visa Dashboards
**Date:** 2026-05-08
**Scope:** Visa Merchant Analytics + Visa Solutions Analyst dashboards
**Approach:** Full SWD Treatment (Knaflic, Storytelling with Data)

---

## Goals

Apply Storytelling with Data best practices to both portfolio dashboards so that a Visa hiring manager reading the portfolio sees an analyst who thinks in insights, not just charts. No structural changes — visual presentation only.

---

## Colour System

Applied identically across both dashboards via a shared constant at the top of each file.

| Role | Hex | Usage |
|---|---|---|
| Navy (primary) | `#1e3a5f` | Headings, the key bar/point per chart |
| Blue (accent) | `#2563eb` | Single highlighted element per chart |
| Grey (context) | `#9ca3af` | All non-highlighted bars/points |
| Red (alert) | `#dc2626` | High risk, churn, drift alerts only |
| Amber (warning) | `#d97706` | Medium risk, developing tier |
| Green (success) | `#16a34a` | Low risk, ready tier — only where semantically required |

---

## Chart Pattern

Every chart follows this exact template:

```
[Bold insight title — states the finding, not the chart type]
[One-line sub-caption in grey — the "so what" or recommended action]
[Altair chart]
  - Grey (#9ca3af) for all context bars/points
  - Blue (#2563eb) or Navy (#1e3a5f) for the key highlighted element
  - No chart border (view strokeWidth = 0)
  - No gridlines (grid=False on both axes)
  - Direct value labels on bars (no legend where avoidable)
  - Minimal axis ticks — only meaningful intervals
```

---

## Page-by-Page Spec

### Visa Merchant Analytics

#### Page 1 — Overview
- **Insight title:** "Manual Integration Drives 2× the Churn of Fully Integrated Merchants"
- **Sub-caption:** "Integration type is the single most actionable lever for reducing portfolio churn."
- **Changes:**
  - Volume by Category bar: grey all bars, blue the highest-volume category
  - Churn by Region bar: grey all, blue MEA (highest), add % value labels
  - Dispute Rate histogram: navy bars, remove x-axis minor ticks
  - Churn by Integration bar: grey Integrated, amber Semi-integrated, red Manual — kept semantic since it tells a risk story

#### Page 2 — Segmentation
- **Insight title:** "Champions Are 11% of Merchants but Drive the Majority of Portfolio Volume"
- **Sub-caption:** "Protecting this segment is the highest-ROI retention investment."
- **Changes:**
  - Scatter: grey Growth Stars and Stable Partners, navy Champions, red At-Risk
  - Dispute Rate bar: same segment colours, remove legend, label bars directly
  - Churn Rate bar: same
  - Segment profiles table: bold the Champions row

#### Page 3 — Churn Risk
- **Insight title:** "The Model Identifies High-Risk Merchants with 83% Recall — Catching 4 in 5 Before They Leave"
- **Sub-caption:** "AUC above 0.80 — meaningfully above random; precision/recall tuned for early intervention."
- **Changes:**
  - ROC curve: navy line, annotate the operating point with a blue dot + label
  - Probability distribution: navy bars, blue vertical threshold line with label, remove grey background
  - Live scorer output: colour the risk tier badge navy/amber/red appropriately

#### Page 4 — Feature Importance
- **Insight title:** "Dispute Rate and Volume Decline Explain Most of the Model's Churn Predictions"
- **Sub-caption:** "These two features are the earliest warning signals — monitor them weekly."
- **Changes:**
  - Global importance bar: top 2 bars in blue (#2563eb), remaining in grey (#9ca3af), remove legend
  - Per-merchant waterfall: keep red/green semantic (increases/reduces risk) — meaning depends on direction
  - Add value labels on the global importance bars

#### Page 5 — Model Monitoring
- **Insight title:** "Model Accuracy Degrades 4 Points by Month 8 — Retraining Trigger Fires"
- **Sub-caption:** "Without retraining, the model loses predictive power as merchant behaviour shifts."
- **Changes:**
  - AUC drift line: navy line, red triangle markers at flagged months, grey the stable period with a shaded band annotation
  - Add a vertical annotation line at the first flagged month with a text label
  - Data quality status bars: green/amber, remove border

---

### Visa Solutions Analyst

#### Page 1 — Market Landscape
- **Insight title:** "North America Leads USDC Volume but MEA Shows the Fastest Year-on-Year Growth"
- **Sub-caption:** "Two different GTM stories: defend the North America lead, invest early in MEA infrastructure."
- **Changes:**
  - All regional bar/line charts: grey all regions, blue North America and MEA
  - KPI cards: navy metric values, remove coloured backgrounds
  - YoY growth chart: annotate MEA bar with value label

#### Page 2 — Client Readiness
- **Insight title:** "Only 28% of Clients Are Ready — Banks Lead on Compliance, Fintechs Lead on Technology"
- **Sub-caption:** "The 54 Developing clients represent the near-term pipeline — prioritise those closest to 70."
- **Changes:**
  - Scorecard table: grey Developing/Early Stage rows, navy Ready rows
  - Scatter distribution: grey all, blue the Ready tier
  - KPI cards: navy values

#### Page 3 — Settlement Economics
- **Insight title:** "MEA Clients Save the Most on USDC Rails — But Take 18 Months to Break Even"
- **Sub-caption:** "North America offers fastest payback — ideal for early pilots. MEA is the long-term prize."
- **Changes:**
  - Cost comparison bars: grey Traditional, navy USDC
  - 5-year cumulative line: navy line, annotate breakeven point with a dot + "Break-even" label
  - Regional benchmark chart: grey Traditional bars, blue USDC bars

#### Page 4 — GTM Playbook
- **Insight title:** "Ready Fintechs in North America Are the Highest-Priority Targets — Shortest Path to Close"
- **Sub-caption:** "Top-right quadrant = act now. Bottom-left = nurture. Do not pursue Early Stage clients this quarter."
- **Changes:**
  - Prioritisation scatter: grey all, navy the top-right quadrant points, annotate quadrant with text labels
  - Quadrant reference lines: make dashed lines more visible with a label ("Priority threshold")
  - Tier playbook section: no chart changes — text only

---

## What Does NOT Change

- Page structure and navigation
- ML models, scoring functions, data
- AI pitch generator and Q&A chat
- Snowflake connection and data loader
- pytest tests
- Streamlit page config or layout

---

## Implementation Notes

- Define `COLORS` dict at the top of each page file — no shared module needed
- Use Altair `configure_view(strokeWidth=0)` to remove chart borders
- Use `axis=alt.Axis(grid=False)` on both x and y
- For direct value labels: use `mark_text` layer with `dx` offset
- Insight titles go in `st.markdown` with `###` heading above each `st.altair_chart` call
- Sub-captions go in `st.caption` immediately below the heading, before the chart
