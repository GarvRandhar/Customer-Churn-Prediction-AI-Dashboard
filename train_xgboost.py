import pandas as pd
import numpy as np
import pickle
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler

print("Loading data...")
df = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")

# Clean TotalCharges and drop ID
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].replace(' ', np.nan))
df = df.dropna()
df = df.drop(columns=['customerID'])

X = df.drop(columns=['Churn'])
y = df['Churn'].map({'Yes': 1, 'No': 0})

FEATURE_ORDER = [
    'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure',
    'PhoneService', 'MultipleLines', 'InternetService', 'OnlineSecurity',
    'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV',
    'StreamingMovies', 'Contract', 'PaperlessBilling', 'PaymentMethod',
    'MonthlyCharges', 'TotalCharges'
]
X = X[FEATURE_ORDER]

print("Creating and fitting encoders and scaler...")
encoders = {}
categorical_cols = [c for c in FEATURE_ORDER if c not in ['tenure', 'MonthlyCharges', 'TotalCharges']]

# Apply encoding by fitting new encoders
for col in categorical_cols:
    if col in X.columns:
        encoders[col] = LabelEncoder()
        X[col] = encoders[col].fit_transform(X[col])

# Apply scaling by fitting new scaler
numerical_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
scaler = StandardScaler()
X[numerical_cols] = scaler.fit_transform(X[numerical_cols])

print("Saving encoders and scaler to disk...")
with open("encoder.pkl", "wb") as f:
    pickle.dump(encoders, f)
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

# Note: We use random_state=42 exactly as typically used to ensure same splits
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Calculate scale_pos_weight for XGBoost (num_negative / num_positive)
scale_pos_weight = sum(y_train == 0) / sum(y_train == 1)

print("Training XGBoost Classifier natively handling class balance...")
# We tune slightly for tabular churn data
model = XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    eval_metric='logloss'
)
model.fit(X_train, y_train)

print("Evaluating XGBoost model...")
y_pred = model.predict(X_test)
print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
print("Classification Report:")
print(classification_report(y_test, y_pred))

print("Saving model to best_model.pkl...")
with open("best_model.pkl", "wb") as f:
    pickle.dump(model, f)
print("Done! XGBoost is now the baseline.")
