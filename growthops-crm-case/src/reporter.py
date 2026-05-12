import pandas as pd

from config import CAMPAIGN_METRICS_FILE, DATA_QUALITY_REPORT_FILE, LEAD_SCORES_FILE, PROCESSED_DATA_DIR


def save_outputs(
    lead_scores: pd.DataFrame,
    campaign_metrics: pd.DataFrame,
    data_quality_report: pd.DataFrame,
) -> None:
    """Persist processed deliverables."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    lead_scores.to_csv(LEAD_SCORES_FILE, index=False, encoding="utf-8-sig")
    campaign_metrics.to_csv(CAMPAIGN_METRICS_FILE, index=False, encoding="utf-8-sig")
    data_quality_report.to_csv(DATA_QUALITY_REPORT_FILE, index=False, encoding="utf-8-sig")


def print_summary(raw_lead_count: int, lead_scores: pd.DataFrame, data_quality_report: pd.DataFrame) -> None:
    print(f"Raw leads count: {raw_lead_count}")
    print(f"Manual Review leads count: {len(lead_scores[lead_scores['lead_grade'].eq('Manual Review')])}")
    print(f"Hot leads count: {len(lead_scores[lead_scores['lead_grade'].eq('Hot')])}")
    print(f"Data quality issue count: {int(data_quality_report['count'].sum()) if not data_quality_report.empty else 0}")
    print("Output file paths:")
    print(f"- {LEAD_SCORES_FILE}")
    print(f"- {CAMPAIGN_METRICS_FILE}")
    print(f"- {DATA_QUALITY_REPORT_FILE}")
