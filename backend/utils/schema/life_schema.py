from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

REQUIRED_LIFE_FIELDS = [
    "age",
    "gender",
    "bmi",
    "smoker",
    "coverage_amount",
    "term_length"
]
ALL_LIFE_FIELDS = [
    "age",
    "gender",
    "bmi",
    "smoker",
    "coverage_amount",
    "term_length",
    "diabetes",
    "high_bp",
    "heart_disease",
    "cancer_history",
    "family_history_count",
    "alcohol",
    "driving_violations",
    "occupation",
    "zip_risk"
]
class LifeMeta(BaseModel):
    insurance_type: str = "life"
    account_id: str
    session_id: str

class LifeWorkflow(BaseModel):
    stage: Optional[str] = None
    intent: Optional[str] = None

class LifeApplicationState(BaseModel):
    answered_fields: Dict[str, Any] = Field(default_factory=dict)
    missing_fields: List[str] = Field(default_factory=list)
    refused_fields: Dict[str, bool] = Field(default_factory=dict)
    ml_quote: Optional[float] = None
    completed: Optional[bool] = None

class DecPageState(BaseModel):
    has_dec_page: bool
    insurance_type: str
    latest_dec_id: Optional[str]
    processing_status: Optional[str]

class LifeDocuments(BaseModel):
    dec_page: DecPageState


class ProfileMemory(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]


class LifeMemory(BaseModel):
    profile: ProfileMemory
    last_messages: List[Dict[str, str]] = Field(default_factory=list)
    session_summary: Optional[str]

class LifeState(BaseModel):
    meta: LifeMeta
    workflow: LifeWorkflow
    application: LifeApplicationState = Field(default_factory=LifeApplicationState)
    documents: LifeDocuments
    memory: LifeMemory
