import pandas as pd

from config import CAMPAIGNS_FILE, CONVERSIONS_FILE, EVENTS_FILE, LEADS_FILE, RAW_DATA_DIR


def generate_dummy_data() -> None:
    """Create deterministic raw CSV files with intentional quality issues."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    campaigns = pd.DataFrame(
        [
            ["CAMP001", "SaaS Growth Webinar", "webinar", "2026-04-01", "2026-05-31", 15000, "utm_webinar_growth"],
            ["CAMP002", "Finance Paid Search", "paid_ads", "2026-04-10", "2026-05-15", 12000, "utm_paid_finance"],
            ["CAMP003", "Healthcare Newsletter", "email", "2026-03-20", "2026-05-20", 5000, "utm_health_email"],
            ["CAMP004", "Enterprise Field Event", "event", "2026-04-15", "2026-06-01", 20000, ""],
        ],
        columns=["campaign_id", "campaign_name", "channel", "start_date", "end_date", "budget", "utm_code"],
    )

    leads = pd.DataFrame(
        [
            ["L001", "alice@alpha.com", "Alpha SaaS", "SaaS", "Enterprise", "CTO", "2026-04-20", "CAMP001"],
            ["L002", "bob@betafinance.com", "Beta Finance", "Finance", "Mid-Market", "Marketing Director", "2026-04-22", "CAMP002"],
            ["L003", "cara@clinicplus.com", "Clinic Plus", "Healthcare", "200-999", "Operations Manager", "2026-04-25", "CAMP003"],
            ["L004", "dave@smallco.com", "SmallCo", "Retail", "SMB", "Analyst", "2026-04-26", "CAMP003"],
            ["L005", "", "No Email Inc", "SaaS", "Enterprise", "CEO", "2026-04-27", "CAMP001"],
            ["L006", "dup@example.com", "Dup One", "Finance", "Mid-Market", "Head of Sales", "2026-04-28", "CAMP002"],
            ["L007", "dup@example.com", "Dup Two", "Finance", "Mid-Market", "Head of Growth", "2026-04-29", "CAMP002"],
            ["L008", "eve@samecorp.com", "Same Corp", "Manufacturing", "1000+", "Manager", "2026-04-30", "CAMP004"],
            ["L009", "frank@samecorp.com", "Same Corp", "Manufacturing", "1000+", "Director", "2026-05-01", "CAMP004"],
            ["L010", "ghost@badref.com", "Ghost Ref", "SaaS", "SMB", "Founder", "2026-05-02", "CAMP999"],
            ["L011", "bot@traffic.com", "Traffic Bot LLC", "SaaS", "Enterprise", "CTO", "2026-05-03", "CAMP001"],
            ["L012", "nina@quiet.com", "Quiet Co", "", "SMB", "", "2026-03-01", "CAMP003"],
        ],
        columns=["lead_id", "email", "company_name", "industry", "company_size", "job_title", "created_at", "source_campaign_id"],
    )

    events = pd.DataFrame(
        [
            ["E001", "L001", "CAMP001", "email_open", "2026-05-05 09:00:00"],
            ["E002", "L001", "CAMP001", "link_click", "2026-05-05 09:05:00"],
            ["E003", "L001", "CAMP001", "landing_visit", "2026-05-05 09:08:00"],
            ["E004", "L001", "CAMP001", "webinar_signup", "2026-05-05 09:10:00"],
            ["E005", "L001", "CAMP001", "demo_request", "2026-05-06 10:00:00"],
            ["E006", "L002", "CAMP002", "email_open", "2026-05-01 11:00:00"],
            ["E007", "L002", "CAMP002", "link_click", "2026-05-01 11:30:00"],
            ["E008", "L003", "CAMP003", "email_open", "2026-04-30 12:00:00"],
            ["E009", "L004", "CAMP003", "landing_visit", "2026-05-02 13:00:00"],
            ["E010", "L999", "CAMP001", "email_open", "2026-05-02 14:00:00"],
            ["E011", "L002", "CAMP999", "landing_visit", "2026-05-03 15:00:00"],
        ],
        columns=["event_id", "lead_id", "campaign_id", "event_type", "event_time"],
    )

    bot_events = pd.DataFrame(
        [[f"EBOT{i:02d}", "L011", "CAMP001", "link_click", f"2026-05-07 09:{i:02d}:00"] for i in range(16)],
        columns=events.columns,
    )
    events = pd.concat([events, bot_events], ignore_index=True)

    conversions = pd.DataFrame(
        [
            ["CV001", "L001", "CAMP001", "consultation_request", "2026-05-06 11:00:00", 0],
            ["CV002", "L001", "CAMP001", "purchase", "2026-05-10 16:00:00", 25000],
            ["CV003", "L002", "CAMP002", "contract", "2026-05-08 12:00:00", 15000],
            ["CV004", "L999", "CAMP002", "purchase", "2026-05-09 12:00:00", 5000],
        ],
        columns=["conversion_id", "lead_id", "campaign_id", "conversion_type", "conversion_time", "amount"],
    )

    campaigns.to_csv(CAMPAIGNS_FILE, index=False)
    leads.to_csv(LEADS_FILE, index=False)
    events.to_csv(EVENTS_FILE, index=False)
    conversions.to_csv(CONVERSIONS_FILE, index=False)
