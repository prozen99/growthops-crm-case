import pandas as pd

from config import CAMPAIGNS_FILE, CONVERSIONS_FILE, EVENTS_FILE, LEADS_FILE


def load_raw_data() -> dict[str, pd.DataFrame]:
    """Load all raw CRM CSV inputs."""
    return {
        "campaigns": pd.read_csv(CAMPAIGNS_FILE, keep_default_na=False),
        "leads": pd.read_csv(LEADS_FILE, keep_default_na=False),
        "events": pd.read_csv(EVENTS_FILE, keep_default_na=False),
        "conversions": pd.read_csv(CONVERSIONS_FILE, keep_default_na=False),
    }
