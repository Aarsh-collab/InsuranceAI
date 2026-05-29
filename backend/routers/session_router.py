from fastapi import APIRouter, Depends, HTTPException, status, Request
from core.rate_limiter import limiter
from sqlalchemy.orm import Session
import uuid
from db import models
from db.database import get_db
from pydantic import BaseModel, Field
from typing import Literal



class CreateSessionRequest(BaseModel):
    insurance_type: Literal[
        "life",
        "homeowners",
        "auto",
        "renters",
        "health",
        "travel",
    ] = Field(..., description="Insurance product the user selected")

class CreateAccountRequest(BaseModel):
    site_id: str = "demo"

router = APIRouter(prefix="/accounts", tags=["account"])

@router.post("", status_code=status.HTTP_201_CREATED,)
@limiter.limit("10/minute")
def create_account(request: Request, payload: CreateAccountRequest, db: Session = Depends(get_db)):
    account_id = str(uuid.uuid4())

    new_user = models.UserProfile(account_id=account_id, site_id=payload.site_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"account_id": new_user.account_id}

@router.post("/{account_id}/sessions", status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def create_session(request: Request, account_id: str, payload: CreateSessionRequest, db: Session = Depends(get_db)):
    account = (db.query(models.UserProfile).filter(models.UserProfile.account_id == account_id).first())
    if not account:
        raise HTTPException(status_code=404, detail="account not found")

    session_id = str(uuid.uuid4())

    new_session = models.Session(
        session_id=session_id,
        account_id=account_id,
        insurance_type=payload.insurance_type,
        site_id=account.site_id
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {"session_id": new_session.session_id, "insurance_type": new_session.insurance_type, "site_id": account.site_id}
