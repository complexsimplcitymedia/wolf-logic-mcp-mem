#!/bin/bash
# Wolf-Logic MCP - Single Directory Launch Script
# Start everything with one command: ./launch.sh

set -e

echo "🚀 Wolf-Logic MCP - Launching..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Building and starting services...${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Creating .env file with defaults...${NC}"
    cat > .env << EOF
# Wolf-Logic MCP Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=memories
POSTGRES_PORT=5432

NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=mem0graph

REDIS_URL=redis://redis:6379

# Optional: Ollama (disabled by default due to AMD/acceleration issues)
# OLLAMA_BASE_URL=http://ollama:11434
# USE_OLLAMA=true

DEBUG=false
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
fi

echo ""
echo -e "${BLUE}Starting Docker services...${NC}"
docker-compose -f Dockerfile up -d

echo ""
echo -e "${GREEN}✓ Services starting!${NC}"
echo ""
echo -e "${BLUE}Waiting for services to be healthy...${NC}"

# Wait for API to be ready
echo "Waiting for FastAPI backend..."
for i in {1..60}; do
    if curl -s http://localhost:8765/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ FastAPI backend is ready${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${YELLOW}⚠️  Timeout waiting for backend. Check logs with: docker-compose -f Dockerfile logs api${NC}"
    fi
    echo -n "."
    sleep 1
done

# Wait for Flask frontend to be ready
echo "Waiting for Flask frontend..."
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Flask frontend is ready${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${YELLOW}⚠️  Timeout waiting for frontend. Check logs with: docker-compose -f Dockerfile logs web${NC}"
    fi
    echo -n "."
    sleep 1
done

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 Wolf-Logic MCP is RUNNING!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📍 Access Points:${NC}"
echo "   🌐 Flask Dashboard:    ${GREEN}http://localhost:3000${NC}"
echo "   🔌 FastAPI Backend:    ${GREEN}http://localhost:8765${NC}"
echo "   📊 API Docs:           ${GREEN}http://localhost:8765/docs${NC}"
echo "   🗄️  PostgreSQL:         ${GREEN}localhost:5432${NC}"
echo "   📈 Neo4j:              ${GREEN}http://localhost:7474${NC}"
echo "   🎯 Qdrant:             ${GREEN}http://localhost:6333${NC}"
echo "   💾 Redis:              ${GREEN}localhost:6379${NC}"
echo ""
echo -e "${BLUE}💻 Useful Commands:${NC}"
echo "   View logs:             ${YELLOW}docker-compose -f Dockerfile logs -f${NC}"
echo "   View specific service: ${YELLOW}docker-compose -f Dockerfile logs -f api${NC}"
echo "   Stop services:         ${YELLOW}docker-compose -f Dockerfile down${NC}"
echo "   Stop and remove data:  ${YELLOW}docker-compose -f Dockerfile down -v${NC}"
echo ""
echo -e "${BLUE}Services Running:${NC}"
docker-compose -f Dockerfile ps
echo ""

