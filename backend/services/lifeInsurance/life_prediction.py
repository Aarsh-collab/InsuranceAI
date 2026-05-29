from pydantic import BaseModel
from fastapi import APIRouter
from typing import Literal
from pathlib import Path
import joblib

router = APIRouter(prefix="/life_prediction", tags=["Life Prediction"])

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "life_model.pkl"
_model = None


def get_model():
    global _model

    if _model is None:
        _model = joblib.load(MODEL_PATH)

    return _model


class lifePredictionRequest(BaseModel):
    age: int
    gender: Literal["male", "female"]
    bmi: float
    smoker: Literal["smoker", "non_smoker"]
    diabetes: bool
    high_bp: bool
    heart_disease: bool
    cancer_history: bool
    family_history_count: int
    alcohol: Literal["none", "moderate", "heavy"]
    driving_violations: int
    occupation: Literal["low", "medium", "high"]
    zip_risk: int
    coverage_amount: int
    term_length: int


def life_predictions(request: lifePredictionRequest):
    model = get_model()

    smoker_map = {"non_smoker": 0, "smoker": 1}
    alcohol_map = {"none": 0, "moderate": 1, "heavy": 2}
    gender_map = {"male": 0, "female": 1}
    occupation_map = {"low": 0, "medium": 1, "high": 2}

    X = [[
        request.age,
        gender_map.get(request.gender.lower(), 1),
        smoker_map.get(request.smoker, 0),
        request.bmi,
        request.diabetes or False,
        request.high_bp,
        request.heart_disease,
        request.cancer_history,
        request.family_history_count,
        alcohol_map.get(request.alcohol.lower(), 0),
        request.driving_violations,
        occupation_map.get(request.occupation.lower(), 0),
        request.zip_risk,
        request.coverage_amount,
        request.term_length
    ]]
    predicted_premium = model.predict(X)[0]

    return predicted_premium

@router.post("/")
async def life_prediction_endpoint(request: lifePredictionRequest):
    life_quote = life_predictions(request)
    return {"predicted_premium": life_quote}
