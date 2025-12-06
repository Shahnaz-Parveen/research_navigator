#!/usr/bin/env bash
# Build script for Render deployment

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Downloading spaCy language model..."
python -m spacy download en_core_web_sm

echo "Build complete!"
