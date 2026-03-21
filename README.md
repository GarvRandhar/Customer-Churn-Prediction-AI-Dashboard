
# Customer Churn Prediction — AI Dashboard

A full-screen, dark-themed AI dashboard for predicting customer churn using a trained XGBoost model. Built with Flask + React.

![Churn Prediction Dashboard](https://img.shields.io/badge/ML-XGBoost-6366F1?style=flat-square) ![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square) ![Flask](https://img.shields.io/badge/Backend-Flask-000000?style=flat-square)

## Features

- 🎯 **AI-powered churn prediction** with probability score and confidence
- 🌑 **Dark professional UI** — full-screen dashboard, not a windowed form
- 📊 **Animated SVG gauge** for visualizing churn probability
- 🧙 **Multi-step wizard** — form split into 5 logical steps with progress tracking
- ⚡ **Real-time feedback** — step validation, completion indicators, loading overlay
- 📱 **Responsive** — works on desktop and mobile

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask, scikit-learn, pandas, numpy |
| Frontend | React 18, Tailwind CSS 3, Lucide Icons |
| ML Model | XGBoost Classifier (SMOTE-balanced) |

## Quick Start

### 1. Clone & install

```bash
git clone <your-repo-url>
cd Churn-Prediction

# Python
pip install -r requirements.txt

# React
cd client && npm install && cd ..
```

### 2. Run (development)

**Terminal 1** — Flask backend:
```bash
python app.py
```

**Terminal 2** — React dev server:
```bash
cd client && npm start
```

Open `http://localhost:3000` (dev) or build for production:

```bash
cd client && npm run build
# Then visit http://localhost:5001
```

## Project Structure

```
├── app.py                  # Flask API server
├── requirements.txt        # Python dependencies
├── best_model.pkl          # Trained XGBoost model
├── encoder.pkl             # Label encoders
├── scaler.pkl              # Feature scaler
├── run.sh                  # Startup script
├── Untitled.ipynb          # Model training notebook
├── WA_Fn-UseC_-Telco-Customer-Churn.csv
└── client/                 # React frontend
    ├── src/
    │   ├── App.js
    │   ├── index.js
    │   ├── index.css
    │   └── components/
    │       ├── PredictionForm.js    # 5-step wizard form
    │       └── ResultDisplay.js     # Gauge + results
    ├── public/index.html
    ├── tailwind.config.js
    └── package.json
```

## How to Use

1. Fill in customer details across **5 steps**: Demographics → Services → Online Features → Contract & Billing → Financials
2. Click **Predict Churn** on the final step
3. View the result: animated gauge, risk verdict, confidence score, and actionable recommendations
4. Click **New Prediction** to analyze another customer

## API

### `POST /predict`

```json
// Request
{
  "gender": "Female", "SeniorCitizen": 0, "Partner": "Yes", "Dependents": "No",
  "tenure": 24, "PhoneService": "Yes", "MultipleLines": "No",
  "InternetService": "Fiber optic", "OnlineSecurity": "Yes", "OnlineBackup": "No",
  "DeviceProtection": "No", "TechSupport": "No", "StreamingTV": "Yes",
  "StreamingMovies": "No", "Contract": "Month-to-month",
  "PaperlessBilling": "Yes", "PaymentMethod": "Electronic check",
  "MonthlyCharges": 70.35, "TotalCharges": 1689.50
}

// Response
{
  "success": true,
  "prediction": "Churn",
  "probability": 0.75,
  "confidence": 75.0
}
```

### `GET /health`
Health check — returns `{"status": "healthy"}`

## Production Deployment

```bash
pip install gunicorn
cd client && npm run build && cd ..
gunicorn app:app --workers 4 --bind 0.0.0.0:5000
```

## License

This project uses the [Telco Customer Churn dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn).

