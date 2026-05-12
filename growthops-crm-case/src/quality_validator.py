from dataclasses import dataclass

import pandas as pd


SEVERITY_BY_ISSUE = {
    "missing_email": "HIGH",
    "invalid_lead_campaign_reference": "HIGH",
    "invalid_event_lead_reference": "HIGH",
    "invalid_event_campaign_reference": "HIGH",
    "invalid_conversion_lead_reference": "HIGH",
    "duplicate_email": "HIGH",
    "suspicious_bot_behavior": "HIGH",
    "duplicate_company_name": "MEDIUM",
    "missing_campaign_utm_code": "MEDIUM",
    "unknown_source_or_blank_optional_field": "LOW",
}


@dataclass
class QualityIssue:
    issue_type: str
    severity: str
    record_id: str
    related_campaign_id: str = ""


def _add_issue(issues: list[QualityIssue], issue_type: str, record_id: str, related_campaign_id: str = "") -> None:
    issues.append(QualityIssue(issue_type, SEVERITY_BY_ISSUE[issue_type], str(record_id), str(related_campaign_id)))


def validate_data(
    campaigns: pd.DataFrame,
    leads: pd.DataFrame,
    events: pd.DataFrame,
    conversions: pd.DataFrame,
) -> list[QualityIssue]:
    """Detect required data quality issues across raw CRM entities."""
    issues: list[QualityIssue] = []
    campaign_ids = set(campaigns["campaign_id"])
    lead_ids = set(leads["lead_id"])

    for _, lead in leads[leads["email"].eq("")].iterrows():
        _add_issue(issues, "missing_email", lead["lead_id"], lead["source_campaign_id"])

    duplicated_email_mask = leads["email"].ne("") & leads["email"].duplicated(keep=False)
    for _, lead in leads[duplicated_email_mask].iterrows():
        _add_issue(issues, "duplicate_email", lead["lead_id"], lead["source_campaign_id"])

    duplicated_company_mask = leads["company_name"].ne("") & leads["company_name"].duplicated(keep=False)
    for _, lead in leads[duplicated_company_mask].iterrows():
        _add_issue(issues, "duplicate_company_name", lead["lead_id"], lead["source_campaign_id"])

    for _, lead in leads[~leads["source_campaign_id"].isin(campaign_ids)].iterrows():
        _add_issue(issues, "invalid_lead_campaign_reference", lead["lead_id"], lead["source_campaign_id"])

    for _, campaign in campaigns[campaigns["utm_code"].eq("")].iterrows():
        _add_issue(issues, "missing_campaign_utm_code", campaign["campaign_id"], campaign["campaign_id"])

    for _, event in events[~events["lead_id"].isin(lead_ids)].iterrows():
        _add_issue(issues, "invalid_event_lead_reference", event["event_id"], event["campaign_id"])

    for _, event in events[~events["campaign_id"].isin(campaign_ids)].iterrows():
        _add_issue(issues, "invalid_event_campaign_reference", event["event_id"], event["campaign_id"])

    for _, conversion in conversions[~conversions["lead_id"].isin(lead_ids)].iterrows():
        _add_issue(issues, "invalid_conversion_lead_reference", conversion["conversion_id"], conversion["campaign_id"])

    optional_columns = ["industry", "company_size", "job_title"]
    blank_optional_mask = leads[optional_columns].eq("").any(axis=1)
    for _, lead in leads[blank_optional_mask].iterrows():
        _add_issue(issues, "unknown_source_or_blank_optional_field", lead["lead_id"], lead["source_campaign_id"])

    for lead_id, group in events.dropna(subset=["event_time"]).groupby("lead_id"):
        sorted_times = group["event_time"].sort_values().reset_index(drop=True)
        for start_time in sorted_times:
            window_count = (sorted_times.between(start_time, start_time + pd.Timedelta(minutes=10))).sum()
            if window_count >= 15:
                campaign_id = group.iloc[0]["campaign_id"]
                _add_issue(issues, "suspicious_bot_behavior", lead_id, campaign_id)
                break

    return issues


def summarize_quality_issues(issues: list[QualityIssue]) -> pd.DataFrame:
    """Aggregate row-level issues into the required report shape."""
    rows = []
    for issue_type, severity in SEVERITY_BY_ISSUE.items():
        matching = [issue for issue in issues if issue.issue_type == issue_type]
        if matching:
            sample_ids = ", ".join(issue.record_id for issue in matching[:5])
            rows.append(
                {
                    "issue_type": issue_type,
                    "count": len(matching),
                    "severity": severity,
                    "sample_ids": sample_ids,
                }
            )
    return pd.DataFrame(rows, columns=["issue_type", "count", "severity", "sample_ids"])


def get_manual_review_lead_ids(issues: list[QualityIssue]) -> set[str]:
    manual_review_issue_types = {
        "missing_email",
        "duplicate_email",
        "invalid_lead_campaign_reference",
        "suspicious_bot_behavior",
    }
    return {
        issue.record_id
        for issue in issues
        if issue.issue_type in manual_review_issue_types and issue.record_id.startswith("L")
    }
