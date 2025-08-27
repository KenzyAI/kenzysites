#!/bin/bash
# Start script for KenzySites Backend - PHASE 1 (Simple version without Agno)

echo "🚀 Starting KenzySites Backend - PHASE 1 (Simple)"
echo "📦 Using minimal dependencies without Agno Framework"

# Check current directory and navigate to backend if needed
if [ -f "main_simple.py" ]; then
    echo "✅ Found main_simple.py in current directory"
else
    echo "📁 Navigating to backend directory..."
    cd backend || exit 1
fi

# Verify file exists
if [ ! -f "main_simple.py" ]; then
    echo "❌ Error: main_simple.py not found!"
    exit 1
fi

echo "✅ Starting uvicorn server..."
# Start the simple version
uvicorn main_simple:app --host 0.0.0.0 --port ${PORT:-8000}