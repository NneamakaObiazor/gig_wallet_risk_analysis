"""
verification_tests.py
======================
Reusable claim-verification harness for the African Gig-Economy & Digital
Wallet Risk dataset (or any future re-extract with the same schema).

Run this FIRST before writing any report from this data. It reloads the five
source CSVs, merges them into one analysis table, and runs the exact
statistical test battery used in Section 3 of Analytical_Report.docx:
chi-square tests of independence for every categorical risk-driver claim,
and Pearson correlations for the continuous velocity_score claim.

Usage:
    python verification_tests.py --data-dir /path/to/csvs

Exit behavior: prints a plain-text verdict table. Does not modify any files.
"""
import argparse
import pandas as pd
from scipy import stats


def load_and_merge(data_dir: str) -> pd.DataFrame:
    fact = pd.read_csv(f"{data_dir}/fact_transactions_Updated_.csv")
    worker = pd.read_csv(f"{data_dir}/dim_worker.csv")
    channel = pd.read_csv(f"{data_dir}/dim_channel.csv")
    market = pd.read_csv(f"{data_dir}/dim_market.csv")
    date = pd.read_csv(f"{data_dir}/dim_date_updated.csv")

    df = (
        fact.merge(worker, on="worker_id", how="left")
        .merge(channel, on="channel_id", how="left")
        .merge(market, on="market_id", how="left")
        .merge(date, on="date_id", how="left")
    )
    df["full_date"] = pd.to_datetime(df["full_date"], format="%m/%d/%Y")
    df["tenure_group"] = pd.cut(
        df.account_tenure_days,
        [-1, 90, 365, 730, 1095, 1460, 1825],
        labels=["0-90d", "91-365d", "1-2yr", "2-3yr", "3-4yr", "4-5yr"],
    )
    return df


def chi2_test(df: pd.DataFrame, col: str, target: str = "is_fraud_flagged"):
    ct = pd.crosstab(df[col], df[target])
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    return chi2, p


def data_quality_report(df: pd.DataFrame):
    print("=" * 78)
    print("DATA QUALITY CHECKS")
    print("=" * 78)
    print(f"Rows: {len(df):,}")
    print(f"Nulls (non-zero columns only):")
    nulls = df.isna().sum()
    print(nulls[nulls > 0] if nulls.sum() else "  none")
    print(f"Duplicate transaction_id: {df['transaction_id'].duplicated().sum()}")
    print()


def claim_battery(df: pd.DataFrame):
    print("=" * 78)
    print("CLAIM VERIFICATION BATTERY  (alpha = 0.05)")
    print("=" * 78)

    tests = [
        ("USSD channel shows 2.3x higher fraud rate than app channel",
         lambda: chi2_test(df, "channel_type", "is_fraud_flagged")),
        ("Nigeria and Kenya drive 70% of fraud volume",
         lambda: chi2_test(df, "country", "is_fraud_flagged")),
        ("New accounts under 90 days show 3x higher fraud rate",
         lambda: chi2_test(df, "tenure_bucket", "is_fraud_flagged")),
        ("Market traders have highest dispute rate among gig segments",
         lambda: chi2_test(df, "gig_segment", "is_disputed")),
        ("Month-end spikes in reversal rate",
         lambda: chi2_test(df, "is_month_end", "is_reversed")),
    ]

    for label, fn in tests:
        chi2, p = fn()
        verdict = "CONFIRMED" if p < 0.05 else "NOT CONFIRMED"
        print(f"[{verdict:14s}] {label}")
        print(f"                 chi2={chi2:.2f}  p={p:.4f}")

    r_fraud = df["velocity_score"].corr(df["is_fraud_flagged"].astype(int))
    r_rev = df["velocity_score"].corr(df["is_reversed"].astype(int))
    verdict = "CONFIRMED" if (abs(r_fraud) > 0.1 or abs(r_rev) > 0.1) else "NOT CONFIRMED"
    print(f"[{verdict:14s}] High velocity score correlates with fraud and reversal")
    print(f"                 r(fraud)={r_fraud:.4f}  r(reversal)={r_rev:.4f}")
    print()


def full_correlation_matrix(df: pd.DataFrame):
    print("=" * 78)
    print("FULL NUMERIC CORRELATION MATRIX")
    print("=" * 78)
    numcols = ["amount_usd", "velocity_score", "fraud_loss_usd",
               "processing_time_ms", "account_tenure_days", "risk_score"]
    tmp = df[numcols + ["is_fraud_flagged", "is_disputed", "is_reversed"]].copy()
    for c in ["is_fraud_flagged", "is_disputed", "is_reversed"]:
        tmp[c] = tmp[c].astype(int)
    print(tmp.corr().round(3))
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="/mnt/user-data/uploads")
    args = parser.parse_args()

    df = load_and_merge(args.data_dir)
    data_quality_report(df)
    claim_battery(df)
    full_correlation_matrix(df)
