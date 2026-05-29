import argparse
import json
import os
import sys
from typing import Any

import requests


API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "test-admin-token")
SITE_ID = os.environ.get("SITE_ID", "demo")


SCENARIOS: dict[str, dict[str, Any]] = {
    "clean": {
        "description": "Happy path quote intake, broker handoff, and admin detail check.",
        "watchpoints": [
            "BMI should extract from height and weight.",
            "Final quote should complete before the broker handoff.",
            "Admin detail should show name, email, phone, meeting status, quote, and high quality.",
        ],
        "messages": [
            "Hey, I want life insurance.",
            "I'm 30 and male.",
            "I'm 5 foot 10 and 180 pounds.",
            "I do not smoke.",
            "I want 500k coverage for a 20 year term.",
            "No diabetes, no high blood pressure, no heart disease, no cancer history.",
            "No family history, I don't drink, no driving violations, I work an office job, zip risk is 5.",
            "Can I talk to a broker?",
            "My name is Test Lead, my email is testlead@example.com, phone is 5551234567, tomorrow afternoon works.",
        ],
    },
    "quote_explanation": {
        "description": "Completed quote followed by pricing explanation questions.",
        "watchpoints": [
            "Explanation requests after quote completion should route to explanation, not matching.",
            "Bot should explain using the user's actual answered fields and quote.",
            "Bot should not invent carrier-specific underwriting details.",
        ],
        "messages": [
            "Hey, I want life insurance.",
            "I'm 30 and male.",
            "I'm 5 foot 10 and 180 pounds.",
            "I do not smoke.",
            "I want 500k coverage for a 20 year term.",
            "No diabetes, no high blood pressure, no heart disease, no cancer history.",
            "No family history, I don't drink, no driving violations, I work an office job, zip risk is 5.",
            "Why is my quote 42 dollars?",
            "What factors made my price higher or lower?",
        ],
    },
    "broker_handoff": {
        "description": "Completed quote followed by explicit broker/agent handoff.",
        "watchpoints": [
            "Broker request should route to meeting immediately after a completed quote.",
            "Bot should collect missing contact fields without repeating quote intake questions.",
            "Admin detail should persist contact info and meeting status.",
        ],
        "messages": [
            "Hey, I want life insurance.",
            "I'm 30 and male.",
            "I'm 5 foot 10 and 180 pounds.",
            "I do not smoke.",
            "I want 500k coverage for a 20 year term.",
            "No diabetes, no high blood pressure, no heart disease, no cancer history.",
            "No family history, I don't drink, no driving violations, I work an office job, zip risk is 5.",
            "Can I talk to a broker?",
            "My name is Test Lead, my email is testlead@example.com, phone is 5551234567, tomorrow afternoon works.",
        ],
    },
    "meeting_before_quote": {
        "description": "User asks for a broker before finishing intake.",
        "watchpoints": [
            "Meeting request should route to meeting even when quote intake is incomplete.",
            "Contact info should be saved without requiring every underwriting field first.",
            "Admin quality should reflect contact info plus incomplete intake.",
        ],
        "messages": [
            "I want life insurance.",
            "I'm 30 and male.",
            "Can I talk to a broker?",
            "My name is Early Lead, my email is earlylead@example.com, phone is 5552223333, tomorrow morning works.",
        ],
    },
    "correction": {
        "description": "User completes quote, then changes coverage and asks why it changed.",
        "watchpoints": [
            "Correction should update the existing application fields instead of starting over.",
            "Quote should recalculate after coverage changes.",
            "Follow-up explanation should reference the changed coverage amount.",
        ],
        "messages": [
            "Hey, I want life insurance.",
            "I'm 30 and male.",
            "I'm 5 foot 10 and 180 pounds.",
            "I do not smoke.",
            "I want 500k coverage for a 20 year term.",
            "No diabetes, no high blood pressure, no heart disease, no cancer history.",
            "No family history, I don't drink, no driving violations, I work an office job, zip risk is 5.",
            "Actually, make the coverage 750k instead.",
            "Can you explain why the quote changed?",
        ],
    },
    "invalid_options": {
        "description": "User asks for unsupported coverage and term values.",
        "watchpoints": [
            "Bot should not silently force unsupported values into valid values.",
            "Bot should guide the user back to supported coverage and term options.",
            "Admin detail should make it obvious if invalid values were accepted.",
        ],
        "messages": [
            "I want life insurance.",
            "I'm 30 and male.",
            "BMI is 25.8.",
            "I do not smoke.",
            "I want 300k coverage for 25 years.",
        ],
    },
    "messy": {
        "description": "Natural messy language with slang, uncertain values, and broker handoff.",
        "watchpoints": [
            "Bot should normalize messy but usable answers.",
            "Bot should ask follow-up questions for anything still missing.",
            "Broker handoff should still persist contact information.",
        ],
        "messages": [
            "yo i probably need life insurance but idk what im doing",
            "im like 29, guy",
            "not sure bmi, 5'9 maybe 175",
            "nah no smoking",
            "half a mil sounds fine maybe 20 years",
            "healthy, no big conditions",
            "social drinking, no tickets, software engineer, tempe area",
            "yeah send this to someone",
            "Aarsh Test, aarsh-test@example.com, 5559871234, friday morning",
        ],
    },
    "privacy": {
        "description": "User wants a quote but resists personal/contact and health questions.",
        "watchpoints": [
            "Bot should respect the user's privacy concern.",
            "Bot should explain why health details matter without pressuring for contact info.",
            "Bot should not fabricate a complete quote if required underwriting fields are missing.",
        ],
        "messages": [
            "I want a quote but I don't want to give my name yet.",
            "I'm 35, female, non smoker.",
            "BMI is 23.5.",
            "250k coverage, 20 year term.",
            "I'd rather not answer health questions right now.",
        ],
    },
}


def request_json(method: str, path: str, **kwargs) -> dict[str, Any]:
    response = requests.request(method, f"{API_BASE_URL}{path}", timeout=90, **kwargs)
    try:
        payload = response.json()
    except Exception:
        payload = {"raw": response.text}

    if not response.ok:
        raise RuntimeError(f"{method} {path} failed: {response.status_code} {payload}")

    return payload


def create_session() -> tuple[str, str]:
    account = request_json("POST", "/accounts", json={"site_id": SITE_ID})
    session = request_json(
        "POST",
        f"/accounts/{account['account_id']}/sessions",
        json={"insurance_type": "life"},
    )
    return account["account_id"], session["session_id"]


def send_chat(session_id: str, message: str) -> dict[str, Any]:
    return request_json(
        "POST",
        "/chat/router",
        params={"session_id": session_id},
        json={"message": message},
    )


def fetch_admin_detail(session_id: str) -> dict[str, Any]:
    return request_json(
        "GET",
        f"/admin/leads/{session_id}",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
    )


def print_turn(step: int, user_message: str, data: dict[str, Any]) -> None:
    reply = data.get("reply") or data.get("response")
    state = data.get("state") or {}
    application = state.get("application") or {}
    intent = data.get("intent") or {}

    print(f"\n--- TURN {step} ---")
    print(f"USER: {user_message}")
    print(f"INTENT: {intent.get('intent')} confidence={intent.get('confidence')}")
    print(f"BOT: {reply}")
    print(f"MISSING: {application.get('missing_fields')}")
    print(f"ANSWERED: {json.dumps(application.get('answered_fields') or {}, default=str)}")
    print(f"QUOTE: {application.get('ml_quote')}")
    print(f"COMPLETED: {application.get('completed')}")


def print_scenario_catalog() -> None:
    print("Available manual life flow scenarios:\n")
    for name, scenario in sorted(SCENARIOS.items()):
        print(f"- {name}: {scenario['description']}")


def print_scenario_header(name: str) -> None:
    scenario = SCENARIOS[name]
    print(f"DESCRIPTION: {scenario['description']}")
    print("WATCHPOINTS:")
    for watchpoint in scenario.get("watchpoints") or []:
        print(f"- {watchpoint}")


def print_admin_summary(session_id: str) -> None:
    detail = fetch_admin_detail(session_id)
    account = detail.get("account") or {}
    state = detail.get("state") or {}
    application = state.get("application") or {}

    print("\n=== ADMIN DETAIL CHECK ===")
    print(f"NAME: {account.get('name')}")
    print(f"EMAIL: {account.get('email')}")
    print(f"PHONE: {account.get('phone')}")
    print(f"MEETING: {account.get('meeting_status')}")
    print(f"QUALITY: {detail.get('lead_quality')}")
    print(f"QUOTE: {application.get('ml_quote')}")
    print(f"MISSING: {application.get('missing_fields')}")
    print(f"MESSAGES: {len(detail.get('messages') or [])}")
    print(f"SUMMARY: {(state.get('memory') or {}).get('session_summary')}")


def run_scenario(name: str, pause: bool) -> None:
    messages = SCENARIOS[name]["messages"]
    account_id, session_id = create_session()

    print("=== MANUAL LIFE FLOW ===")
    print(f"SCENARIO: {name}")
    print(f"ACCOUNT: {account_id}")
    print(f"SESSION: {session_id}")
    print(f"API: {API_BASE_URL}")
    print_scenario_header(name)

    for index, message in enumerate(messages, start=1):
        data = send_chat(session_id, message)
        print_turn(index, message, data)
        if pause and index != len(messages):
            input("\nPress Enter for next message...")

    print_admin_summary(session_id)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a manual InsuranceAI life intake transcript.")
    parser.add_argument(
        "scenario",
        choices=sorted(SCENARIOS.keys()),
        nargs="?",
        default="clean",
    )
    parser.add_argument("--list", action="store_true", help="List available scenarios and exit.")
    parser.add_argument("--pause", action="store_true", help="Pause between turns.")
    args = parser.parse_args()

    if args.list:
        print_scenario_catalog()
        return 0

    try:
        run_scenario(args.scenario, args.pause)
        return 0
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
