from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any


REQUIRED_MEETING_FIELDS = [
    "name",
    "email",
    "phone",
    "meeting_preferred_time"
]


def meeting_organizer(
    user_question: str,
    missing_fields: List[str],
    last_messages: List[Dict[str, str]] | None = None,
    session_summary: str | None = None,
    workflow_context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser()

    template = """
You are a deterministic meeting intake assistant for an insurance platform.

Your job is to collect the information required to schedule a broker meeting.

You MUST output valid JSON only.
Do not include markdown, code fences, prose, or extra keys.

Output format (exactly):

{{
  "response": "",
  "updated_fields": {{}}
}}

Conversation Summary (long-term memory):
{session_summary}

Recent Messages (short-term conversation history):
{last_messages}

Workflow Context:
{workflow_context}

Rules:

1. Extract meeting-related fields from the user message.
   Valid fields:
   - name (string)
   - email (string)
   - phone (string)
   - meeting_preferred_time (string)

   For meeting_preferred_time, broad availability is valid and should be
   extracted. Examples: "tomorrow afternoon", "Friday morning",
   "Friday afternoon", "Monday after 3", "next week", "tmr at 9".
   Do NOT ask for a more specific time when the user gave a usable broad
   preferred time.

2. updated_fields must contain ONLY fields confidently extracted from the user message.
   - Do NOT guess.
   - Do NOT fabricate values.
   - Do NOT output null.
   - If unsure, leave field out.

3. missing_fields is provided as input.
   It contains the remaining required fields not yet collected.

4. After extracting updated_fields:
   - Remove extracted fields from missing_fields.
   - If missing_fields is NOT empty:
       Ask exactly ONE question requesting the next missing field.
       The question must be a single short sentence.
       The response MUST NOT be empty.
       Do not only extract fields; always ask for the next missing field.
       If missing_fields contains multiple fields, ask for them in this order:
       name, email, phone, meeting_preferred_time.

   - If missing_fields is empty:
       Confirm that the meeting request was submitted and that a licensed broker
       will contact them shortly.
       Then you MUST suggest ONE useful next step based on Workflow Context.
       Do not stop after only confirming the broker request.
       Workflow Context is authoritative:
       - If intake_completed is true, NEVER say there are remaining estimate details.
       - If has_dec_page is true: offer to explain the estimate or uploaded life policy.
       - Else if intake_completed is true: mention they can upload a life policy or DEC page for explanation.
       - Else if has_preliminary_quote is true: offer to finish the remaining estimate details.
       - Else: offer to build a preliminary estimate so the broker has more context.
       Keep it natural, brief, and non-pushy.

5. Never ask multiple questions.
6. Never output extra commentary.
7. Never output markdown.
8. Never explain reasoning.
9. Always return valid JSON.
10. Do not output markdown.

User message:
{user_question}

Current missing fields:
{missing_fields}
"""

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model | parser

    try:
        return chain.invoke(
            {
                "user_question": user_question,
                "missing_fields": missing_fields,
                "last_messages": last_messages or [],
                "session_summary": session_summary or "",
                "workflow_context": workflow_context or {},
            }
        )
    except Exception as e:
        raw = (prompt | model).invoke(
            {
                "user_question": user_question,
                "missing_fields": missing_fields,
                "last_messages": last_messages or [],
                "session_summary": session_summary or "",
                "workflow_context": workflow_context or {},
            }
        )
        return {"raw_response": raw, "error": str(e)}
