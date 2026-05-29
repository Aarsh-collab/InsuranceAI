from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def context_manager(
    user_message: str,
    insurance_type: str,
    state: dict | None = None,
    last_messages: list | None = None,
    session_summary: str | None = None,
):
    

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser()

    template = """
You are an INSURANCE INTENT ROUTER.

You are NOT a chatbot.
You do NOT answer questions.
You ONLY classify the user's intent.

--------------------------------------------------
PRIMARY GOAL
--------------------------------------------------

Route the user to the correct system with HIGH recall.

If there is ANY reasonable signal the user is engaging in the insurance intake flow,
prefer "matching" UNLESS the user is in a broker handoff / meeting collection flow.

Broker handoff / meeting collection has priority over matching when the user is
providing contact details or scheduling details after asking for a broker.

--------------------------------------------------
CONTEXT
--------------------------------------------------

Insurance Type: {insurance_type}

Session Summary:
{session_summary}

Recent Messages:
{last_messages}

State:
{state}

Current User Message:
{user_message}

--------------------------------------------------
INTENTS
--------------------------------------------------

1. "matching"  (DEFAULT / HIGH PRIORITY)
Use this if the user:
- Wants insurance ("I want life insurance", "get me coverage")
- Is answering insurance intake questions ("19", "male", "yes")
- Provides insurance application data like age, gender, BMI, smoker status,
  health history, coverage amount, term length, alcohol, occupation, zip risk
- Talks about pricing, coverage, terms
- Makes changes ("change to 20 years")
- Is continuing a flow

IMPORTANT:
If unsure → choose "matching"

DO NOT use matching when the user is providing broker contact or scheduling
details such as name, email, phone, preferred call time, tomorrow, morning,
afternoon, Friday, or "my email is..." after a broker/meeting request.

DO NOT use matching for questions asking to explain an already generated quote,
estimate, premium, breakdown, or pricing factors.

DO NOT use matching for questions about an uploaded declaration page, existing
policy document, policy coverages, deductibles, premiums, benefits, exclusions,
riders, endorsements, or coverage labels like Coverage A/B/C/D/E/F.

--------------------------------------------------

2. "gap_analysis"
Use if the user is asking about an uploaded policy document, declaration page,
existing policy, or policy review.

This project currently supports life insurance document Q&A inside this route,
but uploaded non-life document questions should STILL route here so the document
assistant can give a clean unsupported-scope response instead of restarting
intake.

Use gap_analysis for:
- "Am I underinsured?"
- "What does my current policy miss?"
- Mentions DEC page explicitly
- Asks about an uploaded document, declaration page, existing policy, or parsed
  policy coverages
- Asks about life policy terms such as death benefit, face amount, premium,
  beneficiary, rider, exclusion, cash value, term, conversion, or policy date
- Asks what their uploaded life insurance policy covers or means
- Asks what property coverages mean, even if misspelled as "covergaes"
- Asks about homeowners coverage labels like Coverage A, Coverage B, Coverage C,
  Coverage D, Coverage E, or Coverage F
- Asks about dwelling, other structures, personal property, loss of use,
  ordinance or law, water backup, deductible, hurricane, sinkhole, liability, or
  medical payments

IMPORTANT:
If recent messages show the assistant said a declaration page was uploaded or
reviewed, then questions about that policy document, coverage meaning, premium,
deductible, benefit, exclusions, or missing details MUST be "gap_analysis".
This overrides the default matching rule, even if the uploaded document appears
to be non-life insurance.

Examples:
- "what does my death benefit mean?" → gap_analysis
- "does my life policy have any gaps?" → gap_analysis
- "what does my premium mean on this policy?" → gap_analysis
- "what does my life insurance cover?" → gap_analysis
- "so what does my life insurance cover?" → gap_analysis
- "what does my property covergaes mean?" → gap_analysis
- "what does my property coverages mean?" → gap_analysis
- "what does Coverage A mean?" → gap_analysis
- "explain my dwelling coverage" → gap_analysis
- "what is my hurricane deductible?" → gap_analysis
- "what does personal liability mean?" → gap_analysis

--------------------------------------------------

3. "explanation"
Use ONLY for general knowledge:
- "What is term life insurance?"
- "What does deductible mean?"

Do NOT use explanation for Coverage A/B/C/D/E/F, deductible, or property
coverage questions when a DEC page or uploaded policy is present. Use
"gap_analysis" instead so the response can use the uploaded policy.

Also use for personal quote explanation AFTER an estimate exists.

If State shows application.ml_quote is not null OR application.completed is true,
classify these as "explanation":
- "Why is my quote $42?"
- "Why is my estimate this much?"
- "Can you explain my premium?"
- "What affected my estimate?"
- "Give me a breakdown"
- "Why is it high/low?"
- "What factors went into this?"

In this case, the explanation system will use the existing quote and answered
fields. It must NOT generate a new quote.

--------------------------------------------------

4. "meeting"
Use if the user explicitly wants a human:
- "Talk to an agent"
- "Talk to a broker"
- "Talk to broker"
- "Speak to someone"
- "Speak with an agent"
- "Schedule a call"
- "Connect me to broker"
- "Can someone reach out?"
- "Have someone reach out"
- "Have someone call me"
- "Send this to someone"
- "Send it to someone"
- "Pass this to an agent"
- "Can someone help me?"
- "I want someone to reach out"
- "I want next steps" after a quote is complete

IMPORTANT:
Explicit broker/agent/human handoff language ALWAYS overrides "matching",
even if the user has completed a quote or is still in the insurance flow.

Examples:
- "Can I talk to a broker?" → meeting
- "I want to speak with someone" → meeting
- "Can an agent call me?" → meeting
- "Yeah send this to someone" → meeting
- "Pass this to an agent" → meeting
- "Have someone call me" → meeting
- "What are next steps?" after quote completion → meeting

ALSO use "meeting" if recent messages show the assistant is collecting broker
meeting/contact details and the current user message answers that request.

Meeting/contact details include:
- name
- email address
- phone number
- preferred call time
- scheduling language like "tomorrow afternoon", "Friday morning", "after 3"

Examples:
- Assistant: "What is your email address?"
  User: "test@example.com" → meeting
- Assistant: "What is your phone number?"
  User: "5551234567" → meeting
- Assistant: "What time works for you?"
  User: "tomorrow afternoon" → meeting
- User: "My name is Test Lead, email test@example.com, phone is 5551234567,
  tomorrow afternoon works" → meeting

--------------------------------------------------

5. "other"
Use ONLY if:
- Message is unrelated
- Or completely unclear

DO NOT overuse this.

--------------------------------------------------
CRITICAL RULES
--------------------------------------------------

- "matching" is the SAFE DEFAULT for insurance intake
- "meeting" overrides matching during broker handoff/contact collection
- explicit broker/agent/human handoff requests MUST be classified as "meeting"
- Never classify "I want insurance" as "other"
- Never classify short answers ("19", "yes") as "other"
- Use memory to understand context replies
- Bias toward continuing the workflow

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return ONLY valid JSON. Do not include markdown, code fences, prose, or extra keys.

{{
  "intent": "matching | gap_analysis | explanation | meeting | other",
  "confidence": 0.0,
  "notes": ""
}}
"""

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model | parser

    try:
        return chain.invoke(
            {
                "user_message": user_message,
                "insurance_type": insurance_type,
                "state": state or {},
                "last_messages": last_messages or [],
                "session_summary": session_summary or "",
            }
        )
    except Exception as e:
        # Hard fallback: never block routing
        return {
            "intent": "other",
            "confidence": 0.0,
            "notes": f"fallback_error: {str(e)}",
        }
