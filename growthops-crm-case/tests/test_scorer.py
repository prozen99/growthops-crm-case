import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from scorer import grade_score, score_leads


def test_demo_request_increases_score_for_valid_lead():
    campaigns = pd.DataFrame(
        [
            {
                "campaign_id": "C1",
                "campaign_name": "Demo Campaign",
                "channel": "webinar",
                "budget": 15000,
                "utm_code": "utm_demo",
            }
        ]
    )
    leads = pd.DataFrame(
        [
            {
                "lead_id": "L1",
                "email": "buyer@example.com",
                "company_name": "Buyer Co",
                "industry": "SaaS",
                "company_size": "Enterprise",
                "job_title": "CTO",
                "source_campaign_id": "C1",
            }
        ]
    )
    events = pd.DataFrame(
        [
            {
                "event_id": "E1",
                "lead_id": "L1",
                "campaign_id": "C1",
                "event_type": "demo_request",
                "event_time": pd.Timestamp("2026-05-10 10:00:00"),
            }
        ]
    )
    conversions = pd.DataFrame(columns=["conversion_id", "lead_id", "campaign_id", "conversion_type", "conversion_time", "amount"])

    result = score_leads(leads, campaigns, events, conversions, [], set())

    assert result.loc[0, "lead_score"] > 10
    assert "데모 요청" in result.loc[0, "reason"]


def test_grade_boundaries_match_hot_warm_cold_rules():
    assert grade_score(75) == "Hot"
    assert grade_score(45) == "Warm"
    assert grade_score(44) == "Cold"
