from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from core.admin_auth import verify_admin
from routers.admin.access import allowed_site_ids

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

@router.get("/users")
def get_users(db: Session = Depends(get_db), admin: dict = Depends(verify_admin)):
    sites = allowed_site_ids(admin)
    query = db.query(models.UserProfile)

    if "*" not in sites:
        query = query.filter(models.UserProfile.site_id.in_(sites))

    users = query.order_by(models.UserProfile.meeting_created_at.desc()).all()

    return [
        {
            "account_id": user.account_id,
            "site_id": user.site_id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "meeting_status": user.meeting_status,
            "preferred_time": user.meeting_preferred_time,
            "meeting_preferred_time": user.meeting_created_at
        }
        for user in users
    ]
