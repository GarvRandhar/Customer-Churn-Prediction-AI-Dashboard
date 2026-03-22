# 🔮 Customer Churn Prediction — AI Dashboard

> A full-screen, dark-themed AI dashboard for predicting customer churn using a trained XGBoost model. Built with Flask + React.

![Churn Prediction Dashboard](https://img.shields.io/badge/ML-XGBoost-6366F1?style=for-the-badge&logo=scikit-learn&logoColor=white) 
![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=for-the-badge&logo=react&logoColor=black) 
![Flask](https://img.shields.io/badge/Backend-Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Style-Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

---

## ✨ Features

- 🎯 **AI-Powered Churn Prediction:** Get accurate probability scores and confidence metrics.
- 🌑 **Dark Professional UI:** A sleek, full-screen dashboard experience (no windowed forms).
- 📊 **Animated SVG Gauge:** Visually stunning representation of churn probability.
- 🧙 **Multi-Step Wizard:** The form is intuitively split into 5 logical steps with real-time progress tracking.
- ⚡ **Real-Time Feedback:** Enjoy step validation, completion indicators, and a smooth loading overlay.
- 📱 **Fully Responsive:** Perfectly optimized for both desktop and mobile devices.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask, scikit-learn, pandas, numpy |
| **Frontend** | React 18, Tailwind CSS 3, Lucide Icons |
| **ML Model** | XGBoost Classifier (SMOTE-balanced) |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/GarvRandhar/Customer-Churn-Prediction-AI-Dashboard.git
cd Customer-Churn-Prediction-AI-Dashboard

# Install Python dependencies
pip install -r requirements.txt

# Install React dependencies
cd client && npm install && cd ..
```

### 2. Run Locally (Development)

**Terminal 1** — Start the Flask backend:
```bash
python app.py
```

**Terminal 2** — Start the React dev server:
```bash
cd client && npm start
```

Open `http://localhost:3000` to view it in the browser. 

*To build for production:*
```bash
cd client && npm run build
# Then visit http://localhost:5001
```

---

## 📂 Project Structure

```text
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

---

## 💡 How to Use

1. **Enter Details:** Fill in customer details across 5 easy steps: *Demographics → Services → Online Features → Contract & Billing → Financials*
2. **Predict:** Click **Predict Churn** on the final step.
3. **Analyze:** View the animated gauge, risk verdict, confidence score, and actionable recommendations.
4. **Repeat:** Click **New Prediction** to analyze another customer.

---

## 🔌 API Reference

### `POST /predict`

**Request Example:**
```json
{
  "gender": "Female", "SeniorCitizen": 0, "Partner": "Yes", "Dependents": "No",
  "tenure": 24, "PhoneService": "Yes", "MultipleLines": "No",
  "InternetService": "Fiber optic", "OnlineSecurity": "Yes", "OnlineBackup": "No",
  "DeviceProtection": "No", "TechSupport": "No", "StreamingTV": "Yes",
  "StreamingMovies": "No", "Contract": "Month-to-month",
  "PaperlessBilling": "Yes", "PaymentMethod": "Electronic check",
  "MonthlyCharges": 70.35, "TotalCharges": 1689.50
}
```

**Response Example:**
```json
{
  "success": true,
  "prediction": "Churn",
  "probability": 0.75,
  "confidence": 75.0
}
```

### `GET /health`
Health check endpoint.
Returns: `{"status": "healthy"}`

---

## 🏭 Production Deployment

```bash
pip install gunicorn
cd client && npm run build && cd ..
gunicorn app:app --workers 4 --bind 0.0.0.0:5000
```

---

## 📜 License & Credits

This project uses the [Telco Customer Churn dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) from Kaggle.