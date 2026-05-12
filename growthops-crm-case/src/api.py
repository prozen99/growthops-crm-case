from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException

try:
    from .config import CAMPAIGN_METRICS_FILE, DATA_QUALITY_REPORT_FILE, LEAD_SCORES_FILE
except ImportError:
    from config import CAMPAIGN_METRICS_FILE, DATA_QUALITY_REPORT_FILE, LEAD_SCORES_FILE


app = FastAPI(title="GrowthOps CRM Case Results API")

MISSING_FILE_DETAIL = "Processed CSV file not found. Run `python src/main.py` first."


def _read_processed_csv(file_path: Path) -> list[dict[str, Any]]:
    """Read a processed CSV file and return JSON-safe row dictionaries."""
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=MISSING_FILE_DETAIL)

    frame = pd.read_csv(file_path, keep_default_na=False)
    frame = frame.astype(object).where(pd.notna(frame), None)
    return frame.to_dict(orient="records")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/lead-scores")
def get_lead_scores() -> list[dict[str, Any]]:
    return _read_processed_csv(LEAD_SCORES_FILE)


@app.get("/lead-scores/{lead_id}")
def get_lead_score(lead_id: str) -> dict[str, Any]:
    lead_scores = _read_processed_csv(LEAD_SCORES_FILE)
    for lead_score in lead_scores:
        if str(lead_score.get("lead_id")) == lead_id:
            return lead_score
    raise HTTPException(status_code=404, detail=f"Lead score not found for lead_id: {lead_id}")


@app.get("/campaign-metrics")
def get_campaign_metrics() -> list[dict[str, Any]]:
    return _read_processed_csv(CAMPAIGN_METRICS_FILE)


@app.get("/data-quality-report")
def get_data_quality_report() -> list[dict[str, Any]]:
    return _read_processed_csv(DATA_QUALITY_REPORT_FILE)
