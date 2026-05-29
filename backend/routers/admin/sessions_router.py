from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from core.admin_auth import verify_admin
from routers.admin.access import require_account_access

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

@router.get("/users/{account_id}/sessions")
def get_user_sessions(account_id: str, db: Session = Depends(get_db), admin: dict = Depends(verify_admin)):
    account = (
        db.query(models.UserProfile)
        .filter(models.UserProfile.account_id == account_id)
        .first()
    )
    require_account_access(account, admin)

    sessions = db.query(models.Session)\
        .filter(models.Session.account_id == account_id)\
        .order_by(models.Session.created_at.desc())\
        .all()

    result = []

    for session in sessions:
        state = session.state or {}
        memory = state.get("memory", {})
        application = state.get("application", {})

        result.append({
            "session_id": session.session_id,
            "site_id": session.site_id,
            "insurance_type": session.insurance_type,
            "created_at": session.created_at,
            "summary": memory.get("session_summary", ""),
            "preview_messages": memory.get("last_messages", []),
            "missing_fields": application.get("missing_fields", [])
        })

    return result
