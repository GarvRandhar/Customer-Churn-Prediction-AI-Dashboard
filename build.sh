#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install Node modules and build the React app
cd client
npm install
npm run build
cd ..
