from utils.schema.life_schema import REQUIRED_LIFE_FIELDS
from services.lifeInsurance.life_prediction import lifePredictionRequest, life_predictions
from db.models import LifeInsurance
from typing import Optional, Dict, Any

def life_ml_helper(life_insurance_datatable: LifeInsurance) -> Optional[Dict[str, Any]]:
    required_blockers = []

    for field in REQUIRED_LIFE_FIELDS:
        value = getattr(life_insurance_datatable, field, None)
        if value is None:
            required_blockers.append(field)

    has_blockers = len(required_blockers) > 0
    life_quote = None

    if not has_blockers:
        life_request = lifePredictionRequest(
            age=life_insurance_datatable.age,
            gender=life_insurance_datatable.gender,            # "male" | "female"
            bmi=life_insurance_datatable.bmi,
            smoker=life_insurance_datatable.smoker,            # "smoker" | "non_smoker"

            diabetes=bool(life_insurance_datatable.diabetes),
            high_bp=bool(life_insurance_datatable.high_bp),
            heart_disease=bool(life_insurance_datatable.heart_disease),
            cancer_history=bool(life_insurance_datatable.cancer_history),

            family_history_count=life_insurance_datatable.family_history_count or 0,
            alcohol=life_insurance_datatable.alcohol or "none",        # literal
            driving_violations=life_insurance_datatable.driving_violations or 0,
            occupation=life_insurance_datatable.occupation or "low",  # literal
            zip_risk=life_insurance_datatable.zip_risk or 0,

            coverage_amount=life_insurance_datatable.coverage_amount,
            term_length=life_insurance_datatable.term_length
        )
        life_quote = life_predictions(life_request)

    return life_quote