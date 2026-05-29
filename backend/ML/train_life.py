import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
from sklearn.metrics import mean_absolute_error, r2_score
# Load dataset
df = pd.read_csv("life_insurance_data.csv")

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

# Train the Random Forest model
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    min_samples_split=8,
    min_samples_leaf=4,
    n_jobs=-1,
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
joblib.dump(model, "life_model.pkl")
print("Model saved as life_model.pkl")
