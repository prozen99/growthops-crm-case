from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

CAMPAIGNS_FILE = RAW_DATA_DIR / "campaigns.csv"
LEADS_FILE = RAW_DATA_DIR / "leads.csv"
EVENTS_FILE = RAW_DATA_DIR / "events.csv"
CONVERSIONS_FILE = RAW_DATA_DIR / "conversions.csv"

LEAD_SCORES_FILE = PROCESSED_DATA_DIR / "lead_scores.csv"
CAMPAIGN_METRICS_FILE = PROCESSED_DATA_DIR / "campaign_metrics.csv"
DATA_QUALITY_REPORT_FILE = PROCESSED_DATA_DIR / "data_quality_report.csv"

REFERENCE_DATE = "2026-05-12"
CSV_ENCODING = "utf-8-sig"
