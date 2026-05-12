import pandas as pd

from metrics import calculate_campaign_metrics


def test_conversion_rate_handles_zero_valid_leads():
    campaigns = pd.DataFrame(
        [
            {
                "campaign_id": "C1",
                "campaign_name": "Manual Review Campaign",
                "channel": "webinar",
            }
        ]
    )
    leads = pd.DataFrame(
        [
            {
                "lead_id": "L1",
                "source_campaign_id": "C1",
            }
        ]
    )
    conversions = pd.DataFrame(
        [
            {
                "conversion_id": "CV1",
                "lead_id": "L1",
                "campaign_id": "C1",
                "conversion_type": "purchase",
            }
        ]
    )
    lead_scores = pd.DataFrame([{"lead_id": "L1", "lead_grade": "Manual Review"}])

    result = calculate_campaign_metrics(campaigns, leads, conversions, lead_scores, [])

    assert result.loc[0, "valid_lead_count"] == 0
    assert result.loc[0, "conversion_rate"] == 0
