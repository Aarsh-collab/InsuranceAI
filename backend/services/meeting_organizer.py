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


def meeting_organizer(user_question: str, missing_fields: List[str], last_messages: List[Dict[str, str]] | None = None, session_summary: str | None = None) -> Dict[str, Any]:

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

Rules:

1. Extract meeting-related fields from the user message.
   Valid fields:
   - name (string)
   - email (string)
   - phone (string)
   - meeting_preferred_time (string)

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

   - If missing_fields is empty:
       response must be exactly:
       "Your meeting request has been submitted. A licensed broker will contact you shortly."

5. Never ask multiple questions.
6. Never output extra commentary.
7. Never output markdown.
8. Never explain reasoning.
9. Always return valid JSON.

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
            }
        )
    except Exception as e:
        raw = (prompt | model).invoke(
            {
                "user_question": user_question,
                "missing_fields": missing_fields,
                "last_messages": last_messages or [],
                "session_summary": session_summary or "",
            }
        )
        return {"raw_response": raw, "error": str(e)}
