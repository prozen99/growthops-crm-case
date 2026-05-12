import pandas as pd

from quality_validator import QualityIssue


def calculate_campaign_metrics(
    campaigns: pd.DataFrame,
    leads: pd.DataFrame,
    conversions: pd.DataFrame,
    lead_scores: pd.DataFrame,
    issues: list[QualityIssue],
) -> pd.DataFrame:
    """Build campaign-level performance metrics from scored leads."""
    scored_leads = leads.merge(lead_scores[["lead_id", "lead_grade"]], on="lead_id", how="left")
    rows = []

    for _, campaign in campaigns.iterrows():
        campaign_id = campaign["campaign_id"]
        campaign_leads = scored_leads[scored_leads["source_campaign_id"].eq(campaign_id)]
        valid_leads = campaign_leads[~campaign_leads["lead_grade"].eq("Manual Review")]
        conversion_count = len(conversions[conversions["campaign_id"].eq(campaign_id)])
        valid_lead_count = len(valid_leads)
        conversion_rate = conversion_count / valid_lead_count if valid_lead_count else 0
        issue_count = sum(1 for issue in issues if issue.related_campaign_id == campaign_id)

        rows.append(
            {
                "campaign_id": campaign_id,
                "campaign_name": campaign["campaign_name"],
                "channel": campaign["channel"],
                "lead_count": len(campaign_leads),
                "valid_lead_count": valid_lead_count,
                "hot_lead_count": len(campaign_leads[campaign_leads["lead_grade"].eq("Hot")]),
                "conversion_count": conversion_count,
                "conversion_rate": round(conversion_rate, 4),
                "data_quality_issue_count": issue_count,
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "campaign_id",
            "campaign_name",
            "channel",
            "lead_count",
            "valid_lead_count",
            "hot_lead_count",
            "conversion_count",
            "conversion_rate",
            "data_quality_issue_count",
        ],
    )
