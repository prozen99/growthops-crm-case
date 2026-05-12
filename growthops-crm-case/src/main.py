from cleaner import clean_data
from data_generator import generate_dummy_data
from loader import load_raw_data
from metrics import calculate_campaign_metrics
from quality_validator import get_manual_review_lead_ids, summarize_quality_issues, validate_data
from reporter import print_summary, save_outputs
from scorer import score_leads


def main() -> None:
    generate_dummy_data()
    raw_data = load_raw_data()
    cleaned_data = clean_data(raw_data)

    campaigns = cleaned_data["campaigns"]
    leads = cleaned_data["leads"]
    events = cleaned_data["events"]
    conversions = cleaned_data["conversions"]

    issues = validate_data(campaigns, leads, events, conversions)
    manual_review_lead_ids = get_manual_review_lead_ids(issues)
    lead_scores = score_leads(leads, campaigns, events, conversions, issues, manual_review_lead_ids)
    campaign_metrics = calculate_campaign_metrics(campaigns, leads, conversions, lead_scores, issues)
    data_quality_report = summarize_quality_issues(issues)

    save_outputs(lead_scores, campaign_metrics, data_quality_report)
    print_summary(len(leads), lead_scores, data_quality_report)


if __name__ == "__main__":
    main()
