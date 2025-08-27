#!/bin/bash
# Start script for KenzySites Backend - FASE FINAL com Sistema de Landing Pages

echo "🚀 Starting KenzySites Backend - FASE FINAL"
echo "📦 Sistema de Landing Pages com IA + Agno Framework v1.8.0"

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
    echo "Available files:"
    ls -la *.py
    exit 1
fi

echo "✅ Sistema de Landing Pages ativo!"
echo "✅ Starting uvicorn server with full system..."
# Start the complete version with landing pages system
uvicorn main_with_agno:app --host 0.0.0.0 --port ${PORT:-8000}