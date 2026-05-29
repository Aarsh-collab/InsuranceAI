from fastapi import HTTPException

from db import models


def allowed_site_ids(admin: dict) -> list[str]:
    return admin.get("allowed_site_ids") or []


def can_access_site(admin: dict, site_id: str | None) -> bool:
    sites = allowed_site_ids(admin)
    return "*" in sites or site_id in sites


def require_account_access(account: models.UserProfile | None, admin: dict) -> models.UserProfile:
    if not account or not can_access_site(admin, account.site_id):
        raise HTTPException(status_code=404, detail="account not found")
    return account


def require_session_access(session: models.Session | None, admin: dict) -> models.Session:
    if not session or not can_access_site(admin, session.site_id):
        raise HTTPException(status_code=404, detail="session not found")
    return session
