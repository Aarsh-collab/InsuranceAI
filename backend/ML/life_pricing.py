import math

# ----------------------------------------
# Company loadings (profit, admin, overhead)
# ----------------------------------------

def apply_loadings(base_cost: float, load_factor: float = 1.15) -> float:
    """Apply company loading to the pure risk cost.

    Typical insurers load 10%–20%; we use 15% (1.15x) as a realistic mid‑range.
    """
    return base_cost * load_factor


# ----------------------------------------
# Gompertz–Makeham baseline hazard for age
# ----------------------------------------

A = 0.0005   # age‑independent risk (accidents, etc.)
B = 0.000015 # baseline biological aging
C = 0.085    # aging acceleration rate


def base_hazard(age: int) -> float:
    """Baseline yearly mortality hazard by age using Gompertz–Makeham.

    h(age) = A + B * exp(C * age)
    Returns a yearly probability (approximate) of death.
    """
    return A + B * math.exp(C * age)


# ----------------------------------------
# Profile-based risk multiplier
# ----------------------------------------


def _as_bool(value) -> bool:
    """Robust boolean parser for fields that can be bool/int/str.

    Treats 1/"yes"/"true"/"smoker"/"current_smoker" as True.
    Everything else is False.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value == 1
    if isinstance(value, str):
        v = value.strip().lower()
        return v in {"yes", "true", "y", "smoker", "current_smoker"}
    return False


def compute_risk_multiplier(profile: dict) -> float:
    """Compute an additive risk multiplier from profile fields.

    Expects (when available):
      - age
      - bmi
      - smoker
      - diabetes
      - high_bp or high_Bp
      - heart_disease
      - cancer_history
      - family_history_count
      - occupation_risk (0–2)
      - zip_risk (0–2)
      - driving_violations (0+)

    All contributions are ADDITIVE on top of 1.0, not multiplicative
    against each other. This avoids insane compounding for seniors.
    """

    bmi = profile.get("bmi")

    smoker = _as_bool(profile.get("smoker"))
    diabetes = _as_bool(profile.get("diabetes"))
    # Handle both "high_bp" and old "high_Bp" key just in case
    high_bp = _as_bool(profile.get("high_bp") or profile.get("high_Bp"))
    heart_disease = _as_bool(profile.get("heart_disease"))
    cancer_history = _as_bool(profile.get("cancer_history"))

    family_history = profile.get("family_history_count", 0) or 0
    try:
        family_history = int(family_history)
    except (TypeError, ValueError):
        family_history = 0

    occupation_risk = profile.get("occupation_risk", 0) or 0
    zip_risk = profile.get("zip_risk", 0) or 0
    driving_violations = profile.get("driving_violations", 0) or 0

    try:
        occupation_risk = int(occupation_risk)
    except (TypeError, ValueError):
        occupation_risk = 0

    try:
        zip_risk = int(zip_risk)
    except (TypeError, ValueError):
        zip_risk = 0

    try:
        driving_violations = int(driving_violations)
    except (TypeError, ValueError):
        driving_violations = 0

    # Start at 1.0 = baseline
    risk = 1.0

    # Smoking: lower penalty
    if smoker:
        risk += 0.30  # +30%

    # Medical conditions (scaled down)
    if diabetes:
        risk += 0.05  # +5%
    if high_bp:
        risk += 0.04  # +4%
    if heart_disease:
        risk += 0.10  # +10%
    if cancer_history:
        risk += 0.08  # +8%

    # Family history: softer
    risk += family_history * 0.01  # +1% per affected relative

    # BMI contribution (scaled down)
    if bmi is not None:
        try:
            bmi_val = float(bmi)
            if bmi_val < 18.5:
                risk += 0.02
            elif bmi_val < 25:
                pass
            elif bmi_val < 30:
                risk += 0.03
            elif bmi_val < 35:
                risk += 0.07
            elif bmi_val < 40:
                risk += 0.12
            else:
                risk += 0.20
        except (TypeError, ValueError):
            pass

    # Non-medical risk (scaled down)
    risk += occupation_risk * 0.01
    risk += zip_risk * 0.005
    risk += driving_violations * 0.01

    return risk


# ----------------------------------------
# Final pricing function
# ----------------------------------------


def price_life_policy(profile: dict, coverage_amount: int, term_years: int) -> float:
    """Price a term life policy using a hazard model.

    Args:
        profile: dict with risk features (age, bmi, smoker, etc.)
        coverage_amount: face amount in dollars (e.g., 250000, 500000, 1000000)
        term_years: policy term (10, 20, 30)

    Returns:
        Monthly premium in dollars (float, rounded to 2 decimals).
    """

    age = profile.get("age")
    if age is None:
        raise ValueError("Profile missing age")

    try:
        age = int(age)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid age value: {age}")

    # 1) Baseline hazard from age
    hazard = base_hazard(age)

    # 2) Profile‑based risk multiplier
    risk_mult = compute_risk_multiplier(profile)
    hazard *= risk_mult

    # 3) Cap hazard at 15% annual mortality for term products
    hazard = min(hazard, 0.15)

    # 4) Term factor (longer term slightly more expensive)
    if term_years <= 10:
        term_factor = 1.0
    elif term_years <= 20:
        term_factor = 1.2
    else:  # 30‑year term
        term_factor = 1.5

    # 5) Pure risk cost: hazard * coverage * term load
    annual_cost = hazard * float(coverage_amount) * term_factor

    # 6) Company loading
    loaded_cost = apply_loadings(annual_cost)

    # 7) Annual → monthly + clamping to realistic market range
    monthly_premium = loaded_cost / 12.0
    monthly_premium = max(15.0, min(monthly_premium, 2500.0))

    return round(monthly_premium, 2)
