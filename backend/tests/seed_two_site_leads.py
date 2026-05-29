import json
import os
import sys
from typing import Any

import requests


API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
OWNER_TOKEN = os.environ.get("ADMIN_TOKEN", "test-admin-token")
SITE_TOKEN = os.environ.get("SITE_ADMIN", "friend-dad-test-token")


FLOW_MESSAGES = [
    "I want life insurance.",
    "I'm 30 and male.",
    "I'm 5 foot 10 and 180 pounds.",
    "I do not smoke.",
    "I want 500k coverage for a 20 year term.",
    "No diabetes, no high blood pressure, no heart disease, no cancer history.",
    "No family history, I don't drink, no driving violations, I work an office job, zip risk is 5.",
    "Can I talk to a broker?",
]


def request_json(method: str, path: str, **kwargs) -> dict[str, Any] | list[Any]:
    response = requests.request(method, f"{API_BASE_URL}{path}", timeout=90, **kwargs)
    try:
        payload = response.json()
    except Exception:
        payload = {"raw": response.text}

    if not response.ok:
        raise RuntimeError(f"{method} {path} failed: {response.status_code} {payload}")

    return payload


def create_session(site_id: str) -> tuple[str, str]:
    account = request_json("POST", "/accounts", json={"site_id": site_id})
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


def seed_lead(site_id: str, name: str, email: str, phone: str, time: str) -> dict[str, str]:
    account_id, session_id = create_session(site_id)
    print(f"\n=== SEED {site_id} ===")
    print(f"ACCOUNT: {account_id}")
    print(f"SESSION: {session_id}")

    for index, message in enumerate(FLOW_MESSAGES, start=1):
        data = send_chat(session_id, message)
        intent = data.get("intent") or {}
        print(f"{index:02d}. {intent.get('intent')}: {message}")

    final_message = f"My name is {name}, my email is {email}, phone is {phone}, {time} works."
    data = send_chat(session_id, final_message)
    print(f"09. {(data.get('intent') or {}).get('intent')}: {final_message}")
    print(f"BOT: {data.get('reply')}")

    return {"site_id": site_id, "account_id": account_id, "session_id": session_id}


def fetch_leads(token: str) -> list[dict[str, Any]]:
    payload = request_json(
        "GET",
        "/admin/leads",
        headers={"Authorization": f"Bearer {token}"},
    )
    if not isinstance(payload, list):
        raise RuntimeError(f"Expected /admin/leads list, got: {json.dumps(payload, default=str)}")
    return payload


def assert_visible(leads: list[dict[str, Any]], session_id: str, should_exist: bool, label: str) -> None:
    exists = any(lead.get("session_id") == session_id for lead in leads)
    if exists != should_exist:
        expectation = "include" if should_exist else "exclude"
        raise AssertionError(f"{label} should {expectation} session {session_id}")


def main() -> int:
    try:
        demo = seed_lead(
            "demo",
            "Demo Lead",
            "demo-lead@example.com",
            "5551112222",
            "tomorrow afternoon",
        )
        friend = seed_lead(
            "friend_dad_site",
            "Friend Dad Lead",
            "friend-dad-lead@example.com",
            "5553334444",
            "Friday morning",
        )

        owner_leads = fetch_leads(OWNER_TOKEN)
        site_leads = fetch_leads(SITE_TOKEN)

        assert_visible(owner_leads, demo["session_id"], True, "owner token")
        assert_visible(owner_leads, friend["session_id"], True, "owner token")
        assert_visible(site_leads, demo["session_id"], False, "site token")
        assert_visible(site_leads, friend["session_id"], True, "site token")

        print("\n=== ADMIN VISIBILITY CHECK ===")
        print(f"OWNER TOKEN LEADS: {len(owner_leads)}")
        print(f"SITE TOKEN LEADS: {len(site_leads)}")
        print("PASS: owner sees both seeded leads")
        print("PASS: friend_dad_site admin sees only friend_dad_site lead")
        return 0
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
