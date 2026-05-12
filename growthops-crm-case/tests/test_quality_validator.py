import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from quality_validator import get_manual_review_lead_ids, validate_data


def test_missing_email_lead_becomes_manual_review():
    campaigns = pd.DataFrame([{"campaign_id": "C1", "utm_code": "utm"}])
    leads = pd.DataFrame(
        [
            {
                "lead_id": "L1",
                "email": "",
                "company_name": "No Email",
                "industry": "SaaS",
                "company_size": "Enterprise",
                "job_title": "CEO",
                "source_campaign_id": "C1",
            }
        ]
    )
    events = pd.DataFrame(columns=["event_id", "lead_id", "campaign_id", "event_type", "event_time"])
    conversions = pd.DataFrame(columns=["conversion_id", "lead_id", "campaign_id", "conversion_type", "conversion_time", "amount"])

    issues = validate_data(campaigns, leads, events, conversions)

    assert "L1" in get_manual_review_lead_ids(issues)


def test_invalid_campaign_reference_is_detected():
    campaigns = pd.DataFrame([{"campaign_id": "C1", "utm_code": "utm"}])
    leads = pd.DataFrame(
        [
            {
                "lead_id": "L1",
                "email": "lead@example.com",
                "company_name": "Bad Ref",
                "industry": "SaaS",
                "company_size": "Enterprise",
                "job_title": "CEO",
                "source_campaign_id": "C999",
            }
        ]
    )
    events = pd.DataFrame(columns=["event_id", "lead_id", "campaign_id", "event_type", "event_time"])
    conversions = pd.DataFrame(columns=["conversion_id", "lead_id", "campaign_id", "conversion_type", "conversion_time", "amount"])

    issues = validate_data(campaigns, leads, events, conversions)

    assert any(issue.issue_type == "invalid_lead_campaign_reference" for issue in issues)
