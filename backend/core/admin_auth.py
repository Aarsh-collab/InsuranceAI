import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Header, HTTPException, status

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def verify_admin(authorization: str | None = Header(default=None)):
    admin_token = os.environ.get("ADMIN_TOKEN")
    site_admin = os.environ.get("SITE_ADMIN")
    site_id = os.environ.get("SITE_ID")

    if not admin_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin auth is not configured",
        )

    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format",
        )

    if token == admin_token:
        return {
            "role": "owner",
            "allowed_site_ids": ["*"]
        }
    if token == site_admin:
        return {
            "role": "site_admin",
            "allowed_site_ids": [site_id]
        }

    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
        )   