#!/bin/bash
# Wolf-Logic MCP - Trixie-based Launch

set -e

echo "🚀 Wolf-Logic MCP - Starting on Trixie"
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker not running"
    exit 1
fi

# Create .env if missing
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env from template"
fi

# Build and launch
echo "Starting services..."
docker-compose -f docker-compose.yml up -d

echo ""
echo "✓ Wolf-Logic MCP is launching!"
echo ""
echo "Services:"
echo "  🌐 Flask Dashboard:  http://localhost:3000"
echo "  🔴 REST API:         http://localhost:8888"
echo "  🟢 MCP Connection:   http://localhost:8765"
echo "  📊 API Docs:         http://localhost:8765/docs"
echo "  🗄️  PostgreSQL:       localhost:5432"
echo "  📈 Neo4j:            http://localhost:7474"
echo "  🎯 Qdrant:           http://localhost:6333"
echo "  💾 Redis:            localhost:6379"
echo ""
echo "Logs:"
echo "  All:     docker-compose -f docker-compose.yml logs -f"
echo "  REST API: docker-compose -f docker-compose.yml logs -f api"
echo "  MCP:     docker-compose -f docker-compose.yml logs -f mcp"
echo "  Flask:   docker-compose -f docker-compose.yml logs -f web"
echo "  Workers: docker-compose -f docker-compose.yml logs -f celery-worker"
echo ""

