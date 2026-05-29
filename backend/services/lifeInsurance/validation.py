from utils.helper.BMI import calculate_BMI

ALLOWED_COVERAGE = [100_000, 250_000, 500_000, 750_000, 1_000_000]
ALLOWED_TERMS = [10, 20, 30]

RULES = {
    "age": lambda x: isinstance(x, int) and 0 < x < 120,
    "gender": lambda x: x in ["male", "female"],
    "bmi": lambda x: isinstance(x, (int, float)) and 10 < x < 60,
    "smoker": lambda x: x in ["smoker", "non_smoker"],
    "diabetes": lambda x: isinstance(x, bool),
    "high_bp": lambda x: isinstance(x, bool),
    "heart_disease": lambda x: isinstance(x, bool),
    "cancer_history": lambda x: isinstance(x, bool),
    "family_history_count": lambda x: isinstance(x, int) and x >= 0,
    "alcohol": lambda x: x in ["none", "moderate", "heavy"],
    "driving_violations": lambda x: isinstance(x, int) and x >= 0,
    "occupation": lambda x: isinstance(x, int) and 0 <= x <= 2,
    "zip_risk": lambda x: isinstance(x, int) and 1 <= x <= 10,
    "coverage_amount": lambda x: isinstance(x, int) and x in ALLOWED_COVERAGE,
    "term_length": lambda x: isinstance(x, int) and x in ALLOWED_TERMS,
}

def is_missing(value):
    return value is None or (isinstance(value, str) and not value.strip())

def validate_fields(data):
# ---- Convert height_weight → BMI then remove it ----


    height_ft = data.pop("height_ft", None)
    height_in = data.pop("height_in", None)
    weight_lbs = data.pop("weight_lbs", None)


    if  "bmi" not in data:
        if height_ft is not None and height_in is not None and weight_lbs is not None:
            try:
                bmi_value = calculate_BMI(height_ft, height_in, weight_lbs)
                if bmi_value is not None:
                    data["bmi"] = bmi_value
                    print(f"[BMI DEBUG] Calculated BMI: {bmi_value}")
            except Exception as e:
                print(f"[BMI ERROR] {e}")    
    
    
    fixed = {}

    for k, v in data.items():

        # attempt auto-fix if invalid
        if k in RULES and not RULES[k](v):
            v = auto_fix_field(k, v)

        # final check
        if k in RULES and RULES[k](v):
            fixed[k] = v

    return fixed

    

# Auto-fix function for fields
def auto_fix_field(key, value):
    try:
        if key == "age":
            return int(value)

        if key == "gender":
            val = str(value).lower()
            if "male" in val:
                return "male"
            if "female" in val:
                return "female"

        if key == "bmi":
            return float(value)

        if key == "smoker":
            if str(value).lower() in ["yes", "y", "true", "1"]:
                return "smoker"
            if str(value).lower() in ["no", "n", "false", "0"]:
                return "non_smoker"

        if key in ["diabetes", "high_bp", "heart_disease", "cancer_history"]:
            if str(value).lower() in ["yes", "y", "true", "1"]:
                return True
            if str(value).lower() in ["no", "n", "false", "0"]:
                return False

        if key == "family_history_count":
            return max(0, int(value))

        if key == "alcohol":
            val = str(value).lower()
            if "none" in val or val in ["0"]:
                return "none"
            if "moderate" in val or "1" in val:
                return "moderate"
            if "heavy" in val or "2" in val:
                return "heavy"

        if key == "occupation":
            # accept numeric or map common jobs to risk buckets
            try:
                v = int(value)
                return min(2, max(0, v))
            except:
                val = str(value).lower()
                low = ["engineer", "developer", "student", "teacher", "accountant"]
                high = ["construction", "miner", "police", "firefighter", "driver"]
                if any(w in val for w in low):
                    return 0
                if any(w in val for w in high):
                    return 2
                return 1

        if key == "zip_risk":
            # if given a zip code, convert to rough risk; otherwise clamp
            try:
                v = int(value)
                # treat 5-digit zip as input -> map to mid risk
                if v > 10000:
                    return 5
                return min(10, max(1, v))
            except:
                return 5

        if key == "driving_violations":
            return int(value)

        if key == "coverage_amount":
            if isinstance(value, str):
                val = value.lower().replace(",", "").replace("$", "")
                if "k" in val:
                    v = int(val.replace("k", "")) * 1000
                elif "m" in val:
                    v = int(float(val.replace("m", "")) * 1_000_000)
                else:
                    v = int(val)
            else:
                v = int(value)

            # snap to nearest allowed
            return min(ALLOWED_COVERAGE, key=lambda c: abs(c - v))

        if key == "term_length":
            v = int(value)
            return min(ALLOWED_TERMS, key=lambda t: abs(t - v))

    except:
        return value

    return value