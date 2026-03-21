#!/bin/bash

echo "🚀 Starting Customer Churn Prediction App..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found at $SCRIPT_DIR/.venv"
    echo "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if dependencies are installed
if ! "$VENV_PYTHON" -c "import flask" 2>/dev/null; then
    echo "❌ Python dependencies not installed"
    echo "Run: $VENV_PYTHON -m pip install -r requirements.txt"
    exit 1
fi

if [ ! -d "client/build" ]; then
    echo "⚠️  React app not built"
    echo "Building React app..."
    cd client
    npm install
    npm run build
    cd ..
    echo ""
fi

echo "✅ All dependencies ready"
echo ""
echo "🎯 Starting Flask server..."
echo ""
echo "🧹 Cleaning up existing processes on port 5001..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
sleep 1
echo ""
echo "📱 Open your browser and visit: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

"$VENV_PYTHON" app.py
