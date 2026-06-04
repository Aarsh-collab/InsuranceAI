from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def session_summarizer(last_messages: str, session_summary: str, current_state=None, workflow_context=None):

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    template = """
        You are a memory compression engine for an AI insurance advisor system.

    Your job is to maintain a concise running summary of the conversation between the user and the insurance assistant.

    The summary is used as long-term memory so the system can remember important facts even when older messages are removed.

    You will receive:
    1. The previous session summary
    2. The most recent conversation messages
    3. The current structured state

    Your task:
    Update the session summary to include any new important information.

    IMPORTANT RULES:

    Only include important facts such as:
    - User identity (name, email, phone)
    - Insurance goals
    - Coverage preferences
    - Health or underwriting factors
    - Current policy details
    - Important decisions made
    - Meeting scheduling info

    Do NOT include:
    - greetings
    - filler conversation
    - repeated questions
    - assistant explanations
    - small talk

    Keep the summary concise and factual.

    Maximum length: 120 words.

    Write in clear third-person factual statements.

    Do NOT repeat information that already exists in the previous summary unless it changes.

    If the previous summary conflicts with the current structured state or the
    newest messages, the current structured state and newest messages win.
    Remove stale values instead of preserving them.

    If a quote, coverage amount, term, contact info, meeting status, or missing
    field changed, the summary must reflect the current value.

    The output must be ONLY the updated summary text.
    No extra commentary.

    Here is the previous summary:
    {session_summary}

    Here is the last messages: 
    {last_messages}

    Here is the current structured state:
    {current_state}

    Here is the current workflow context:
    {workflow_context}
        """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model | StrOutputParser()

    try:
        return chain.invoke(
            {
                "last_messages": last_messages,
                "session_summary": session_summary,
                "current_state": current_state or {},
                "workflow_context": workflow_context or {},
            }
        )
    except Exception as e:
        raw = (prompt | model).invoke(
            {
                "last_messages": last_messages,
                "session_summary": session_summary,
                "current_state": current_state or {},
                "workflow_context": workflow_context or {},
            }
        )
        return {"raw_response": raw, "error": str(e)}
