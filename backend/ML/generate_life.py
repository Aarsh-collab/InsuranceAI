import random
import pandas as pd
from life_pricing import price_life_policy

def random_profile():
    age = random.randint(20, 75)
    # Risk tier sampling for balanced RF learning
    risk_tier = random.choices(

        ["healthy", "moderate", "risky"],
        weights=[0.65, 0.25, 0.10],
        k=1
    )[0]
    gender = random.choice(["male", "female"])

    # Generate BMI directly (RF‑friendly, realistic distribution)
    bmi = random.choices(
        population=[
            random.uniform(18, 20),   # underweight
            random.uniform(25, 30),   # overweight
            random.uniform(30, 35),   # obese I
            random.uniform(35, 40),   # obese II
            random.uniform(40, 42)    # extreme
        ],
        weights=[5, 40, 30, 15, 10],
        k=1
    )[0]

    # --- CORRELATED RISK ADJUSTMENTS ---

    # Higher BMI increases diabetes and BP probability
    bmi_risk = 0
    if bmi >= 35:
        bmi_risk = 0.10
    elif bmi >= 30:
        bmi_risk = 0.05

    # Very low BMI slightly increases cancer/heart odds
    if bmi < 20:
        bmi_risk -= 0.02

    # Smoking probability based on age + risk tier
    if risk_tier == "healthy":
        smoker = random.random() < (0.04 if age < 50 else 0.06)
    elif risk_tier == "moderate":
        smoker = random.random() < (0.10 if age < 50 else 0.14)
    else:  # risky
        smoker = random.random() < (0.20 if age < 50 else 0.28)

    # Diabetes probability from age + BMI + risk tier
    base_diab_rate = (
        0.02 if age < 35 else
        0.08 if age < 50 else
        0.18
    )
    if risk_tier == "moderate":
        base_diab_rate += 0.04
    elif risk_tier == "risky":
        base_diab_rate += 0.08

    diabetes = random.random() < (base_diab_rate + bmi_risk)

    base_bp_rate = (
        0.04 if age < 35 else
        0.10 if age < 50 else
        0.22
    )
    if risk_tier == "moderate":
        base_bp_rate += 0.03
    elif risk_tier == "risky":
        base_bp_rate += 0.06

    high_bp = random.random() < (base_bp_rate + bmi_risk * 0.5)

    base_hd_rate = (
        0.015 if age < 40 else
        0.08 if age < 60 else
        0.16
    )
    if risk_tier == "moderate":
        base_hd_rate += 0.04
    elif risk_tier == "risky":
        base_hd_rate += 0.08

    heart_boost = 0.05 if diabetes else 0.0
    heart_boost += 0.04 if high_bp else 0.0
    heart_disease = random.random() < (base_hd_rate + heart_boost)

    base_cancer_rate = (
        0.012 if age < 40 else
        0.045 if age < 60 else
        0.09
    )
    if risk_tier == "moderate":
        base_cancer_rate += 0.02
    elif risk_tier == "risky":
        base_cancer_rate += 0.04

    family_history_count = random.choice([0, 0, 1, 1, 2])
    cancer_boost = 0.03 if smoker else 0.0
    cancer_boost += 0.04 if family_history_count >= 2 else 0.0
    cancer_history = random.random() < (base_cancer_rate + cancer_boost)

    # Alcohol linked to risk tier + smoking
    if risk_tier == "healthy":
        alcohol = random.choices([0, 1, 2], weights=[0.65, 0.30, 0.05])[0]
    elif risk_tier == "moderate":
        alcohol = random.choices([0, 1, 2], weights=[0.45, 0.40, 0.15])[0]
    else:
        alcohol = random.choices([0, 1, 2], weights=[0.30, 0.40, 0.30])[0]

    # Driving violations
    driving_violations = random.choices([0, 1, 2], weights=[0.75, 0.18, 0.07])[0]

    # Occupation risk correlated with tier
    if risk_tier == "healthy":
        occ_weights = [0.70, 0.22, 0.08]
    elif risk_tier == "moderate":
        occ_weights = [0.55, 0.30, 0.15]
    else:
        occ_weights = [0.45, 0.35, 0.20]

    occupation_risk = random.choices(
        [0, 1, 2],
        weights=occ_weights,
        k=1
    )[0]

    # ZIP risk skewed low with occasional high pockets
    zip_risk = random.choices(
        population=[0,1,2,3,4,5,6,7,8,9,10],
        weights=[20,15,13,10,8,7,5,4,3,2,1],
        k=1
    )[0]

    return {
        "age": age,
        "gender": gender,
        "bmi": bmi,
        "smoker": smoker,
        "diabetes": diabetes,
        "high_bp": high_bp,
        "heart_disease": heart_disease,
        "cancer_history": cancer_history,
        "family_history_count": family_history_count,
        "alcohol": alcohol,
        "driving_violations": driving_violations,
        "occupation_risk": occupation_risk,
        "zip_risk": zip_risk,
    }

def generate_dataset(n=5000):
    rows = []
    for _ in range(n):
        profile = random_profile()
        coverage = random.choice([100000, 250000, 500000, 750000, 1000000])

        # Age‑based term realism
        if profile["age"] <= 45:
            term = random.choice([10, 20, 30])
        elif profile["age"] <= 55:
            term = random.choice([10, 20])
        elif profile["age"] <= 65:
            term = 10
        else:
            term = 10 

        premium = price_life_policy(profile, coverage, term)

        row = {
            **profile,
            "coverage": coverage,
            "term": term,
            "monthly_premium": premium,
        }
        rows.append(row)

    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = generate_dataset(1_000_000)
    df.to_csv("life_insurance_data.csv", index=False)
    print("Generated life_insurance_data.csv")