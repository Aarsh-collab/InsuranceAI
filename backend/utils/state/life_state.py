from __future__ import annotations
from typing import Dict, Any, List
from utils.schema.life_schema import LifeApplicationState, LifeMemory, LifeMeta, LifeDocuments, LifeState, LifeWorkflow, ProfileMemory, DecPageState


# Fields required to generate a life insurance quote
REQUIRED_LIFE_FIELDS: List[str] = [
    "age",
    "gender",
    "smoker",
    "bmi",
    "coverage_amount",
    "term_length",
]


def _safe_get(obj: Any, attr: str, default: Any = None) -> Any:
    """Helper: getattr that won't throw if obj is None."""
    if obj is None:
        return default
    return getattr(obj, attr, default)


def build_life_state(
    db,
    *,
    account_id: int,
    session_id: str,
) -> Dict[str, Any]:
    
   
    from db.models import LifeInsurance, Session  
    
    # Optional models (only included if they exist in your project today)
    DecPage = None
    BrokerMeeting = None
    try:
        from models import DecPage  # type: ignore
        DecPage = DecPage
    except Exception:
        try:
            from models import DecPage  # type: ignore
            DecPage = DecPage
        except Exception:
            DecPage = None

    try:
        from models import BrokerMeeting  # type: ignore
        BrokerMeeting = BrokerMeeting
    except Exception:
        try:
            from models import BrokerMeeting  # type: ignore
            BrokerMeeting = BrokerMeeting
        except Exception:
            BrokerMeeting = None

    # 1) Load session (anchor for everything in this request)
    session_row = (
        db.query(Session)
        .filter(Session.session_id == session_id, Session.account_id == account_id)
        .first()
    )

    # 2) Load the life application row for this session
    life_application = (
        db.query(LifeInsurance)
        .filter(LifeInsurance.account_id == account_id)
        .first()
    )

    # 3) Derive answered/missing fields from the LifeInsurance row
    answered_fields: Dict[str, Any] = {}
    missing_fields: List[str] = []

    if life_application is None:
        # No row yet: everything is missing
        missing_fields = list(REQUIRED_LIFE_FIELDS)
    else:
        for field in REQUIRED_LIFE_FIELDS:
            value = getattr(life_application, field, None)
            if value is None:
                missing_fields.append(field)
            else:
                answered_fields[field] = value

    completed = (len(missing_fields) == 0) and (_safe_get(life_application, "ml_prediction", None) is not None)

    # 4) Attach meeting + document context if available
    meeting_context: Dict[str, Any] = {
        "has_meeting": False,
        "meeting_status": None,
        "meeting_time": None,
        "meeting_id": None,
    }
    if BrokerMeeting is not None:
        meeting_row = (
            db.query(BrokerMeeting)
            .filter(BrokerMeeting.session_id == session_id)
            .order_by(BrokerMeeting.timestamp.desc())
            .first()
        )
        if meeting_row is not None:
            meeting_context = {
                "has_meeting": True,
                "meeting_status": _safe_get(meeting_row, "status"),
                "meeting_time": _safe_get(meeting_row, "scheduled_for"),
                "meeting_id": _safe_get(meeting_row, "meeting_id"),
            }

    dec_page_context: Dict[str, Any] = {
        "has_dec_page": False,
        "insurance_type": "life",
        "latest_dec_id": None,
        "processing_status": None,
    }
    if DecPage is not None:
        dec_row = (
            db.query(DecPage)
            .filter(DecPage.session_id == session_id)
            .order_by(DecPage.timestamp.desc())
            .first()
        )
        if dec_row is not None:
            dec_page_context = {
                "has_dec_page": True,
                "insurance_type": _safe_get(dec_row, "insurance_type", "life"),
                "latest_dec_id": _safe_get(dec_row, "dec_id"),
                "processing_status": _safe_get(dec_row, "processing_status"),
            }

    # 5) Decide a default "stage" for this request.
    #    Keep this simple: the router/context-manager can override.
    stage = "matching" if missing_fields else "post_match"

    # 6) Build the state envelope.
    #    IMPORTANT: This is what every downstream LLM call gets.
    state = LifeState(
        meta=LifeMeta(
            account_id=account_id,
            session_id=session_id
        ),
        workflow=LifeWorkflow(
            stage=stage,
            intent="auto"
        ),
        application=LifeApplicationState(
            answered_fields=answered_fields,
            missing_fields=missing_fields,
            refused_fields=_safe_get(session_row, "refused_fields", {}) if session_row else {},
            ml_quote=_safe_get(life_application, "ml_prediction", None),
            completed=completed
        ),
        documents=LifeDocuments(
            dec_page=DecPageState(**dec_page_context)
        ),

        memory=LifeMemory(
            profile=ProfileMemory(
                name=_safe_get(session_row, "name"),
                email=_safe_get(session_row, "email"),
                phone=_safe_get(session_row, "phone"),
            ),
            session_summary=_safe_get(session_row, "session_summary", None),
        )
    )

    return state