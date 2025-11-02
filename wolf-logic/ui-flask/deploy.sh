#!/bin/bash

# OpenMemory Flask UI - Quick Deploy Script
# User: cadillacthewolf

set -e

echo "🚀 Deploying OpenMemory Flask UI..."
echo ""

# Set credentials
export OLLAMA_URL="your-openai-api-key-here"
export USER="cadillacthewolf"

echo "📋 Configuration:"
echo "   User: $USER"
echo "   OpenAI Key: ${OLLAMA_URL:0:20}..."
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker stop wolf-logic_ui wolf-logic-mcp wolf-logic_store 2>/dev/null || true
docker rm wolf-logic_ui wolf-logic-mcp wolf-logic_store 2>/dev/null || true

# Build and start services
echo ""
echo "🔨 Building Flask UI..."
docker-compose build

echo ""
echo "🚀 Starting all services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
echo ""
echo "✅ Service Status:"
docker ps --filter "name=wolf-logic_ui" --filter "name=openmemory-mcp" --filter "name=wolf-logic_store" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ OpenMemory Flask UI is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Frontend UI:  http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8765"
echo "📊 API Docs:     http://localhost:8765/docs"
echo "🗄️  Qdrant:      http://localhost:6333"
echo ""
echo "📝 View logs:"
echo "   docker logs -f wolf-logic_ui"
echo "   docker logs -f openmemory-mcp"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
