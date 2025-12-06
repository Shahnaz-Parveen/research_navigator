#!/usr/bin/env bash
# Build script for Render deployment

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Downloading spaCy language model..."
python -m spacy download en_core_web_sm

echo "Initializing database..."
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized!')"

echo "Build complete!"
