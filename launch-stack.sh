#!/bin/bash
# Wolf-Logic MCP - Complete Stack Startup
# Launches: PostgreSQL, Neo4j, Qdrant, MCP Server, REST API, Flask UI

set -e

echo "🚀 Wolf-Logic MCP - Starting Complete Stack"
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker not running"
    exit 1
fi

# Create .env if missing
if [ ! -f .env ]; then
    echo "Creating .env from example..."
    cp .env.example .env 2>/dev/null || echo "No .env.example found, continuing..."
fi

echo "Building and starting services..."
docker compose -f docker-compose.yml up --build -d

echo ""
echo "✅ Services starting!"
echo ""
echo "📍 Access Points:"
echo "  🌐 Flask Dashboard:    http://localhost:3000"
echo "  🔴 REST API:           http://localhost:8888"
echo "  🟢 MCP Server:         http://localhost:8765"
echo "  📊 API Docs:           http://localhost:8888/docs"
echo "  🗄️  PostgreSQL:         localhost:8432"
echo "  📈 Neo4j Browser:      http://localhost:7474"
echo "  🎯 Qdrant:             http://localhost:6333"
echo ""
echo "📋 Service Status:"
docker compose -f docker-compose.yml ps
echo ""
echo "📝 View Logs:"
echo "  All:        docker compose -f docker-compose.yml logs -f"
echo "  API:        docker compose -f docker-compose.yml logs -f api"
echo "  MCP:        docker compose -f docker-compose.yml logs -f mcp"
echo "  Flask:      docker compose -f docker-compose.yml logs -f web"
echo ""
echo "⏹️  Stop All:  docker compose -f docker-compose.yml down"
echo ""

