#!/bin/bash
# Start script for KenzySites Backend - PHASE 1 (Simple version without Agno)

echo "🚀 Starting KenzySites Backend - PHASE 1 (Simple)"
echo "📦 Using minimal dependencies without Agno Framework"

# Start the simple version
uvicorn main_simple:app --host 0.0.0.0 --port ${PORT:-8000}