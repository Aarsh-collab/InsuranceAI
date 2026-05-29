from typing import Any


def _has_contact(account: Any) -> bool:
    return bool(
        getattr(account, "email", None)
        or getattr(account, "phone", None)
        or getattr(account, "name", None)
    )


def calculate_lead_quality(
    *,
    account: Any,
    session_state: dict | None,
    has_dec_page: bool = False,
    message_count: int = 0,
) -> dict:
    state = session_state or {}
    application = state.get("application", {}) if isinstance(state, dict) else {}
    answered_fields = application.get("answered_fields") or {}
    missing_fields = application.get("missing_fields") or []
    ml_quote = application.get("ml_quote")
    completed = bool(application.get("completed"))

    contact_exists = _has_contact(account)
    meeting_requested = bool(getattr(account, "meeting_requested", False))
    meaningful_progress = (
        len(answered_fields) >= 3
        or message_count >= 4
        or ml_quote is not None
        or has_dec_page
    )
    quote_complete = completed and len(missing_fields) == 0

    reasons = []

    if contact_exists:
        reasons.append("Has contact information")
    else:
        reasons.append("Missing contact information")

    if quote_complete:
        reasons.append("Quote intake is complete")
    elif meaningful_progress:
        reasons.append("Has meaningful intake progress")
    else:
        reasons.append("Limited intake progress")

    if meeting_requested:
        reasons.append("Requested broker follow-up")

    if has_dec_page:
        reasons.append("Uploaded policy document")

    if contact_exists and (quote_complete or meeting_requested):
        score = "high"
    elif contact_exists or meaningful_progress:
        score = "medium"
    else:
        score = "low"

    return {
        "score": score,
        "reasons": reasons,
    }
