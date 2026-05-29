from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.admin_auth import verify_admin
from db import models
from db.database import get_db
from services.lead_quality import calculate_lead_quality

router = APIRouter(
    prefix="/admin",
    tags=["Admin", "Leads"],
)


def _application_state(session: models.Session) -> dict:
    state = session.state or {}
    if not isinstance(state, dict):
        return {}
    application = state.get("application") or {}
    return application if isinstance(application, dict) else {}


def _message_count(db: Session, session_id: str) -> int:
    return (
        db.query(models.Message)
        .filter(models.Message.session_id == session_id)
        .count()
    )


def _conversation_summary(session_state: dict | None, messages: list[models.Message]) -> str:
    state = session_state or {}
    memory = state.get("memory", {}) if isinstance(state, dict) else {}
    summary = memory.get("session_summary") if isinstance(memory, dict) else None
    if summary:
        return summary

    if not messages:
        return ""

    recent = messages[-4:]
    snippets = []
    for message in recent:
        content = (message.content or "").strip()
        if not content:
            continue
        snippets.append(f"{message.role}: {content[:180]}")

    return "Recent conversation: " + " | ".join(snippets) if snippets else ""


def _lead_row(db: Session, session: models.Session) -> dict:
    account = session.user
    application = _application_state(session)
    life_application = (
        db.query(models.LifeInsurance)
        .filter(models.LifeInsurance.account_id == session.account_id)
        .first()
    )
    dec_page = (
        db.query(models.DecPage)
        .filter(models.DecPage.session_id == session.session_id)
        .first()
    )
    recent_messages = (
        db.query(models.Message)
        .filter(models.Message.session_id == session.session_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )
    message_count = _message_count(db, session.session_id)
    lead_quality = calculate_lead_quality(
        account=account,
        session_state=session.state,
        has_dec_page=dec_page is not None,
        message_count=message_count,
    )

    return {
        "account_id": session.account_id,
        "session_id": session.session_id,
        "name": account.name if account else "",
        "email": account.email if account else None,
        "phone": account.phone if account else None,
        "insurance_type": session.insurance_type,
        "created_at": session.created_at,
        "meeting_requested": account.meeting_requested if account else False,
        "meeting_status": account.meeting_status if account else None,
        "meeting_preferred_time": account.meeting_preferred_time if account else None,
        "ml_quote": application.get("ml_quote"),
        "completed": application.get("completed") or False,
        "missing_fields": application.get("missing_fields") or [],
        "answered_fields": application.get("answered_fields") or {},
        "has_dec_page": dec_page is not None,
        "message_count": message_count,
        "conversation_summary": _conversation_summary(session.state, recent_messages),
        "lead_quality": lead_quality,
        "site_id": session.site_id
    }


@router.get("/leads")
def get_leads(db: Session = Depends(get_db), admin = Depends(verify_admin)):
    allowed_sites = admin.get("allowed_site_ids", [])
    if "*" in allowed_sites:
        sessions = (
            db.query(models.Session)
            .order_by(models.Session.created_at.desc())
            .all()
        )
    else:
        sessions = (
            db.query(models.Session)
            .filter(models.Session.site_id.in_(allowed_sites))
            .order_by(models.Session.created_at.desc())
            .all()
        )
    
    return [_lead_row(db, session) for session in sessions]


@router.get("/leads/{session_id}")
def get_lead_detail(session_id: str, admin = Depends(verify_admin), db: Session = Depends(get_db)):
    allowed_sites = admin.get("allowed_site_ids", [])

    session = (
        db.query(models.Session)
        .filter(models.Session.session_id == session_id)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="lead not found")
    if "*" not in allowed_sites and session.site_id not in allowed_sites:
        raise HTTPException(status_code=404, detail="lead not found")

    account = session.user
    life_application = (
        db.query(models.LifeInsurance)
        .filter(models.LifeInsurance.account_id == session.account_id)
        .first()
    )
    dec_page = (
        db.query(models.DecPage)
        .filter(models.DecPage.session_id == session_id)
        .first()
    )
    messages = (
        db.query(models.Message)
        .filter(models.Message.session_id == session_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )

    lead_quality = calculate_lead_quality(
        account=account,
        session_state=session.state,
        has_dec_page=dec_page is not None,
        message_count=len(messages),
    )
    conversation_summary = _conversation_summary(session.state, messages)

    return {
        "account": {
            "account_id": account.account_id if account else None,
            "name": account.name if account else "",
            "email": account.email if account else None,
            "phone": account.phone if account else None,
            "meeting_requested": account.meeting_requested if account else False,
            "meeting_status": account.meeting_status if account else None,
            "meeting_preferred_time": account.meeting_preferred_time if account else None,
            "meeting_notes": account.meeting_notes if account else None,
            "meeting_created_at": account.meeting_created_at if account else None,
        },
        "session": {
            "session_id": session.session_id,
            "account_id": session.account_id,
            "insurance_type": session.insurance_type,
            "created_at": session.created_at,
            "is_active": session.is_active,
            "site_id": session.site_id
        },
        "life_application": {
            "life_application_id": life_application.life_application_id if life_application else None,
            "age": life_application.age if life_application else None,
            "gender": life_application.gender if life_application else None,
            "bmi": life_application.bmi if life_application else None,
            "smoker": life_application.smoker if life_application else None,
            "diabetes": life_application.diabetes if life_application else None,
            "high_bp": life_application.high_bp if life_application else None,
            "heart_disease": life_application.heart_disease if life_application else None,
            "cancer_history": life_application.cancer_history if life_application else None,
            "family_history_count": life_application.family_history_count if life_application else None,
            "alcohol": life_application.alcohol if life_application else None,
            "driving_violations": life_application.driving_violations if life_application else None,
            "occupation": life_application.occupation if life_application else None,
            "zip_risk": life_application.zip_risk if life_application else None,
            "coverage_amount": life_application.coverage_amount if life_application else None,
            "term_length": life_application.term_length if life_application else None,
        },
        "state": session.state or {},
        "messages": [
            {
                "message_id": message.message_id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
        "conversation_summary": conversation_summary,
        "dec_page": {
            "dec_page_id": dec_page.dec_page_id,
            "insurance_type": dec_page.insurance_type,
            "raw_text": dec_page.raw_text,
            "parsed_json": dec_page.parsed_json,
            "uploaded_at": dec_page.uploaded_at,
        }
        if dec_page
        else None,
        "lead_quality": lead_quality,
    }
