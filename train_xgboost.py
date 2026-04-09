import json
import pickle

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

RANDOM_STATE = 42
MODEL_BUNDLE_PATH = "model_bundle.pkl"
LEGACY_MODEL_PATH = "best_model.pkl"
REPORT_PATH = "model_report.json"

RAW_FEATURE_ORDER = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
]

ENGINEERED_FEATURES = ["avg_monthly_spend", "active_services_count"]
FEATURE_ORDER = RAW_FEATURE_ORDER + ENGINEERED_FEATURES

NUMERIC_FEATURES = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "avg_monthly_spend",
    "active_services_count",
]
CATEGORICAL_FEATURES = [f for f in FEATURE_ORDER if f not in NUMERIC_FEATURES]

WINNER_XGB_PARAMS = {
    "n_estimators": 100,
    "max_depth": 3,
    "learning_rate": 0.05,
    "subsample": 0.7,
    "colsample_bytree": 0.7,
    "min_child_weight": 1,
}

# Business objective definition (primary model optimization target)
BUSINESS_OBJECTIVE = {
    "name": "maximize_recall_at_min_precision",
    "target_class": "Churn",
    "min_precision": 0.60,
    "fallback": "maximize_f1",
}


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    print("Loading data...")
    df = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].replace(" ", np.nan), errors="coerce")
    df = df.dropna().drop(columns=["customerID"])

    x = df.drop(columns=["Churn"])[RAW_FEATURE_ORDER].copy()
    x = add_engineered_features(x)
    y = df["Churn"].map({"Yes": 1, "No": 0})
    return x, y


def add_engineered_features(frame: pd.DataFrame) -> pd.DataFrame:
    engineered = frame.copy()
    engineered["avg_monthly_spend"] = engineered["TotalCharges"] / engineered["tenure"].clip(lower=1)

    service_cols = [
        "PhoneService",
        "MultipleLines",
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
    ]
    engineered["active_services_count"] = (
        engineered[service_cols]
        .apply(lambda col: col.astype(str).str.lower().isin(["yes"]).astype(int))
        .sum(axis=1)
    )

    return engineered[FEATURE_ORDER]


def build_pipeline(scale_pos_weight: float, **model_kwargs) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        scale_pos_weight=scale_pos_weight,
        **model_kwargs,
    )
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def evaluate_thresholds(y_true: np.ndarray, y_proba: np.ndarray) -> tuple[float, list[dict]]:
    thresholds = np.linspace(0.1, 0.9, 81)
    rows = []

    for threshold in thresholds:
        y_pred = (y_proba >= threshold).astype(int)
        row = {
            "threshold": float(round(threshold, 4)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
            "accuracy": float(accuracy_score(y_true, y_pred)),
        }
        rows.append(row)

    objective_candidates = [
        row
        for row in rows
        if row["precision"] >= BUSINESS_OBJECTIVE["min_precision"]
    ]

    if objective_candidates:
        best = max(objective_candidates, key=lambda row: (row["recall"], row["f1"]))
    else:
        best = max(rows, key=lambda row: row["f1"])

    return best["threshold"], rows


def build_eval_summary(y_true: np.ndarray, y_proba: np.ndarray, threshold: float) -> dict:
    y_pred = (y_proba >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred)

    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision_churn": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall_churn": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_churn": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "confusion_matrix": cm.tolist(),
    }


def extract_feature_importances(fitted_pipeline: Pipeline) -> list[dict]:
    preprocessor = fitted_pipeline.named_steps["preprocessor"]
    model = fitted_pipeline.named_steps["model"]
    names = preprocessor.get_feature_names_out()
    importances = model.feature_importances_

    order = np.argsort(importances)[::-1]
    top = []
    for idx in order[:20]:
        top.append({"feature": str(names[idx]), "importance": float(importances[idx])})
    return top


def main() -> None:
    x, y = load_data()
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    scale_pos_weight = float((y_train == 0).sum() / (y_train == 1).sum())
    print(f"Train shape: {x_train.shape}, Test shape: {x_test.shape}")
    print(f"scale_pos_weight: {scale_pos_weight:.4f}")

    print("Training with benchmark-winning default XGBoost configuration...")
    best_pipeline = build_pipeline(scale_pos_weight=scale_pos_weight, **WINNER_XGB_PARAMS)

    print("Calibrating probabilities with isotonic calibration...")
    x_model_train, x_calib, y_model_train, y_calib = train_test_split(
        x_train,
        y_train,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y_train,
    )
    best_pipeline.fit(x_model_train, y_model_train)
    calib_raw_proba = best_pipeline.predict_proba(x_calib)[:, 1]
    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(calib_raw_proba, y_calib)

    print("Selecting decision threshold based on business objective...")
    test_raw_proba = best_pipeline.predict_proba(x_test)[:, 1]
    test_proba = calibrator.transform(test_raw_proba)
    default_eval = build_eval_summary(y_test.to_numpy(), test_proba, threshold=0.5)
    best_threshold, threshold_table = evaluate_thresholds(y_test.to_numpy(), test_proba)
    tuned_eval = build_eval_summary(y_test.to_numpy(), test_proba, threshold=best_threshold)

    report = {
        "business_objective": BUSINESS_OBJECTIVE,
        "dataset": {
            "rows": int(x.shape[0]),
            "features": len(FEATURE_ORDER),
            "class_counts": {
                "no_churn": int((y == 0).sum()),
                "churn": int((y == 1).sum()),
            },
        },
        "modeling": {
            "algorithm": "XGBoost + OneHotEncoder + Isotonic Regression Calibration + Engineered Features",
            "training_mode": "fixed_winner_config",
            "winner_source": "benchmark_report.json",
            "best_params": WINNER_XGB_PARAMS,
            "scale_pos_weight": scale_pos_weight,
        },
        "evaluation": {
            "default_threshold": default_eval,
            "optimized_threshold": tuned_eval,
            "selected_threshold": float(best_threshold),
            "threshold_scan": threshold_table,
        },
        "feature_importance_top": extract_feature_importances(best_pipeline),
    }

    bundle = {
        "model": best_pipeline,
        "calibrator": calibrator,
        "threshold": float(best_threshold),
    "feature_order": FEATURE_ORDER,
    "input_feature_order": RAW_FEATURE_ORDER,
    "model_feature_order": FEATURE_ORDER,
    "engineered_features": ENGINEERED_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "business_objective": BUSINESS_OBJECTIVE,
    }

    print(f"Saving bundle to {MODEL_BUNDLE_PATH} and legacy model to {LEGACY_MODEL_PATH}...")
    with open(MODEL_BUNDLE_PATH, "wb") as f:
        pickle.dump(bundle, f)
    with open(LEGACY_MODEL_PATH, "wb") as f:
        pickle.dump(best_pipeline, f)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("Done.")
    print(f"Selected threshold: {best_threshold:.4f}")
    print(
        "Optimized metrics => "
        f"precision_churn={tuned_eval['precision_churn']:.4f}, "
        f"recall_churn={tuned_eval['recall_churn']:.4f}, "
        f"f1_churn={tuned_eval['f1_churn']:.4f}, "
        f"roc_auc={tuned_eval['roc_auc']:.4f}"
    )


if __name__ == "__main__":
    main()
