# Power BI Report Build Guide
### African Gig-Economy & Digital Wallet Risk — Data Model & Report Spec

This sandbox cannot run Power BI Desktop itself (it's a Windows/Mac desktop
app with no headless mode), so instead of a fake `.pbix`, this folder gives
you everything needed to build the real one in under 15 minutes:

- `dim_worker.csv`, `dim_channel.csv`, `dim_market.csv`, `dim_date.csv`,
  `fact_transactions.csv` — cleaned, referentially-verified star schema
- `DAX_measures.txt` — every measure, ready to paste
- This guide — relationships, page layout, and visual-by-visual spec

## 1. Load & model (5 min)

1. **Get Data > Text/CSV**, import all five files from this folder.
2. Power BI will likely auto-detect the relationships from the `*_id`
   columns. Confirm in **Model view** that you have a clean star schema:
   `dim_worker`, `dim_channel`, `dim_market`, `dim_date` each 1-to-many into
   `fact_transactions`. All relationships should be single-direction
   (dim → fact), not bidirectional.
3. Right-click `dim_date` → **Mark as date table**, using `full_date`.
4. Add the calculated columns from `DAX_measures.txt`: `Tenure Group` and
   `Risk Band` and `Tenure Sort Order` on `dim_worker`.
5. Paste in all measures from `DAX_measures.txt`.
6. Fix `dim_date.week_number` (100% null in the source file) using either
   method documented in `DAX_measures.txt` — the Power Query custom column
   (recommended, fixes it at the source-query layer).

## 2. Report pages

### Page 1 — Executive Overview
- **KPI cards (top row):** Total Transactions · Transaction Value USD · Fraud Rate
  · Total Fraud Loss USD · Fraud Loss Rate · 
- **Line chart:** `Fraud Rate` by `dim_date[full_date]` (month) — this is the chart
  that shows there's no seasonal pattern.
  **Fraud Loss:** `Fraud Loss Rate` by `dim_date[full_date]` (month) — this is the chart
  that shows there's no seasonal pattern to financial loss.
- **Callout/text box:** plain-language note that fraud rate holds flat at ~50% across every dimension tested — Check page 5 for the statistical detail.
- **Slicers:** Year, Country, Channel Type (top of page, apply to all visuals).

### Page 2 — Geography & Channel
- **Map or bar chart:** `Total Value USD` and `Fraud Rate` by `country`
  (from `dim_market`) — use a clustered bar, not a map, since only 4
  countries exist and a map adds no resolution.
- **Bar chart:** `Fraud Rate` by `channel_type` and `channel_subtype`, with
  95% CI error bars (Power BI: use the CI Lower/Upper measures as a custom
  error-bar visual, or Deneb/error-bars-by-VIZ custom visual) and the overall
  mean as a reference line.
- **Table:** channel_type × `Is Rate Significantly Different` so viewers can
  see at a glance that nothing clears the significance bar.

### Page 3 — Worker & Segment Risk
- **Bar chart:** `Dispute Rate` by `gig_segment`, sorted descending, overall
  mean line.
- **Bar chart:** `Fraud Rate` by `Tenure Bucket`.
- **Scatter/matrix:** `risk_score` (dim_worker) vs `Fraud Rate`, bucketed
  into deciles, to visually confirm (or, here, disconfirm) any relationship.
- **Slicer:** kyc_tier, age_band, gender.

### Page 4 — Transaction Behaviour
- **Bar chart:** `Total Value USD` by `transaction_type`.
- **Stacked bar:** `transaction_outcome` distribution.
- **Clustered column:** Cash-Out share and Reversal Rate, split by
  `dim_date[is_month_end]`, to test the month-end spike claim.
- **Histogram (2 overlaid):** `velocity_score` distributions for
  fraud-flagged vs not — built as a binned calculated column + stacked
  histogram, since Power BI has no native overlaid-density visual.

### Page 5 — Recommendations & Verification (built)
Status: implemented. This page merges the original guide's separate
"Statistical Validation" and "Recommendations" concepts into one closing
page, since the recommendations only make sense read alongside the
verification that produced them.

- **Header + "0 of 6" stat card:** static text/shape, not a live measure —
  see `DAX_measures.txt` for why (chi-square isn't a native DAX aggregation).
- **Verdict table:** all 6 claims from the brief, sourced from
  `Claim_Verification.csv` in this folder (Get Data > Text/CSV, or Enter Data
  if you'd rather embed it with no external file dependency) — same content
  as Section 3 of `Analytical_Report.docx`, so the report and dashboard never
  disagree with each other.
- **Three panels:** Immediate Actions, Known Data Issues (including the
  week_number fix below), and What to Prioritize If Real Data Arrives —
  content mirrors Section 5 of the analytical report.
- Not included: a separate live correlation-matrix visual. The correlation
  findings are covered in the report (`09_correlation_heatmap.png` /
  Section 2.3) rather than duplicated as a Power BI matrix, since — like the
  chi-square results — they're a one-time statistical output, not something
  that should silently recalculate against whatever data happens to be
  loaded.

## 3. Formatting notes
- Use a consistent 2-color risk palette (e.g., navy `#1B2A4A` for neutral
  volume, coral `#E8604C` reserved only for genuinely significant risk
  findings) so color always carries meaning — don't color-code categories
  that aren't actually different.
- Every rate visual should carry its overall-mean reference line and, where
  space allows, an error bar or CI band. A bar chart of rates without an
  uncertainty band is the #1 way this kind of report misleads readers.
- Title each visual with the finding, not the field name (see the chart
  titles already used in the analytical report / `charts/` folder for the
  exact phrasing pattern: "X by Y — verdict").

## 4. Final cleanup checklist
- [ ] Page tab name "Risk & Fraaud Exposure" — typo, should read "Fraud"
- [ ] Scatter chart title "Country Fraud Severity Natrix" — typo, should
      read "Matrix"
- [ ] Consider softening "Where is the risk?" / "Who and when is fraud risk
      highest?" page subtitles slightly, since Page 5 concludes that risk
      isn't concentrated anywhere in particular — the framing question and
      the conclusion should agree once a reader reaches the last page
