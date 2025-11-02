version: '3.9'

services:
  # ============= Data Stores =============

  postgres:
    image: pgvector/pgvector:0.8.1-pg18-trixie
    container_name: pgvector_db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-postgres}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - wolf-logic-net

  neo4j:
    image: neo4j:ubi9
    container_name: neo4j_graph
    environment:
      NEO4J_AUTH: ${NEO4J_USERNAME:-neo4j}/${NEO4J_PASSWORD:-mem0graph}
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_apoc_export_file_enabled: "true"
      NEO4J_apoc_import_file_enabled: "true"
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4jdata:/data
    healthcheck:
      test: ["CMD", "wget", "http://localhost:7474", "-q", "-O", "-"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - wolf-logic-net

  qdrant:
    image: qdrant/qdrant:dev
    container_name: qdrant_vector
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrantdata:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - wolf-logic-net

  redis:
    image: redis:7-alpine
    container_name: redis_cache
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - wolf-logic-net

  # ============= Applications =============

  api:
    build:
      context: ./server
      dockerfile: dev.Dockerfile
    container_name: fastapi_backend
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      qdrant:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-postgres}
      REDIS_URL: redis://redis:6379
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USERNAME: ${NEO4J_USERNAME:-neo4j}
      NEO4J_PASSWORD: ${NEO4J_PASSWORD:-mem0graph}
      # Ollama is OPTIONAL - only set if you have proper GPU acceleration
      # OLLAMA_BASE_URL: http://ollama:11434
      # USE_OLLAMA: "false"
    ports:
      - "8765:8000"
    volumes:
      - ./server:/app
      - ./wolf-logic:/app/packages/wolf-logic
      - ./history:/app/history
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - wolf-logic-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ============= Background Workers =============

  celery-worker:
    build:
      context: ./server
      dockerfile: dev.Dockerfile
    container_name: celery_worker
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    environment:
      REDIS_URL: redis://redis:6379
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-postgres}
    volumes:
      - ./server:/app
      - ./wolf-logic:/app/packages/wolf-logic
    command: celery -A celery_config worker -l info --concurrency=4
    networks:
      - wolf-logic-net

  celery-beat:
    build:
      context: ./server
      dockerfile: dev.Dockerfile
    container_name: celery_beat
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    environment:
      REDIS_URL: redis://redis:6379
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-postgres}
    volumes:
      - ./server:/app
      - ./wolf-logic:/app/packages/wolf-logic
    command: celery -A celery_config beat -l info
    networks:
      - wolf-logic-net

  # ============= Frontend =============

  web:
    build:
      context: ./wolf-logic/ui-flask
      dockerfile: Dockerfile
    container_name: flask_frontend
    depends_on:
      api:
        condition: service_healthy
    environment:
      API_URL: http://api:8000
      MEMORY_API_URL: http://api:8000
      REDIS_URL: redis://redis:6379
      DEBUG: "False"
    ports:
      - "3000:3000"
    volumes:
      - ./wolf-logic/ui-flask:/app
    networks:
      - wolf-logic-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============= Optional: Ollama (Local LLM) =============

  ollama:
    image: ollama/ollama:latest
    container_name: ollama_llm
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    networks:
      - wolf-logic-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

# ============= Volumes =============

volumes:
  pgdata:
    driver: local
  neo4jdata:
    driver: local
  qdrantdata:
    driver: local
  redisdata:
    driver: local
  ollama_models:
    driver: local

# ============= Networks =============

networks:
  wolf-logic-net:
    driver: bridge
