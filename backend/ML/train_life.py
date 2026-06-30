import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
import joblib
from sklearn.metrics import mean_absolute_error, r2_score
from pathlib import Path

ML_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ML_DIR.parent
DATA_PATH = ML_DIR / "life_insurance_data.csv"
MODEL_DIR = BACKEND_DIR / "models"
MODEL_PATH = MODEL_DIR / "life_model.pkl"

# Load dataset
df = pd.read_csv(DATA_PATH)

X = df[[
    "age",
    "gender",
    "smoker",
    "bmi",
    "diabetes",
    "high_bp",
    "heart_disease",
    "cancer_history",
    "family_history_count",
    "alcohol",
    "driving_violations",
    "occupation_risk",
    "zip_risk",
    "coverage",
    "term"
]].copy()

# Convert booleans to ints
bool_cols = ["smoker", "diabetes", "high_bp", "heart_disease", "cancer_history"]
for col in bool_cols:
    X[col] = X[col].astype(int)

# Map categorical fields
o_risk_map = {"low": 0, "medium": 1, "high": 2}
X["occupation_risk"] = X["occupation_risk"].map(o_risk_map)
X["alcohol"] = X["alcohol"].map({"none": 0, "moderate": 1, "heavy": 2})
X["gender"] = X["gender"].map({"male": 0, "female": 1})

y = df["monthly_premium"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42,
    shuffle=True
)

# Train the regression model
model = HistGradientBoostingRegressor(
    max_iter=300,
    learning_rate=0.05,
    max_leaf_nodes=31,
    l2_regularization=0.01,
    random_state=42
)

model.fit(X_train, y_train)


# Predictions for evaluation
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("MAE:", mae)
print("R² Score:", r2)
# Save the trained model
MODEL_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(model, MODEL_PATH)
print(f"Model saved as {MODEL_PATH}")
