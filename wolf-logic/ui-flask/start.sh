#!/bin/bash

# OpenMemory Flask UI Startup Script

echo "🚀 Starting OpenMemory Flask UI..."

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if USER_ID is set
if [ -z "$USER_ID" ]; then
    echo "⚠️  USER_ID not set, using default: default-user"
    export USER_ID="default-user"
fi

# Check if MEMORY_API_URL is set
if [ -z "$MEMORY_API_URL" ]; then
    echo "⚠️  MEMORY_API_URL not set, using default: http://openmemory-mcp:8765"
    export MEMORY_API_URL="http://openmemory-mcp:8765"
fi

echo "📊 Configuration:"
echo "  - DEBUG: ${DEBUG:-True}"
echo "  - USER_ID: $USER_ID"
echo "  - MEMORY_API_URL: $MEMORY_API_URL"

# Check if backend is accessible
echo ""
echo "🔍 Checking backend connectivity..."
if command -v curl &> /dev/null; then
    if curl -s -o /dev/null -w "%{http_code}" "$MEMORY_API_URL/docs" | grep -q "200"; then
        echo "✅ Backend is accessible at $MEMORY_API_URL"
    else
        echo "❌ Warning: Cannot reach backend at $MEMORY_API_URL"
        echo "   Make sure the OpenMemory backend is running"
    fi
else
    echo "⚠️  curl not found, skipping connectivity check"
fi

echo ""
echo "🌐 Starting Flask application..."
echo "   Access the UI at: http://localhost:3000"
echo "   Backend MCP Server: http://localhost:8765"
echo ""

# Start the application on port 3000 (matching Next.js UI)
export PORT=3000
python run.py
