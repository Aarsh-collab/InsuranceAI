from sqlalchemy import (Column, String, JSON, Integer, DateTime, ForeignKey, Boolean, Float, Text)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import uuid


# =========================
# ACCOUNT (WHO)
# =========================
class UserProfile(Base):
    __tablename__ = "UserProfiles"

    account_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(String, default="demo", index=True)

    name = Column(String, nullable=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)

    meeting_requested = Column(Boolean, default=False)
    meeting_status = Column(String)  # "requested", "sent", "completed", "cancelled"
    meeting_preferred_time = Column(String)
    meeting_notes = Column(String)
    meeting_created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


# =========================
# SESSION (WHAT THEY'RE DOING)
# =========================
class Session(Base):
    __tablename__ = "Sessions"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("UserProfiles.account_id"), nullable=False)
    state = Column(JSON)
    site_id = Column(String, default="demo")

    insurance_type = Column(String)  # "life", "auto", "home", etc
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    user = relationship("UserProfile", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


# =========================
# LIFE INSURANCE APPLICATION
# =========================
class LifeInsurance(Base):
    __tablename__ = "LifeInsurance"

    life_application_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    account_id = Column(String,ForeignKey("UserProfiles.account_id"),nullable=False,unique=True)

    age = Column(Integer)
    gender = Column(String)
    bmi = Column(Float)
    smoker = Column(String)

    diabetes = Column(Boolean)
    high_bp = Column(Boolean)
    heart_disease = Column(Boolean)
    cancer_history = Column(Boolean)

    family_history_count = Column(Integer)
    alcohol = Column(String)
    driving_violations = Column(Integer)
    occupation = Column(Integer)
    zip_risk = Column(Integer)

    coverage_amount = Column(Integer)
    term_length = Column(Integer)


# =========================
# DECLARATIONS PAGE (DOCUMENT STORAGE)
# =========================
class DecPage(Base):
    __tablename__ = "DecPages"

    dec_page_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    session_id = Column(
        String,
        ForeignKey("Sessions.session_id"),
        nullable=False
    )

    insurance_type = Column(String, nullable=False)  # "life", "auto", etc

    raw_text = Column(String)        # Full extracted text from PDF
    parsed_json = Column(JSON)       # Structured parsed output from parser

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


# =========================
# MESSAGES STORAGE (CHAT HISTORY)
# =========================
class Message(Base):
    __tablename__ = "messages"

    message_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    session_id = Column(
        String,
        ForeignKey("Sessions.session_id"),
        nullable=False,
        index=True
    )

    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    session = relationship("Session", back_populates="messages")