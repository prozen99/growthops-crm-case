import pandas as pd

from config import REFERENCE_DATE
from quality_validator import QualityIssue


ACTION_BY_GRADE = {
    "Hot": "영업 담당자가 24시간 내 직접 연락",
    "Warm": "마케팅 nurture 이메일 발송 후 3일 내 재확인",
    "Cold": "장기 육성 캠페인에 포함",
    "Manual Review": "데이터 품질 확인 후 수동 검토",
}


def grade_score(score: int, is_manual_review: bool = False) -> str:
    if is_manual_review:
        return "Manual Review"
    if score >= 75:
        return "Hot"
    if score >= 45:
        return "Warm"
    return "Cold"


def _lead_issue_map(issues: list[QualityIssue]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for issue in issues:
        if issue.record_id.startswith("L"):
            result.setdefault(issue.record_id, []).append(issue.issue_type)
    return result


def _manual_review_reason(issue_types: list[str]) -> str:
    labels = {
        "missing_email": "이메일 누락",
        "duplicate_email": "동일 이메일 중복",
        "invalid_lead_campaign_reference": "캠페인 참조 오류",
        "suspicious_bot_behavior": "짧은 시간 내 과도한 이벤트 발생",
    }
    reasons = [labels[issue] for issue in labels if issue in issue_types]
    return f"{' 및 '.join(reasons)}로 자동 점수 계산에서 제외됨"


def score_leads(
    leads: pd.DataFrame,
    campaigns: pd.DataFrame,
    events: pd.DataFrame,
    conversions: pd.DataFrame,
    issues: list[QualityIssue],
    manual_review_lead_ids: set[str],
) -> pd.DataFrame:
    """Calculate explainable rule-based lead scores."""
    campaign_lookup = campaigns.set_index("campaign_id").to_dict("index")
    lead_issues = _lead_issue_map(issues)
    reference_date = pd.Timestamp(REFERENCE_DATE)
    recent_cutoff = reference_date - pd.Timedelta(days=30)
    rows = []

    for _, lead in leads.iterrows():
        lead_id = lead["lead_id"]
        campaign = campaign_lookup.get(lead["source_campaign_id"], {})
        lead_events = events[events["lead_id"].eq(lead_id)]
        lead_conversions = conversions[conversions["lead_id"].eq(lead_id)]

        if lead_id in manual_review_lead_ids:
            rows.append(
                {
                    "lead_id": lead_id,
                    "email": lead["email"],
                    "company_name": lead["company_name"],
                    "lead_score": 0,
                    "lead_grade": "Manual Review",
                    "reason": _manual_review_reason(lead_issues.get(lead_id, [])),
                    "recommended_action": ACTION_BY_GRADE["Manual Review"],
                    "data_quality_status": "REVIEW_REQUIRED",
                }
            )
            continue

        score = 10
        reason_parts = ["기본 정상 리드 점수"]
        event_types = set(lead_events["event_type"])
        conversion_types = set(lead_conversions["conversion_type"])

        event_score_rules = {
            "email_open": (5, "이메일 오픈"),
            "link_click": (10, "링크 클릭"),
            "landing_visit": (10, "랜딩 페이지 방문"),
            "webinar_signup": (20, "웨비나 신청"),
            "demo_request": (30, "데모 요청"),
        }
        for event_type, (points, label) in event_score_rules.items():
            if event_type in event_types:
                score += points
                reason_parts.append(label)

        recent_event_count = len(lead_events[lead_events["event_time"].ge(recent_cutoff)])
        if recent_event_count:
            recent_points = min(recent_event_count * 2, 20)
            score += recent_points
            reason_parts.append(f"최근 30일 이벤트 {recent_event_count}건")
        else:
            score -= 10
            reason_parts.append("최근 이벤트 없음")

        conversion_score_rules = {
            "consultation_request": (25, "상담 요청"),
            "contract": (40, "계약 전환"),
            "purchase": (50, "구매 전환"),
        }
        for conversion_type, (points, label) in conversion_score_rules.items():
            if conversion_type in conversion_types:
                score += points
                reason_parts.append(label)

        if lead["company_size"] in {"Enterprise", "1000+"}:
            score += 15
            reason_parts.append("대기업 규모")
        elif lead["company_size"] in {"Mid-Market", "200-999"}:
            score += 10
            reason_parts.append("중견 기업 규모")

        title = lead["job_title"].lower()
        if any(keyword.lower() in title for keyword in ["Head", "Director", "Manager", "CTO", "CEO"]):
            score += 10
            reason_parts.append("의사결정권자 직무")

        if lead["industry"] in {"SaaS", "Finance", "Healthcare"}:
            score += 10
            reason_parts.append("우선순위 산업군")

        if campaign:
            if campaign["budget"] >= 10000:
                score += 5
                reason_parts.append("고예산 캠페인 유입")
            if campaign["channel"] in {"webinar", "paid_ads"}:
                score += 5
                reason_parts.append("고관여 채널 유입")
            if campaign["utm_code"] == "":
                score -= 10
                reason_parts.append("캠페인 UTM 누락")

        score = max(0, min(100, int(score)))
        grade = grade_score(score)
        rows.append(
            {
                "lead_id": lead_id,
                "email": lead["email"],
                "company_name": lead["company_name"],
                "lead_score": score,
                "lead_grade": grade,
                "reason": f"{', '.join(reason_parts)} 근거로 {grade} Lead로 분류됨",
                "recommended_action": ACTION_BY_GRADE[grade],
                "data_quality_status": "VALID",
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "lead_id",
            "email",
            "company_name",
            "lead_score",
            "lead_grade",
            "reason",
            "recommended_action",
            "data_quality_status",
        ],
    )
