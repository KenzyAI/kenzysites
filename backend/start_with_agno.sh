#!/bin/bash
# Start script for KenzySites Backend - PHASE 2 (With Agno Framework 1.8.0)

echo "🚀 Starting KenzySites Backend - PHASE 2 (With Agno)"
echo "🤖 Using Agno Framework v1.8.0"

# Check current directory and navigate to backend if needed
if [ -f "main_with_agno.py" ]; then
    echo "✅ Found main_with_agno.py in current directory"
else
    echo "📁 Navigating to backend directory..."
    cd backend || exit 1
fi

# Verify file exists
if [ ! -f "main_with_agno.py" ]; then
    echo "❌ Error: main_with_agno.py not found!"
    exit 1
fi

echo "✅ Starting uvicorn server with Agno support..."
# Start with Agno support
uvicorn main_with_agno:app --host 0.0.0.0 --port ${PORT:-8000}