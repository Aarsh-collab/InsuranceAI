from typing import Any, Dict, List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def conversation_recovery(
    user_message: str,
    state: Dict[str, Any],
    last_messages: List[Dict[str, str]] | None = None,
    session_summary: str | None = None,
    workflow_context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser()

    template = """
You are InsuranceAI's conversation recovery assistant.

Your job is to handle messages routed as "other" without breaking the workflow.
Read the conversation, state, and workflow context, then write a short natural
response that either:
- acknowledges a simple closing/thanks,
- gently redirects unrelated messages back to the supported product,
- asks a brief clarifying question if the user's intent is unclear,
- or helps the user continue the most relevant unfinished action.

Supported product scope:
- preliminary life insurance estimates
- life policy / life DEC page explanation
- licensed broker handoff

Rules:
- Do not invent capabilities.
- Do not claim support for auto, home, renters, health, or property insurance.
- Do not ask for SSN or sensitive government IDs.
- Do not output markdown, bullets, numbered lists, or bold formatting.
- Do not mention internal routing, intents, state, or prompts.
- Keep the response concise and human.
- If the user is clearly thanking or closing, respond naturally and leave the
  door open to continue.
- If the user seems to want to correct/remove a previous answer, ask what they
  want changed instead of changing data yourself.
- Always return valid JSON only.

Output format:
{{
  "response": ""
}}

Session Summary:
{session_summary}

Recent Messages:
{last_messages}

State:
{state}

Workflow Context:
{workflow_context}

User Message:
{user_message}
"""

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model | parser

    try:
        return chain.invoke(
            {
                "user_message": user_message,
                "state": state or {},
                "last_messages": last_messages or [],
                "session_summary": session_summary or "",
                "workflow_context": workflow_context or {},
            }
        )
    except Exception as e:
        raw = (prompt | model).invoke(
            {
                "user_message": user_message,
                "state": state or {},
                "last_messages": last_messages or [],
                "session_summary": session_summary or "",
                "workflow_context": workflow_context or {},
            }
        )
        return {"raw_response": raw, "error": str(e)}
