from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from core.admin_auth import verify_admin
from routers.admin.access import require_session_access

router = APIRouter(
    prefix="/admin",
    tags=["Admin", "Session"],
)

@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str, db: Session = Depends(get_db), admin: dict = Depends(verify_admin)):
    session = (
        db.query(models.Session)
        .filter(models.Session.session_id == session_id)
        .first()
    )
    require_session_access(session, admin)

    messages = db.query(models.Message)\
        .filter(models.Message.session_id == session_id)\
        .order_by(models.Message.created_at.asc())\
        .limit(50)\
        .all()
    
    if not messages:
        return []
    return [
        {
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at
        }
        for message in messages
    ]
