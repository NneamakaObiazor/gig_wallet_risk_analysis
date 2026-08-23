# African Gig-Economy & Digital Wallet Risk — EDA, Verification & BI Model

A full analytics workflow — Python EDA, statistical claim verification, a
5-page Power BI dashboard, and a polished analytical report — built against
a 50,000-transaction synthetic dataset covering gig-worker digital wallet
activity across Nigeria, Kenya, Ghana, and South Africa (Jan 2023–Dec 2024).

The brief that shipped with this dataset proposed six specific fraud/risk
patterns (channel effects, country concentration, new-account risk, gig
segment disputes, velocity correlation, month-end spikes). **We tested all
six directly against the data and none held up** — every categorical split
and correlation came back statistically indistinguishable from noise
(p > 0.05 in every case, most p > 0.4). Fraud, dispute, and reversal flags
sit at a uniform ~50% no matter how you slice the data.

This repo documents that verification process end-to-end, rather than
writing a report that assumes the brief's claims are true, and carries the
same verdict into the live Power BI file itself so the report and dashboard
never disagree. See [`report/Analytical_Report.docx`](report/Analytical_Report.docx)
for the full write-up, or [`scripts/verification_tests.py`](scripts/verification_tests.py)
to reproduce the statistics yourself in under 10 seconds.

## Why this matters (the "AI-proofing" angle)

A common failure mode when an LLM or analyst is handed a brief with
pre-written "expected findings" is to produce a report that simply restates
those findings with cosmetic numbers attached — regardless of what the data
actually shows. This project is built to resist that:

- Every claim in the original brief is run through an explicit statistical
  test (chi-square test of independence for categorical splits, Pearson
  correlation for the continuous velocity claim), with the test, statistic,
  p-value, and verdict shown side-by-side with the original claim.
- The verification script (`scripts/verification_tests.py`) is a standalone,
  re-runnable harness — not just numbers pasted into a report — so the
  conclusion is auditable and reproducible against any future re-extract of
  this schema.
- The dashboard's closing page (**Recommendations & Verification**) surfaces
  the exact same verdict table live in Power BI, sourced from
  `powerbi_model/Claim_Verification.csv` — nobody clicking through the
  dashboard alone can miss that the brief's hypotheses weren't confirmed.
- Where the data does show something real (e.g. the mechanical 0.77
  correlation between `fraud_loss_usd` and `is_fraud_flagged`, or the
  `week_number` column being 100% null), it's called out and explained
  rather than smoothed over.

## Repository structure

```
.
├── README.md                          ← you are here
├── data/                               Original source CSVs (as provided)
│   ├── dim_channel.csv
│   ├── dim_date_updated.csv
│   ├── dim_market.csv
│   ├── dim_worker.csv
│   └── fact_transactions_Updated_.csv
├── scripts/
│   ├── explore.py                      Initial structural EDA (schema, nulls, dtypes)
│   ├── build_charts.py                 Generates all report/dashboard charts
│   └── verification_tests.py           Reusable statistical claim-verification harness
├── charts/                             10 PNG charts (300dpi-ready) used in the report
├── report/
│   ├── Analytical_Report.docx          Full analytical report (Word)
│   └── Analytical_Report.pdf           Same report, rendered to PDF
└── powerbi_model/
    ├── dim_worker.csv                  Cleaned star-schema tables for Power BI import
    ├── dim_channel.csv
    ├── dim_market.csv
    ├── dim_date.csv                    week_number defect repaired (was 100% null)
    ├── fact_transactions.csv
    ├── Claim_Verification.csv          Feeds the dashboard's verdict table (Page 5)
    ├── DAX_measures.txt                Full measure library incl. significance guardrails
    └── PowerBI_Build_Guide.md          Page-by-page report build spec
```

## Dataset

| Table | Rows | Grain |
|---|---|---|
| `dim_worker` | 5,000 | 1 row per gig worker (segment, KYC tier, tenure, risk score, demographics) |
| `dim_channel` | 12 | 1 row per channel configuration (type × subtype) |
| `dim_market` | 4 | 1 row per country (Nigeria, Kenya, Ghana, South Africa) |
| `dim_date` | 731 | 1 row per calendar day, 2023-01-01 to 2024-12-31 |
| `fact_transactions` | 50,000 | 1 row per transaction (13 types, 8 outcome states) |

**Data quality:** zero nulls in the fact table, zero duplicate transaction
IDs, 100% referential integrity across all four dimension tables. The one
defect found was `dim_date.week_number` (100% null in the source file),
fixed with a true ISO 8601 week-number formula implemented directly in
Power Query (see `powerbi_model/DAX_measures.txt` for the exact M code, or
use the equivalent one-line `ISOWEEKNUM()` DAX calculated column if you'd
rather not touch the query layer).

## Key findings

| # | Claim | Result | p-value |
|---|---|---|---|
| 1 | USSD shows 2.3x higher fraud rate than app channel | USSD 51.2% vs App 50.3% | 0.13 |
| 2 | Nigeria + Kenya drive 70% of fraud volume | Each country ≈ 25% of volume | 0.51 |
| 3 | New accounts (<90d) show 3x higher fraud rate | 51.2% vs 49.9% (oldest cohort) | 0.65 |
| 4 | Market traders have highest dispute rate | Rank 10th of 15 segments | 0.06 |
| 5 | High velocity score correlates with fraud/reversal | r ≈ 0.00 in both cases | — |
| 6 | Month-end spikes in cash-out/reversal | Both within sampling noise | 0.14 |

**Zero of six claims confirmed.** Full methodology, all charts, and the
complete statistical detail are in the analytical report.

What the data *does* support: total transaction value of **$24.98M**, a flat
**50.3%** fraud-flag rate across the board (**$12.56M** in flagged loss
exposure), a near-perfectly even worker/segment/channel/country mix, and
internal consistency in every relationship that's mechanically defined
(e.g. `fraud_loss_usd` is deterministically $0 for non-flagged transactions).
Details and interpretation in Section 4 of the report.

## The Power BI dashboard

Five pages:

| Page | Purpose |
|---|---|
| Home | Title, navigation |
| Executive Overview | KPIs, monthly trend, no-seasonality callout |
| Risk Analysis | Fraud/loss rate by risk band, channel, segment |
| Risk & Fraud Exposure | Fraud rate by tenure/KYC/segment, country×channel heatmap |
| **Recommendations & Verification** | The "0 of 6" headline stat, the full claim-verification table, and the report's recommendations — built directly from `Claim_Verification.csv` and Section 5 of the analytical report |

To rebuild it from scratch (or extend it), start with
[`powerbi_model/PowerBI_Build_Guide.md`](powerbi_model/PowerBI_Build_Guide.md),
which includes exact DAX, the Power Query fix for `week_number`, and a
page-by-page visual spec.

## Reproducing the analysis

```bash
pip install pandas numpy scipy matplotlib seaborn

# Full structural EDA
python scripts/explore.py

# Regenerate all charts
python scripts/build_charts.py

# Re-run the statistical claim-verification battery
python scripts/verification_tests.py --data-dir ./data
```

## Recommendations

1. **Do not build risk rules from this dataset** — no channel, country,
   tenure, or segment split carries signal; a model trained on it would
   perform at the base rate.
2. **Treat this as a schema/pipeline fixture**, not a source for policy or
   model-training decisions, until its provenance is confirmed.
3. **If a production-representative extract becomes available**, re-run
   `verification_tests.py` unchanged against it before drafting any policy,
   then update `Claim_Verification.csv` and the dashboard's "0 of 6" card to
   match — neither recalculates automatically, by design (see
   `DAX_measures.txt`).
4. **`week_number` is already fixed** at the Power Query layer, so it holds
   up under a normal data refresh.

---
*Currency: USD throughout. See
`report/Analytical_Report.pdf` Section 4.4 for a note on the FX-rate
reference data in `dim_market`, which does not match real-world rates for
these currencies and should not be used for `amount_local` conversions.*
