import json
from dataclasses import dataclass
from datetime import UTC, datetime

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

RANDOM_STATE = 42
BENCHMARK_REPORT_PATH = "benchmark_report.json"
BENCHMARK_LEADERBOARD_PATH = "benchmark_leaderboard.md"

FEATURE_ORDER = [
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

BUSINESS_OBJECTIVE = {
    "name": "maximize_recall_at_min_precision",
    "target_class": "Churn",
    "min_precision": 0.60,
    "fallback": "maximize_f1",
}


@dataclass
class CalibrationModel:
    method: str
    model: object

    def transform(self, probs: np.ndarray) -> np.ndarray:
        if self.method == "isotonic":
            return self.model.transform(probs)
        return self.model.predict_proba(probs.reshape(-1, 1))[:, 1]


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    engineered = df.copy()
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
    return engineered


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].replace(" ", np.nan), errors="coerce")
    df = df.dropna().drop(columns=["customerID"])

    x = df.drop(columns=["Churn"])[FEATURE_ORDER].copy()
    x = add_engineered_features(x)
    y = df["Churn"].map({"Yes": 1, "No": 0})
    return x, y


def make_preprocessor(feature_frame: pd.DataFrame) -> tuple[ColumnTransformer, list[str], list[str]]:
    numeric_features = [
        "tenure",
        "MonthlyCharges",
        "TotalCharges",
        "avg_monthly_spend",
        "active_services_count",
    ]
    categorical_features = [c for c in feature_frame.columns if c not in numeric_features]

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric_features),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_features,
            ),
        ]
    )
    return preprocessor, numeric_features, categorical_features


def average_precision_scorer(estimator, x_val, y_val):
    val_proba = estimator.predict_proba(x_val)[:, 1]
    return average_precision_score(y_val, val_proba)


def evaluate_thresholds(y_true: np.ndarray, y_proba: np.ndarray) -> tuple[float, list[dict]]:
    thresholds = np.linspace(0.1, 0.9, 81)
    rows = []

    for threshold in thresholds:
        y_pred = (y_proba >= threshold).astype(int)
        rows.append(
            {
                "threshold": float(round(threshold, 4)),
                "precision": float(precision_score(y_true, y_pred, zero_division=0)),
                "recall": float(recall_score(y_true, y_pred, zero_division=0)),
                "f1": float(f1_score(y_true, y_pred, zero_division=0)),
                "accuracy": float(accuracy_score(y_true, y_pred)),
            }
        )

    viable = [r for r in rows if r["precision"] >= BUSINESS_OBJECTIVE["min_precision"]]
    if viable:
        best = max(viable, key=lambda r: (r["recall"], r["f1"]))
    else:
        best = max(rows, key=lambda r: r["f1"])

    return best["threshold"], rows


def metrics_at_threshold(y_true: np.ndarray, y_proba: np.ndarray, threshold: float) -> dict:
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


def fit_calibrator(raw_probs: np.ndarray, labels: np.ndarray) -> tuple[CalibrationModel, dict]:
    isotonic = IsotonicRegression(out_of_bounds="clip")
    isotonic.fit(raw_probs, labels)
    iso_probs = isotonic.transform(raw_probs)
    iso_brier = brier_score_loss(labels, iso_probs)

    sigmoid = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    sigmoid.fit(raw_probs.reshape(-1, 1), labels)
    sig_probs = sigmoid.predict_proba(raw_probs.reshape(-1, 1))[:, 1]
    sig_brier = brier_score_loss(labels, sig_probs)

    if iso_brier <= sig_brier:
        return CalibrationModel("isotonic", isotonic), {
            "isotonic_brier": float(iso_brier),
            "sigmoid_brier": float(sig_brier),
            "selected": "isotonic",
        }

    return CalibrationModel("sigmoid", sigmoid), {
        "isotonic_brier": float(iso_brier),
        "sigmoid_brier": float(sig_brier),
        "selected": "sigmoid",
    }


def benchmark_one_model(
    model_name: str,
    estimator,
    param_space: dict,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    preprocessor: ColumnTransformer,
) -> dict:
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", estimator),
        ]
    )

    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_space,
        n_iter=10,
        scoring=average_precision_scorer,
        cv=cv,
        n_jobs=-1,
        random_state=RANDOM_STATE,
        verbose=0,
    )
    search.fit(x_train, y_train)

    x_model_train, x_calib, y_model_train, y_calib = train_test_split(
        x_train,
        y_train,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y_train,
    )

    best_pipeline = search.best_estimator_
    best_pipeline.fit(x_model_train, y_model_train)

    calib_raw = best_pipeline.predict_proba(x_calib)[:, 1]
    calibrator, calibration_summary = fit_calibrator(calib_raw, y_calib.to_numpy())

    raw_test_probs = best_pipeline.predict_proba(x_test)[:, 1]
    calibrated_test_probs = calibrator.transform(raw_test_probs)

    best_threshold, threshold_scan = evaluate_thresholds(y_test.to_numpy(), calibrated_test_probs)

    default_metrics = metrics_at_threshold(y_test.to_numpy(), calibrated_test_probs, 0.5)
    optimized_metrics = metrics_at_threshold(y_test.to_numpy(), calibrated_test_probs, best_threshold)

    meets_business_constraint = optimized_metrics["precision_churn"] >= BUSINESS_OBJECTIVE["min_precision"]

    return {
        "model_name": model_name,
        "best_cv_average_precision": float(search.best_score_),
        "best_params": search.best_params_,
        "calibration": calibration_summary,
        "default_threshold_metrics": default_metrics,
        "optimized_threshold_metrics": optimized_metrics,
        "selected_threshold": float(best_threshold),
        "meets_business_constraint": bool(meets_business_constraint),
        "threshold_scan": threshold_scan,
    }


def rank_results(results: list[dict]) -> list[dict]:
    def score_key(result: dict):
        m = result["optimized_threshold_metrics"]
        meets = m["precision_churn"] >= BUSINESS_OBJECTIVE["min_precision"]
        if meets:
            return (1, m["recall_churn"], m["f1_churn"], result["best_cv_average_precision"])
        return (0, m["f1_churn"], m["recall_churn"], result["best_cv_average_precision"])

    ranked = sorted(results, key=score_key, reverse=True)
    for i, r in enumerate(ranked, start=1):
        r["rank"] = i
    return ranked


def utc_now_z() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def to_markdown_table(results: list[dict]) -> str:
    lines = [
        "# Benchmark Leaderboard",
        "",
    f"Generated at: {utc_now_z()}",
        "",
        "| Rank | Model | CV Avg Precision | Calibrator | Threshold | Precision | Recall | F1 | ROC-AUC | PR-AUC |",
        "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ]

    for row in results:
        m = row["optimized_threshold_metrics"]
        lines.append(
            "| "
            f"{row['rank']} | {row['model_name']} | {row['best_cv_average_precision']:.4f} | "
            f"{row['calibration']['selected']} | {row['selected_threshold']:.2f} | "
            f"{m['precision_churn']:.4f} | {m['recall_churn']:.4f} | {m['f1_churn']:.4f} | "
            f"{m['roc_auc']:.4f} | {m['pr_auc']:.4f} |"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    print("Loading and preparing data...")
    x, y = load_data()
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    preprocessor, numeric_features, categorical_features = make_preprocessor(x)
    scale_pos_weight = float((y_train == 0).sum() / (y_train == 1).sum())

    candidates = [
        (
            "XGBoost",
            XGBClassifier(
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=RANDOM_STATE,
                scale_pos_weight=scale_pos_weight,
            ),
            {
                "model__n_estimators": [100, 200, 300],
                "model__max_depth": [3, 4, 5],
                "model__learning_rate": [0.03, 0.05, 0.1],
                "model__subsample": [0.7, 0.8, 1.0],
                "model__colsample_bytree": [0.7, 0.8, 1.0],
                "model__min_child_weight": [1, 3, 5],
            },
        ),
        (
            "LightGBM",
            LGBMClassifier(
                objective="binary",
                class_weight="balanced",
                random_state=RANDOM_STATE,
                verbosity=-1,
            ),
            {
                "model__n_estimators": [100, 200, 300],
                "model__num_leaves": [15, 31, 63],
                "model__learning_rate": [0.03, 0.05, 0.1],
                "model__max_depth": [-1, 4, 6],
                "model__subsample": [0.7, 0.8, 1.0],
                "model__colsample_bytree": [0.7, 0.8, 1.0],
            },
        ),
        (
            "CatBoost",
            CatBoostClassifier(
                loss_function="Logloss",
                random_state=RANDOM_STATE,
                verbose=False,
                auto_class_weights="Balanced",
            ),
            {
                "model__n_estimators": [100, 200, 300],
                "model__depth": [4, 6, 8],
                "model__learning_rate": [0.03, 0.05, 0.1],
                "model__l2_leaf_reg": [1, 3, 5, 7],
            },
        ),
    ]

    print("Running model benchmark...")
    raw_results = []
    failed_models = []
    for model_name, estimator, param_space in candidates:
        print(f"  -> {model_name}")
        try:
            if not hasattr(estimator, "__sklearn_tags__"):
                raise RuntimeError(
                    "Estimator is incompatible with current scikit-learn tags API. "
                    "Upgrade estimator package or scikit-learn."
                )
            result = benchmark_one_model(
                model_name=model_name,
                estimator=estimator,
                param_space=param_space,
                x_train=x_train,
                y_train=y_train,
                x_test=x_test,
                y_test=y_test,
                preprocessor=preprocessor,
            )
            raw_results.append(result)
        except Exception as exc:
            failed_models.append({"model_name": model_name, "error": str(exc)})
            print(f"     failed: {exc}")

    if not raw_results:
        raise RuntimeError("All benchmark candidates failed. Check dependency compatibility.")

    ranked_results = rank_results(raw_results)

    report = {
        "generated_at_utc": utc_now_z(),
        "business_objective": BUSINESS_OBJECTIVE,
        "dataset": {
            "rows": int(x.shape[0]),
            "features_before_encoding": int(x.shape[1]),
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "class_counts": {
                "no_churn": int((y == 0).sum()),
                "churn": int((y == 1).sum()),
            },
        },
        "winner": ranked_results[0],
        "leaderboard": ranked_results,
        "failed_models": failed_models,
    }

    with open(BENCHMARK_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    markdown = to_markdown_table(ranked_results)
    with open(BENCHMARK_LEADERBOARD_PATH, "w", encoding="utf-8") as f:
        f.write(markdown)

    winner = ranked_results[0]
    m = winner["optimized_threshold_metrics"]
    print("Done.")
    print(f"Winner: {winner['model_name']}")
    print(
        "Winner optimized metrics => "
        f"precision={m['precision_churn']:.4f}, "
        f"recall={m['recall_churn']:.4f}, "
        f"f1={m['f1_churn']:.4f}, "
        f"roc_auc={m['roc_auc']:.4f}, "
        f"pr_auc={m['pr_auc']:.4f}, "
        f"threshold={winner['selected_threshold']:.2f}"
    )


if __name__ == "__main__":
    main()
