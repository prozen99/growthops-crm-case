import pandas as pd


def clean_data(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Standardize blank strings, dates, and basic text casing."""
    campaigns = data["campaigns"].copy()
    leads = data["leads"].copy()
    events = data["events"].copy()
    conversions = data["conversions"].copy()

    for frame in [campaigns, leads, events, conversions]:
        for column in frame.columns:
            if pd.api.types.is_object_dtype(frame[column]) or pd.api.types.is_string_dtype(frame[column]):
                frame[column] = frame[column].astype(str).str.strip()

    leads["email"] = leads["email"].str.lower()
    leads["created_at"] = pd.to_datetime(leads["created_at"], errors="coerce")
    campaigns["start_date"] = pd.to_datetime(campaigns["start_date"], errors="coerce")
    campaigns["end_date"] = pd.to_datetime(campaigns["end_date"], errors="coerce")
    events["event_time"] = pd.to_datetime(events["event_time"], errors="coerce")
    conversions["conversion_time"] = pd.to_datetime(conversions["conversion_time"], errors="coerce")
    campaigns["budget"] = pd.to_numeric(campaigns["budget"], errors="coerce").fillna(0)
    conversions["amount"] = pd.to_numeric(conversions["amount"], errors="coerce").fillna(0)

    return {
        "campaigns": campaigns,
        "leads": leads,
        "events": events,
        "conversions": conversions,
    }
