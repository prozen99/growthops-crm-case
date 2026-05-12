import pandas as pd

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


def test_suspicious_bot_behavior_lead_becomes_manual_review():
    campaigns = pd.DataFrame([{"campaign_id": "C1", "utm_code": "utm"}])
    leads = pd.DataFrame(
        [
            {
                "lead_id": "L1",
                "email": "bot@example.com",
                "company_name": "Bot Co",
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
                "event_id": f"E{i:02d}",
                "lead_id": "L1",
                "campaign_id": "C1",
                "event_type": "link_click",
                "event_time": pd.Timestamp("2026-05-10 09:00:00") + pd.Timedelta(seconds=i * 30),
            }
            for i in range(15)
        ]
    )
    conversions = pd.DataFrame(columns=["conversion_id", "lead_id", "campaign_id", "conversion_type", "conversion_time", "amount"])

    issues = validate_data(campaigns, leads, events, conversions)

    assert any(issue.issue_type == "suspicious_bot_behavior" for issue in issues)
    assert "L1" in get_manual_review_lead_ids(issues)


def test_duplicate_email_leads_become_manual_review():
    campaigns = pd.DataFrame([{"campaign_id": "C1", "utm_code": "utm"}])
    leads = pd.DataFrame(
        [
            {
                "lead_id": "L1",
                "email": "same@example.com",
                "company_name": "Same One",
                "industry": "SaaS",
                "company_size": "Enterprise",
                "job_title": "CEO",
                "source_campaign_id": "C1",
            },
            {
                "lead_id": "L2",
                "email": "same@example.com",
                "company_name": "Same Two",
                "industry": "Finance",
                "company_size": "Mid-Market",
                "job_title": "Director",
                "source_campaign_id": "C1",
            },
        ]
    )
    events = pd.DataFrame(columns=["event_id", "lead_id", "campaign_id", "event_type", "event_time"])
    conversions = pd.DataFrame(columns=["conversion_id", "lead_id", "campaign_id", "conversion_type", "conversion_time", "amount"])

    issues = validate_data(campaigns, leads, events, conversions)
    manual_review_lead_ids = get_manual_review_lead_ids(issues)

    assert {"L1", "L2"}.issubset(manual_review_lead_ids)


def test_invalid_conversion_lead_reference_is_detected():
    campaigns = pd.DataFrame([{"campaign_id": "C1", "utm_code": "utm"}])
    leads = pd.DataFrame(
        [
            {
                "lead_id": "L1",
                "email": "lead@example.com",
                "company_name": "Lead Co",
                "industry": "SaaS",
                "company_size": "Enterprise",
                "job_title": "CEO",
                "source_campaign_id": "C1",
            }
        ]
    )
    events = pd.DataFrame(columns=["event_id", "lead_id", "campaign_id", "event_type", "event_time"])
    conversions = pd.DataFrame(
        [
            {
                "conversion_id": "CV1",
                "lead_id": "L999",
                "campaign_id": "C1",
                "conversion_type": "purchase",
                "conversion_time": pd.Timestamp("2026-05-10 10:00:00"),
                "amount": 1000,
            }
        ]
    )

    issues = validate_data(campaigns, leads, events, conversions)

    assert any(issue.issue_type == "invalid_conversion_lead_reference" for issue in issues)
