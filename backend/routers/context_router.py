from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from services.context_manager import context_manager
from services.session_summarizer import session_summarizer
from services.lifeInsurance.life_matcher import lifeInsuranceAI
from services.lifeInsurance.validation import RULES, validate_fields, is_missing
from db import models
from db.database import get_db
from utils.state.life_state import build_life_state
from utils.apply_state_updates import apply_state_updates
from utils.schema.life_schema import LifeState, ALL_LIFE_FIELDS
from services.lifeInsurance.life_ML import life_ml_helper
from services.lifeInsurance.life_gap_analysis import lifeDecPageAnalysis
from services.meeting_organizer import REQUIRED_MEETING_FIELDS, meeting_organizer
from services.lifeInsurance.life_explanation import lifeExplanation
from services.conversation_recovery import conversation_recovery
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from core.rate_limiter import limiter


router = APIRouter(prefix="/chat", tags=["Chat"])
DEFAULT_ZIP_RISK = 5

class ChatRequest(BaseModel):
    message: str


def _is_dec_page_question(message: str) -> bool:
    text = (message or "").lower()

    document_terms = [
        "dec page",
        "declaration",
        "document",
        "uploaded",
        "policy",
        "plan",
        "beneficiary",
        "death benefit",
        "face amount",
        "premium",
        "rider",
        "exclusion",
        "cash value",
        "surrender",
        "coverage",
    ]
    review_terms = [
        "what does",
        "what is",
        "mean",
        "good",
        "enough",
        "missing",
        "gap",
        "review",
        "think",
        "look",
    ]

    return any(term in text for term in document_terms) and any(
        term in text for term in review_terms
    )


def _is_valid_life_field(field: str, value) -> bool:
    if field not in RULES:
        return value is not None
    try:
        return RULES[field](value)
    except Exception:
        return False


def _sync_life_application_state(state: LifeState, life_insurance_datatable: models.LifeInsurance) -> None:
    answered = {}
    missing = []

    for field in ALL_LIFE_FIELDS:
        value = getattr(life_insurance_datatable, field, None)
        if _is_valid_life_field(field, value):
            answered[field] = value
        else:
            missing.append(field)

    state.application.answered_fields = answered
    state.application.missing_fields = missing
    state.application.completed = bool(state.application.ml_quote is not None and not missing)


def _ensure_internal_defaults(life_insurance_datatable: models.LifeInsurance) -> None:
    if is_missing(life_insurance_datatable.zip_risk):
        life_insurance_datatable.zip_risk = DEFAULT_ZIP_RISK

def _reset_life_estimate(life_insurance_datatable: models.LifeInsurance, state: LifeState) -> None:
    for field in ALL_LIFE_FIELDS:
        setattr(life_insurance_datatable, field, None)

    _ensure_internal_defaults(life_insurance_datatable)
    state.application.ml_quote = None
    state.application.refused_fields = {}
    state.application.answered_fields = {}
    state.application.missing_fields = []
    state.application.completed = False
    state.workflow.stage = "matching"
    state.workflow.intent = "reset_estimate"
    state.memory.session_summary = None


def _workflow_context(account: models.UserProfile, state: LifeState, has_dec_page: bool) -> dict:
    return {
        "meeting_requested": bool(account.meeting_requested),
        "meeting_status": account.meeting_status,
        "meeting_preferred_time": account.meeting_preferred_time,
        "has_preliminary_quote": state.application.ml_quote is not None,
        "quote_amount": state.application.ml_quote,
        "intake_completed": bool(state.application.completed),
        "missing_life_fields": state.application.missing_fields,
        "has_dec_page": has_dec_page,
    }


def _send_meeting_email(account: models.UserProfile) -> None:
    message = Mail(
        from_email=os.environ.get('FROM_EMAIL_ADDRESS'),
        to_emails=os.environ.get('TO_EMAIL_ADDRESS'),
        subject='New InsuranceAI Meeting Request',
        html_content=f'''
            <strong>New Meeting Request Name: {account.name}<br>
            Email: {account.email}<br>
            Phone: {account.phone}<br>
            Account_id: {account.account_id}</strong><br><br>
        '''
    )

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.send(message)
    except Exception as e:
        print(str(e))


@router.post("/router")
@limiter.limit("30/minute")
async def context_router(request: Request, session_id: str, body: ChatRequest, db: Session = Depends(get_db)):
    
    session = db.query(models.Session).filter(models.Session.session_id == session_id).first()
    
    #check if session exists
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    
    #check insurance type
    insurance_type = session.insurance_type 

    #check for account
    account = db.query(models.UserProfile).filter(models.UserProfile.account_id == session.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="account not found")


    #life insurance datatable
    life_insurance_datatable = db.query(models.LifeInsurance).filter(models.LifeInsurance.account_id == session.account_id).first()
    if not life_insurance_datatable:
        life_insurance_datatable = models.LifeInsurance(
            account_id = session.account_id,
            )
        db.add(life_insurance_datatable)

    _ensure_internal_defaults(life_insurance_datatable)


    #dec page check
    dec_page_table = db.query(models.DecPage).filter(models.DecPage.session_id == session_id).first()

    #check if state exists
    if not session.state:
        state = build_life_state(db, account_id=session.account_id, session_id=session_id)
        session.state = state.dict()
    else: 
        state = LifeState(**session.state)

    if dec_page_table:
        state.documents.dec_page.has_dec_page = True
        state.documents.dec_page.insurance_type = dec_page_table.insurance_type
        state.documents.dec_page.latest_dec_id = dec_page_table.dec_page_id
        state.documents.dec_page.processing_status = "parsed" if dec_page_table.parsed_json else "uploaded"

    _sync_life_application_state(state, life_insurance_datatable)
    workflow_context = _workflow_context(account, state, dec_page_table is not None)
      
    # ---- Conversation Memory Handling ----
    user_message = body.message

    # Ensure memory objects exist
    if state.memory.last_messages is None:
        state.memory.last_messages = []

    last_messages = state.memory.last_messages
    session_summary = state.memory.session_summary

    # 1. Append the user message to memory
    last_messages.append({
        "role": "user",
        "content": user_message
    })
    saved_user_message = models.Message(
            session_id = session_id,
            role = "user",
            content = user_message
        )
    db.add(saved_user_message)

    # 2. Determine intent using conversation context
    if dec_page_table and _is_dec_page_question(user_message):
        intent = {
            "intent": "gap_analysis",
            "confidence": 1.0,
            "notes": "deterministic_dec_page_question",
        }
    else:
        route_state = state.dict()
        route_state["workflow_context"] = workflow_context
        intent = context_manager(
            user_message,
            insurance_type,
            route_state,
            last_messages,
            session_summary
        )

    # temporary placeholder
    reply = None 
    
   
    if intent.get("intent") == "reset_estimate":
        _reset_life_estimate(life_insurance_datatable, state)
        _sync_life_application_state(state, life_insurance_datatable)
        workflow_context = _workflow_context(account, state, dec_page_table is not None)
        state.memory.last_messages = [{"role": "user", "content": user_message}]
        session.state = state.dict()
        db.add(life_insurance_datatable)
        reply = "Absolutely. I reset the estimate so we can start fresh. What age and gender should I use for the new life insurance estimate?"

    elif intent.get("intent") == "matching":
        missing = state.application.missing_fields
        was_completed = bool(state.application.completed)
        reply = lifeInsuranceAI(user_message, state, missing, last_messages, session_summary, workflow_context)
        if not isinstance(reply, dict) or reply.get("error"):
            reply = lifeInsuranceAI(user_message, state, missing, last_messages, session_summary, workflow_context)
        print(f'LLM reply: {reply}')

     # apply state_updates from LLM (session-level memory only)
        state_updates = reply.get("state_updates")
        if state_updates and isinstance(state_updates, dict):
            original_state = state.dict()
            updated_state = apply_state_updates(original_state, state_updates)
            if original_state != updated_state:
                try: 
                    state = LifeState(**updated_state)
                    session.state = state.dict()
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Invalid state update: {e}")
                
    # update fields
        field_updates = reply.get("updated_fields")

        if field_updates and isinstance(field_updates, dict):
            field_updates.pop("zip_risk", None)
            fixed_fields = validate_fields(field_updates)

            for field, value in fixed_fields.items():
                if not hasattr(life_insurance_datatable, field):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid field for LifeInsurance: {field}"
                    )
                setattr(life_insurance_datatable, field, value)
                # remove from refused_fields if user now provided the value
                if state.application.refused_fields and field in state.application.refused_fields:
                    state.application.refused_fields.pop(field, None)

            _sync_life_application_state(state, life_insurance_datatable)
        # clean up any False values left in refused_fields (from LLM overrides)
        if state.application.refused_fields:
            keys_to_remove = [k for k, v in state.application.refused_fields.items() if v is False]
            for k in keys_to_remove:
                state.application.refused_fields.pop(k, None)
        _sync_life_application_state(state, life_insurance_datatable)
        session.state = state.dict()


        reply = reply.get("response")
        
    
    # ML call

        life_quote = life_ml_helper(life_insurance_datatable)
        
        if life_quote is not None:
            state.application.ml_quote = life_quote
            _sync_life_application_state(state, life_insurance_datatable)
            session.state = state.dict()
            workflow_context = _workflow_context(account, state, dec_page_table is not None)
        
        if (not state.application.missing_fields
            and state.application.ml_quote
            and not was_completed
        ):
            state.application.completed = True
            session.state = state.dict()
            workflow_context = _workflow_context(account, state, dec_page_table is not None)
            completion_answer = lifeInsuranceAI(
                user_message,
                state,
                state.application.missing_fields,
                last_messages,
                session_summary,
                workflow_context,
            )
            completion_reply = completion_answer.get("response")
            if completion_reply:
                reply = completion_reply

        if not reply:
            retry_answer = lifeInsuranceAI(
                "The previous matching response was empty. Continue the life insurance conversation from the current state. Acknowledge the user's latest information from recent messages and ask the next appropriate question, or explain the completed preliminary estimate.",
                state,
                state.application.missing_fields,
                last_messages,
                session_summary,
                workflow_context,
            )
            reply = retry_answer.get("response")



    elif intent.get("intent") == "gap_analysis":
        if not dec_page_table:
            answer = lifeDecPageAnalysis(user_message, None, last_messages, session_summary)
            reply = answer.get("answer")

        else:
            answer = lifeDecPageAnalysis(user_message, dec_page_table.parsed_json, last_messages, session_summary)
            reply = answer.get("answer")

    elif intent.get("intent") == "meeting":
        # 1. Calculate missing from account (source of truth)
        missing = [
            field for field in REQUIRED_MEETING_FIELDS
            if is_missing(getattr(account, field, None))
        ]

        if not missing:
            if not account.meeting_requested:
                account.meeting_requested = True
                account.meeting_status = "requested"
                _send_meeting_email(account)
                account.meeting_status = "sent"

            workflow_context = _workflow_context(account, state, dec_page_table is not None)
            answer = meeting_organizer(
                user_message,
                [],
                last_messages,
                session_summary,
                workflow_context,
            )
            reply = answer.get("response")
            if not reply:
                retry_answer = meeting_organizer(
                    "The broker meeting fields are already collected. Confirm the meeting request and suggest the next useful action from workflow context.",
                    [],
                    last_messages,
                    session_summary,
                    workflow_context,
                )
                reply = retry_answer.get("response")
        else:
            # 2. Call meeting LLM only if we still need fields
            answer = meeting_organizer(user_message, missing, last_messages, session_summary, workflow_context)
            reply = answer.get("response")

            # 3. Apply DB updates from LLM extraction
            field_updates = answer.get("updated_fields")
            if field_updates:
                for field, value in field_updates.items():
                    if not hasattr(account, field):
                        raise HTTPException(400, f"Invalid meeting field: {field}")
                    setattr(account, field, value)



            # 4. Recalculate missing AFTER update
            missing_after = [
                field for field in REQUIRED_MEETING_FIELDS
                if is_missing(getattr(account, field, None))
            ]

            # 5. Finalize immediately if intake just completed
            if not missing_after and not account.meeting_requested:
                account.meeting_requested = True
                account.meeting_status = "requested"
                _send_meeting_email(account)
                account.meeting_status = "sent"

            workflow_context = _workflow_context(account, state, dec_page_table is not None)
            if not missing_after:
                final_answer = meeting_organizer(
                    user_message,
                    [],
                    last_messages,
                    session_summary,
                    workflow_context,
                )
                reply = final_answer.get("response") or reply
                if not reply:
                    retry_answer = meeting_organizer(
                        "The broker meeting fields are now collected. Confirm the meeting request and suggest the next useful action from workflow context.",
                        [],
                        last_messages,
                        session_summary,
                        workflow_context,
                    )
                    reply = retry_answer.get("response")
            else:
                followup_answer = meeting_organizer(
                    user_message,
                    missing_after,
                    last_messages,
                    session_summary,
                    workflow_context,
                )
                reply = followup_answer.get("response") or reply
                if not reply:
                    retry_answer = meeting_organizer(
                        "Ask the user for the next missing broker meeting field.",
                        missing_after,
                        last_messages,
                        session_summary,
                        workflow_context,
                    )
                    reply = retry_answer.get("response")
            

    elif intent.get("intent") == "explanation":
        ml_quote = state.application.ml_quote
        dec_page = dec_page_table.parsed_json if dec_page_table else None

        answered_fields = {}
        for field in ALL_LIFE_FIELDS:
            value = getattr(life_insurance_datatable, field, None)

            if value is not None:
                answered_fields[field] = value

        answer = lifeExplanation(user_message, answered_fields, ml_quote, dec_page, last_messages, None)


        reply = answer.get("response")
    
    elif intent.get("intent") == "other":
        answer = conversation_recovery(
            user_message,
            state.dict(),
            last_messages,
            session_summary,
            workflow_context,
        )
        reply = answer.get("response")

    # ---- Save assistant response to memory ----

    if isinstance(reply, dict):
        reply = reply.get("response")

    if not (reply and isinstance(reply, str) and reply.strip()):
        raise HTTPException(
            status_code=502,
            detail=f"{intent.get('intent', 'unknown')} handler did not return a response"
        )

    state.memory.last_messages.append({
        "role": "assistant",
        "content": reply
    })

    assistant_message = models.Message(
        session_id = session_id,
        role = "assistant",
        content = reply
    )
    db.add(assistant_message)

    workflow_context = _workflow_context(account, state, dec_page_table is not None)
    if len(state.memory.last_messages) > 10:
        summary = session_summarizer(
            state.memory.last_messages,
            state.memory.session_summary,
            state.dict(),
            workflow_context,
        )
        state.memory.session_summary = summary
        state.memory.last_messages = state.memory.last_messages[-5:]

    session.state = state.dict()
    db.add(session)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"intent": intent, "reply": reply, "state": state}
