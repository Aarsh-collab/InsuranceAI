from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI



def decPageParser(decpage_text: str):
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser()

    template = """
  You are a STRICT insurance declaration (DEC) page parser.

  Your task is to extract ONLY factual, explicitly stated information from an insurance declaration page.
  The document may be for ANY insurance type (life, homeowners, auto, renters, umbrella, etc.).

  You MUST return ONLY valid JSON.
  Any extra text, explanation, markdown, code fences, or wrapping keys will make
  the output INVALID.

  ABSOLUTE RULES (NON-NEGOTIABLE):
  - Output MUST be valid JSON and MUST match the schema exactly.
  - Do NOT wrap the output in "reply", "result", "data", or any other top-level key.
  - If you do, the output is INVALID.
  - Use null for any value that is missing, unclear, or not explicitly stated.
  - Do NOT infer, guess, estimate, calculate, or normalize anything.
  - Do NOT rewrite labels or rename coverage fields.
  - Extract ONLY what is explicitly written on the document.
  - If a value is not clearly present, set it to null.

  DATE RULES:
  - If a date range appears (e.g. "3/28/20 to 3/28/2021"):
    - effective_date MUST be the start date
    - expiration_date MUST be the end date
  - Returning a combined date range string is INVALID.

  COVERAGE RULES:
  - "coverage" may be:
    - a single numeric value (e.g. life insurance face amount), OR
    - an object with multiple labeled coverage entries (e.g. homeowners, auto).
  - Preserve coverage labels exactly as written in the document.

  NAME RULES:
  - If multiple insured parties are listed, combine them into ONE string.
  - Do NOT split names into arrays.
  NUMBER FORMATTING RULES:
  - For money amounts (premium value and coverage amounts), output MUST be a number, not a string.
    - Example: 854 (or 854.0) NOT "$854" and NOT "854 dollars".
  - Do NOT include currency symbols, commas, or units inside numeric fields.
  - Keep `premium.currency` as a 3-letter code like "USD" when present.
  - Preserve the exact magnitude of the amount shown in the document.
  - NEVER add zeros, infer rounded amounts, or change thousands.
    - "$5,000" MUST be 5000, NOT 50000.
    - "$3,200" MUST be 3200, NOT 32000.
    - "$104,250" MUST be 104250, NOT 1042500.
  - If a coverage row has a limit and a separate premium, use the LIMIT OF
    LIABILITY value as the coverage amount, not the premium.
  - If a row says "Included" in the premium column, do NOT treat "Included" as
    a coverage amount.

  SCHEMA (YOU MUST FOLLOW THIS STRUCTURE EXACTLY):

{{
  "insurance_type": null,

  "insured": {{
    "full_name": null,
    "address": null,
    "zip_code": null
  }},

  "policy": {{
    "policy_number": null,
    "carrier": null,
    "policy_type": null,
    "effective_date": null,
    "expiration_date": null,
    "term_length_years": null,

    "coverage": null,

    "premium": {{
      "value": int,
      "currency": null,
      "period": null
    }}
  }},

  "metadata": {{
    "source": "dec_page",
    "confidence": null
  }}
}}

FINAL CHECK BEFORE RESPONDING:
- Top-level JSON must start with "insurance_type"
- No wrapper keys allowed
- All keys must exist (use null if needed)
- Output must be parsable JSON

Insurance declaration page text:
{decpage_text}
"""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model | parser

    try:
        return chain.invoke({'decpage_text': decpage_text})
    except Exception as e:
        # parser throws if model doesn't output JSON
        # you can still fall back to manual cleaning if you want
        raw = (prompt | model).invoke({'decpage_text': decpage_text})
        return {"raw_response": raw, "error": str(e)}
