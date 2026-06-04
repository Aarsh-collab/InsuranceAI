import argparse
import json
import os
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

import requests


API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "test-admin-token")
SITE_ID = os.environ.get("SITE_ID", "demo")
DEFAULT_LOG_DIR = Path(__file__).resolve().parents[2] / "docs" / "manual-flow-runs"


COMMON_CLEAN_INTAKE = [
    "Hey, I want life insurance.",
    "I'm 30 and male.",
    "I'm 5 foot 10 and 180 pounds.",
    "I do not smoke.",
    "I want 500k coverage for a 20 year term.",
    "No diabetes, no high blood pressure, no heart disease, no cancer history.",
    "No family history, I don't drink, no driving violations, I work an office job, zip risk is 5.",
]


SCENARIOS: dict[str, dict[str, Any]] = {
    "clean": {
        "description": "Happy path quote intake, broker handoff, and admin detail check.",
        "watchpoints": [
            "BMI should extract from height and weight.",
            "Final quote should complete before the broker handoff.",
            "Admin detail should show name, email, phone, meeting status, quote, and high quality.",
        ],
        "messages": [
            *COMMON_CLEAN_INTAKE,
            "Can I talk to a broker?",
            "My name is Test Lead, my email is testlead@example.com, phone is 5551234567, tomorrow afternoon works.",
        ],
        "expected_intents": [
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "meeting",
            "meeting",
        ],
        "expect": {
            "completed": True,
            "quote": True,
            "meeting_status": "sent",
            "account_fields": ["name", "email", "phone"],
            "missing_fields": [],
        },
    },
    "quote_explanation": {
        "description": "Completed quote followed by pricing explanation questions.",
        "watchpoints": [
            "Explanation requests after quote completion should route to explanation, not matching.",
            "Bot should explain using the user's actual answered fields and quote.",
            "Bot should not invent carrier-specific underwriting details.",
        ],
        "messages": [
            *COMMON_CLEAN_INTAKE,
            "Why is my quote 42 dollars?",
            "What factors made my price higher or lower?",
        ],
        "expected_intents": [
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "explanation",
            "explanation",
        ],
        "expect": {
            "completed": True,
            "quote": True,
            "meeting_status": None,
            "missing_fields": [],
        },
    },
    "broker_handoff": {
        "description": "Completed quote followed by explicit broker/agent handoff.",
        "watchpoints": [
            "Broker request should route to meeting immediately after a completed quote.",
            "Bot should collect missing contact fields without repeating quote intake questions.",
            "Admin detail should persist contact info and meeting status.",
        ],
        "messages": [
            *COMMON_CLEAN_INTAKE,
            "Can I talk to a broker?",
            "My name is Test Lead, my email is testlead@example.com, phone is 5551234567, tomorrow afternoon works.",
        ],
        "expected_intents": [
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "meeting",
            "meeting",
        ],
        "expect": {
            "completed": True,
            "quote": True,
            "meeting_status": "sent",
            "account_fields": ["name", "email", "phone"],
            "missing_fields": [],
        },
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
        "expected_intents": ["matching", "matching", "meeting", "meeting"],
        "expect": {
            "completed": False,
            "quote": False,
            "meeting_status": "sent",
            "account_fields": ["name", "email", "phone"],
            "missing_includes": ["bmi", "smoker", "coverage_amount", "term_length"],
        },
    },
    "correction": {
        "description": "User completes quote, then changes coverage and asks why it changed.",
        "watchpoints": [
            "Correction should update the existing application fields instead of starting over.",
            "Quote should recalculate after coverage changes.",
            "Follow-up explanation should reference the changed coverage amount.",
        ],
        "messages": [
            *COMMON_CLEAN_INTAKE,
            "Actually, make the coverage 750k instead.",
            "Can you explain why the quote changed?",
        ],
        "expected_intents": [
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "explanation",
        ],
        "expect": {
            "completed": True,
            "quote": True,
            "answered_fields": {"coverage_amount": 750000},
            "missing_fields": [],
        },
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
        "expected_intents": ["matching", "matching", "matching", "matching", "matching"],
        "expect": {
            "completed": False,
            "quote": False,
            "missing_includes": ["coverage_amount", "term_length"],
            "answered_absent": ["coverage_amount", "term_length"],
        },
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
        "expected_intents": [
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "meeting",
            "meeting",
        ],
        "expect": {
            "completed": False,
            "quote": True,
            "meeting_status": "sent",
            "account_fields": ["name", "email", "phone"],
            "missing_includes": ["family_history_count"],
        },
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
        "expected_intents": ["matching", "matching", "matching", "matching", "matching"],
        "expect": {
            "completed": False,
            "quote": True,
            "missing_includes": [
                "diabetes",
                "high_bp",
                "heart_disease",
                "cancer_history",
                "family_history_count",
            ],
        },
    },
    "broker_first_then_quote": {
        "description": "Broker handoff is completed first, then user continues the quote intake.",
        "watchpoints": [
            "Meeting completion should not trap later quote answers in the meeting route.",
            "User can continue quote intake after broker request is already sent.",
            "Smoker, coverage, and health answers should still route to matching.",
        ],
        "messages": [
            "hello",
            "I want to meet with a broker, my name is Aarsh Test, my phone number is 5559871111, and my email is aarsh-broker-first@example.com and tomorrow at 9 works.",
            "yes lets do the quote",
            "I'm 19 male.",
            "im about 5 foot 9 and 160 lbs",
            "non-smoker",
            "500k for 20 years",
            "healthy, no diabetes, no high blood pressure, no heart disease, no cancer.",
            "no family history, no drinking, no tickets, student office job, zip risk 5",
        ],
        "expected_intents": [
            "matching",
            "meeting",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
        ],
        "expect": {
            "completed": True,
            "quote": True,
            "meeting_status": "sent",
            "account_fields": ["name", "email", "phone"],
            "missing_fields": [],
        },
    },
    "partial_meeting_then_quote_then_finish_meeting": {
        "description": "User starts broker handoff, switches to quote, then finishes broker contact.",
        "watchpoints": [
            "Partial meeting data should persist.",
            "Quote flow should continue after a partial meeting handoff.",
            "Later phone/time should finalize the meeting request.",
        ],
        "messages": [
            "I want life insurance.",
            "Can I talk to a broker? My name is Partial Lead and my email is partiallead@example.com.",
            "Actually can we get a quote first?",
            "I'm 41 female.",
            "BMI 24.2.",
            "I do not smoke.",
            "250k for 20 years.",
            "No diabetes, blood pressure, heart disease, or cancer.",
            "No family history, no alcohol, no violations, office worker, zip risk 4.",
            "My phone is 5554443333 and Friday afternoon works.",
        ],
        "expected_intents": [
            "matching",
            "meeting",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "meeting",
        ],
        "expect": {
            "completed": True,
            "quote": True,
            "meeting_status": "sent",
            "account_fields": ["name", "email", "phone"],
            "missing_fields": [],
        },
    },
    "route_switch_marathon": {
        "description": "Stress test: quote, explanation, correction, broker handoff, thanks, then more quote changes.",
        "watchpoints": [
            "Router should switch cleanly between matching, explanation, and meeting.",
            "Corrections after explanation should update fields and recalculate quote.",
            "Thanks after meeting should not cause a repeated meeting loop.",
            "Changing coverage after meeting should route back to matching.",
        ],
        "messages": [
            *COMMON_CLEAN_INTAKE,
            "Why is it that price?",
            "Actually make it 750k.",
            "Why did it change?",
            "Have someone call me.",
            "Route Switch, route-switch@example.com, 5551112222, Monday morning.",
            "thanks",
            "Actually change it back to 500k.",
            "Can you explain the new quote?",
        ],
        "expected_intents": [
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "matching",
            "explanation",
            "matching",
            "explanation",
            "meeting",
            "meeting",
            "other",
            "matching",
            "explanation",
        ],
        "expect": {
            "completed": True,
            "quote": True,
            "meeting_status": "sent",
            "answered_fields": {"coverage_amount": 500000},
            "missing_fields": [],
        },
    },
    "document_question_no_upload": {
        "description": "User asks life policy / DEC questions before uploading a document.",
        "watchpoints": [
            "Life policy questions should route to gap_analysis rather than starting quote intake.",
            "Assistant should not ask age/gender for document questions.",
        ],
        "messages": [
            "What does death benefit mean on a life policy?",
            "Can you review my life insurance policy if I upload it?",
            "Does my policy have gaps?",
        ],
        "expected_intents": ["gap_analysis", "gap_analysis", "gap_analysis"],
        "expect": {
            "completed": False,
            "quote": False,
        },
    },
    "off_topic_recovery": {
        "description": "Off-topic message followed by normal quote intake.",
        "watchpoints": [
            "Unrelated questions should not corrupt the life application.",
            "The user should still be able to start quote intake afterward.",
        ],
        "messages": [
            "what is the weather today?",
            "Actually I need life insurance.",
            "I'm 28 female.",
            "BMI is 22.8.",
            "non smoker",
        ],
        "expected_intents": ["other", "matching", "matching", "matching", "matching"],
        "expect": {
            "completed": False,
            "quote": False,
            "answered_fields": {"age": 28, "gender": "female", "bmi": 22.8, "smoker": "non_smoker"},
        },
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


def assert_turn_expectation(
    scenario_name: str,
    step: int,
    expected_intent: str | None,
    data: dict[str, Any],
) -> None:
    if not expected_intent:
        return

    actual_intent = (data.get("intent") or {}).get("intent")
    if actual_intent != expected_intent:
        raise AssertionError(
            f"{scenario_name} turn {step}: expected intent {expected_intent!r}, got {actual_intent!r}"
        )

    reply = data.get("reply") or data.get("response")
    if reply is None:
        raise AssertionError(f"{scenario_name} turn {step}: assistant reply was None")


def assert_final_expectations(
    scenario_name: str,
    detail: dict[str, Any],
    expectations: dict[str, Any],
) -> None:
    account = detail.get("account") or {}
    state = detail.get("state") or {}
    application = state.get("application") or {}
    answered = application.get("answered_fields") or {}
    missing = application.get("missing_fields") or []

    if "completed" in expectations and application.get("completed") != expectations["completed"]:
        raise AssertionError(
            f"{scenario_name}: expected completed={expectations['completed']}, "
            f"got {application.get('completed')}"
        )

    if expectations.get("quote") is True and application.get("ml_quote") is None:
        raise AssertionError(f"{scenario_name}: expected a quote, got None")

    if expectations.get("quote") is False and application.get("ml_quote") is not None:
        raise AssertionError(
            f"{scenario_name}: expected no quote, got {application.get('ml_quote')}"
        )

    if "meeting_status" in expectations and account.get("meeting_status") != expectations["meeting_status"]:
        raise AssertionError(
            f"{scenario_name}: expected meeting_status={expectations['meeting_status']!r}, "
            f"got {account.get('meeting_status')!r}"
        )

    for field in expectations.get("account_fields") or []:
        if not account.get(field):
            raise AssertionError(f"{scenario_name}: expected account.{field} to be populated")

    if "missing_fields" in expectations and missing != expectations["missing_fields"]:
        raise AssertionError(
            f"{scenario_name}: expected missing_fields={expectations['missing_fields']}, got {missing}"
        )

    for field in expectations.get("missing_includes") or []:
        if field not in missing:
            raise AssertionError(f"{scenario_name}: expected {field!r} in missing_fields, got {missing}")

    for field in expectations.get("answered_absent") or []:
        if field in answered:
            raise AssertionError(f"{scenario_name}: expected {field!r} to be absent from answered_fields")

    for field, expected_value in (expectations.get("answered_fields") or {}).items():
        actual_value = answered.get(field)
        if actual_value != expected_value:
            raise AssertionError(
                f"{scenario_name}: expected answered_fields[{field!r}]={expected_value!r}, "
                f"got {actual_value!r}"
            )


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


def print_admin_summary(session_id: str) -> dict[str, Any]:
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
    return detail


def run_scenario(name: str, pause: bool, assert_expectations: bool) -> None:
    scenario = SCENARIOS[name]
    messages = scenario["messages"]
    expected_intents = scenario.get("expected_intents") or []
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
        if assert_expectations:
            expected_intent = expected_intents[index - 1] if index <= len(expected_intents) else None
            assert_turn_expectation(name, index, expected_intent, data)
        if pause and index != len(messages):
            input("\nPress Enter for next message...")

    detail = print_admin_summary(session_id)
    if assert_expectations:
        assert_final_expectations(name, detail, scenario.get("expect") or {})


def run_all_scenarios(pause: bool, assert_expectations: bool, sleep_seconds: float) -> None:
    failures: list[tuple[str, str]] = []

    for index, name in enumerate(sorted(SCENARIOS.keys()), start=1):
        print(f"\n\n########## SUITE {index}/{len(SCENARIOS)}: {name} ##########")
        try:
            run_scenario(name, pause, assert_expectations)
        except Exception as exc:
            failures.append((name, str(exc)))
            print(f"\nFAILED {name}: {exc}", file=sys.stderr)
        if sleep_seconds > 0 and index != len(SCENARIOS):
            time.sleep(sleep_seconds)

    print("\n=== SUITE SUMMARY ===")
    if not failures:
        print(f"PASS: {len(SCENARIOS)} scenarios")
        return

    print(f"FAIL: {len(failures)} of {len(SCENARIOS)} scenarios")
    for name, error in failures:
        print(f"- {name}: {error}")
    raise RuntimeError("manual flow suite failed")


def default_log_path() -> Path:
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return DEFAULT_LOG_DIR / f"manual-life-flow-{timestamp}.log"


def run_with_optional_log(log_path: str | None, run_fn) -> None:
    if not log_path:
        run_fn()
        return

    path = Path(log_path)
    if path.is_dir():
        path = path / default_log_path().name

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        with redirect_stdout(file):
            run_fn()

    print(f"Wrote manual flow transcript to: {path}")


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
    parser.add_argument("--all", action="store_true", help="Run every scenario.")
    parser.add_argument(
        "--no-assert",
        action="store_true",
        help="Print transcripts without failing on expected intents/final state.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.0,
        help="Seconds to sleep between scenarios when using --all.",
    )
    parser.add_argument(
        "--log-file",
        help="Write the full transcript to this file. If a directory is provided, a timestamped log file is created inside it.",
    )
    parser.add_argument(
        "--log-default",
        action="store_true",
        help=f"Write a timestamped log under {DEFAULT_LOG_DIR}.",
    )
    args = parser.parse_args()

    if args.list:
        print_scenario_catalog()
        return 0

    try:
        log_path = str(default_log_path()) if args.log_default else args.log_file

        def run_selected() -> None:
            if args.all:
                run_all_scenarios(args.pause, not args.no_assert, args.sleep)
            else:
                run_scenario(args.scenario, args.pause, not args.no_assert)

        run_with_optional_log(log_path, run_selected)
        return 0
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
