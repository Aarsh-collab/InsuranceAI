import re
import requests
import random

ACCOUNT_URL = "http://localhost:8000/accounts"
CHAT_ROUTER = "http://localhost:8000/chat/router"


# --- Create account + session ---
def create_session():
    account_id = requests.post(ACCOUNT_URL).json()["account_id"]

    session_id = requests.post(
        f"{ACCOUNT_URL}/{account_id}/sessions",
        json={"insurance_type": "life"}
    ).json()["session_id"]

    return account_id, session_id


# --- USER TYPES ---


def has_word(text: str, pattern: str) -> bool:
    return re.search(rf"\b{pattern}\b", text) is not None

def clean_user(bot_question):
    q = bot_question.lower()

    answers = []

    # age
    if "how old" in q or has_word(q, "age"):
        answers.append("19")

    # gender
    if has_word(q, "gender") or "male or female" in q:
        answers.append("male")

    # body metrics + smoking (logical pairing)
    if any(x in q for x in ["bmi", "height", "weight"]):
        answers.append("22.2")
        if any(x in q for x in ["smoke", "non-smoker", "tobacco"]):
            answers.append("no")
        return " ".join(answers)

    # health batch (grouped logically)
    if any(x in q for x in ["diabetes", "blood pressure", "heart", "cancer"]):
        answers.append("no")

    # family history
    if has_word(q, "family"):
        answers.append("1")

    # alcohol
    if has_word(q, "alcohol") or has_word(q, "drink") or "drinking" in q:
        answers.append("moderate")

    # violations
    if has_word(q, "violation") or has_word(q, "violations") or has_word(q, "ticket"):
        answers.append("0")

    # occupation
    if has_word(q, "occupation") or has_word(q, "job"):
        answers.append("0")

    # zip
    if has_word(q, "zip"):
        answers.append("5")

    # coverage + term (paired logically)
    if has_word(q, "coverage") and has_word(q, "term"):
        return "500000 20"

    if has_word(q, "coverage"):
        answers.append("500000")

    if has_word(q, "term") or has_word(q, "years"):
        answers.append("20")

    if answers:
        return " ".join(answers)

    return "no"


def messy_user(bot_question):
    q = bot_question.lower()

    # realistic messy but extractable responses
    patterns = [
        ("age", ["i'm like 19 i think", "around 20", "uh 19"]),
        ("gender", ["male i guess", "probably male", "im a guy"]),
        ("bmi", ["idk bmi but i'm 5'9 180", "not sure maybe normal", "uh 22ish"]),
        ("smoker", ["nah i don't smoke", "nope", "used to but not anymore"]),
        ("coverage", ["like 500k i think", "maybe half a mil", "idk 300k?"]),
        ("term", ["maybe 20 years", "not sure like long term", "uh 10 or 20"]),
        ("health", ["i'm healthy", "nothing serious", "nah all good"]),
        ("family", ["maybe 1 person", "idk like one", "not many"]),
        ("alcohol", ["sometimes", "socially", "not much"]),
        ("violations", ["none", "0", "maybe one a while ago"]),
        ("occupation", ["tech job", "engineer", "office job"]),
        ("zip", ["85281", "near phoenix", "tempe area"])
    ]

    for key, responses in patterns:
        if key in q:
            return random.choice(responses)

    # fallback: semi-coherent noise
    return random.choice([
        "uhhh not sure",
        "idk honestly",
        "whatever is normal",
        "you can decide",
        "not really sure"
    ])


def refusal_user(bot_question):
    q = bot_question.lower()
    if "how old" in q or has_word(q, "age"):
        return "i don't want to share that"

    if random.random() < 0.5:
        return "prefer not to say"

    return clean_user(bot_question)


def correction_user(bot_question):
    q = bot_question.lower()
    if "how old" in q or has_word(q, "age"):
        return random.choice(["19", "actually 20"])

    if "smoke" in q:
        return random.choice(["no", "wait actually yes"])

    return clean_user(bot_question)


USER_TYPES = {
    "clean": clean_user,
    "messy": messy_user,
    "refusal": refusal_user,
    "correction": correction_user
}


# --- RUN TEST ---
def run_test(user_type_name):
    user_fn = USER_TYPES[user_type_name]

    account_id, session_id = create_session()

    print("\n============================")
    print(f"USER TYPE: {user_type_name.upper()}")
    print("ACCOUNT:", account_id)
    print("SESSION:", session_id)
    print("============================\n")

    msg = "Hey, I want life insurance"

    for step in range(30):
        response = requests.post(
            CHAT_ROUTER,
            params={"session_id": session_id},
            json={"message": msg}
        )

        data = response.json()

        bot_reply = data.get("response") or data.get("reply")
        missing = data.get("state", {}).get("application", {}).get("missing_fields")
        quote = data.get("state", {}).get("application", {}).get("ml_quote")

        print("USER:", msg)
        print("BOT :", bot_reply)
        print("MISSING:", missing)
        print("QUOTE:", quote)
        print("------------------------")

        if not bot_reply:
            print("ERROR RESPONSE:", data)
            break

        if data.get("intake_complete"):
            print("\n✅ INTAKE COMPLETE\n")
            break

        msg = user_fn(bot_reply)


# --- RUN ALL SCENARIOS ---
if __name__ == "__main__":
    for user_type in USER_TYPES.keys():
        run_test(user_type)