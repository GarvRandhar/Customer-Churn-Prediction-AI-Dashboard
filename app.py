from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
import os

app = Flask(__name__, static_folder='client/build', static_url_path='')
CORS(app)

MODEL_BUNDLE_PATH = 'model_bundle.pkl'
LEGACY_MODEL_PATH = 'best_model.pkl'

FEATURE_ORDER = [
    'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure',
    'PhoneService', 'MultipleLines', 'InternetService', 'OnlineSecurity',
    'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV',
    'StreamingMovies', 'Contract', 'PaperlessBilling', 'PaymentMethod',
    'MonthlyCharges', 'TotalCharges'
]
NUMERIC_FEATURES = ['tenure', 'MonthlyCharges', 'TotalCharges']
DEFAULT_THRESHOLD = 0.5


def _load_model_artifacts():
    if os.path.exists(MODEL_BUNDLE_PATH):
        with open(MODEL_BUNDLE_PATH, 'rb') as f:
            bundle = pickle.load(f)
        return {
            'model': bundle['model'],
            'calibrator': bundle.get('calibrator'),
            'threshold': float(bundle.get('threshold', DEFAULT_THRESHOLD)),
            'feature_order': bundle.get('feature_order', FEATURE_ORDER),
            'input_feature_order': bundle.get('input_feature_order', FEATURE_ORDER),
            'model_feature_order': bundle.get('model_feature_order', bundle.get('feature_order', FEATURE_ORDER)),
        }

    # Backward compatibility fallback
    with open(LEGACY_MODEL_PATH, 'rb') as f:
        legacy_model = pickle.load(f)
    return {
        'model': legacy_model,
        'calibrator': None,
        'threshold': DEFAULT_THRESHOLD,
        'feature_order': FEATURE_ORDER,
        'input_feature_order': FEATURE_ORDER,
        'model_feature_order': FEATURE_ORDER,
    }


ARTIFACTS = _load_model_artifacts()
model = ARTIFACTS['model']
calibrator = ARTIFACTS.get('calibrator')
DECISION_THRESHOLD = ARTIFACTS['threshold']
FEATURE_ORDER = ARTIFACTS['feature_order']
INPUT_FEATURE_ORDER = ARTIFACTS.get('input_feature_order', FEATURE_ORDER)
MODEL_FEATURE_ORDER = ARTIFACTS.get('model_feature_order', FEATURE_ORDER)


def _add_engineered_features(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    if 'avg_monthly_spend' not in enriched.columns:
        enriched['avg_monthly_spend'] = enriched['TotalCharges'] / enriched['tenure'].clip(lower=1)

    if 'active_services_count' not in enriched.columns:
        service_cols = [
            'PhoneService',
            'MultipleLines',
            'OnlineSecurity',
            'OnlineBackup',
            'DeviceProtection',
            'TechSupport',
            'StreamingTV',
            'StreamingMovies',
        ]
        enriched['active_services_count'] = (
            enriched[service_cols]
            .apply(lambda col: col.astype(str).str.lower().isin(['yes']).astype(int))
            .sum(axis=1)
        )

    return enriched


def _coerce_input(data: dict):
    missing_required = [feature for feature in INPUT_FEATURE_ORDER if feature not in data]
    if missing_required:
        raise ValueError(f"Missing required fields: {', '.join(missing_required)}")

    cleaned = {feature: data.get(feature) for feature in INPUT_FEATURE_ORDER}

    for col in NUMERIC_FEATURES:
        cleaned[col] = float(cleaned[col])
    cleaned['SeniorCitizen'] = int(cleaned['SeniorCitizen'])

    return cleaned

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve the React app"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    elif os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return send_from_directory(app.static_folder, 'index.html')
    return {'message': 'React app not built yet. Run: cd client && npm run build'}, 500

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        data = request.get_json(silent=True) or {}

        cleaned = _coerce_input(data)
        input_df = pd.DataFrame([cleaned])[INPUT_FEATURE_ORDER]
        input_df = _add_engineered_features(input_df)
        input_df = input_df[MODEL_FEATURE_ORDER]

        raw_probability = model.predict_proba(input_df)[0, 1]
        if calibrator is not None:
            probability = float(calibrator.transform([raw_probability])[0])
        else:
            probability = float(raw_probability)
        prediction = int(probability >= DECISION_THRESHOLD)
        
        result = {
            'success': True,
            'prediction': 'Churn' if prediction == 1 else 'No Churn',
            'probability': float(probability),
            'confidence': float(max(probability, 1 - probability)) * 100,
            'decision_threshold': float(DECISION_THRESHOLD)
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
