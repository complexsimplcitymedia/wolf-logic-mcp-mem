# 🧠 Wolf-Logic MCP - Memory Context Protocol Server

Complete memory management system for AI agents with distributed architecture, AMD ROCM support, and multi-store synchronization.

## 🏗️ Architecture

### Core Services

| Service | Port | Purpose |
|---------|------|---------|
| **Flask Dashboard** | 3000 | Web UI for memory browsing |
| **REST API** | 8888 | FastAPI memory CRUD operations |
| **MCP Server** | 8765 | Model Context Protocol |
| **Time Sync** | 8900 | Timestamp synchronization |
| **PostgreSQL + PgVector** | 8432 | Vector embeddings storage |
| **Neo4j** | 7474/7687 | Graph relationships |
| **Qdrant** | 6333 | Vector similarity search |

### Data Flow

```
User/AI Agent
    ↓
Flask UI (3000) ──→ REST API (8888)
    ↓                     ↓
MCP Server (8765) ────────┤
    ↓                     ↓
Time Sync (8900) ←────────┤
    ↓                     ↓
┌───────────────────────────────┐
│   PostgreSQL   Neo4j   Qdrant │
│    (8432)     (7687)   (6333) │
└───────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- AMD ROCM drivers (optional, for GPU acceleration)
- 16GB+ RAM recommended

### Launch Everything

```bash
cd /mnt/s/wolf-logic-mcp
docker compose -f docker-compose.yml up -d
```

### Access Services

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8888/docs
- **Neo4j Browser**: http://localhost:7474
- **Time Sync Status**: http://localhost:8900/sync/status

## 📋 API Endpoints

### REST API (Port 8888)

**Memory Operations:**
- `POST /memories` - Create memory
- `GET /memories` - List memories (requires user_id/agent_id/run_id)
- `GET /memories/{id}` - Get specific memory
- `PUT /memories/{id}` - Update memory
- `DELETE /memories/{id}` - Delete memory
- `POST /search` - Semantic search
- `GET /memories/{id}/history` - Memory history

**System:**
- `GET /health` - Health check
- `GET /stats` - System statistics
- `POST /configure` - Update configuration

### Time Sync API (Port 8900)

**Synchronization:**
- `POST /sync` - Update service timestamp
- `GET /sync/status/{service}` - Check service status
- `GET /sync/status` - All services status
- `POST /sync/compare` - Compare timestamps
- `GET /sync/latest` - Latest update timestamp

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=memories
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=mem0graph

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:3b
OLLAMA_EMBEDDER_MODEL=nomic-embed-text
```

**Flask UI (.env):**
```env
MEMORY_API_URL=http://localhost:8888
PGVECTOR_URL=postgresql://postgres:postgres@localhost:8432/memories
USER_ID=cadillacthewolf
```

## 🐳 Docker Services

### Data Stores
- **PostgreSQL + PgVector** - Primary memory storage with vector embeddings
- **Neo4j** - Graph relationships between memories
- **Qdrant** - Fast vector similarity search

### Application Services
- **FastAPI REST API** - Memory CRUD operations
- **FastAPI MCP Server** - Model Context Protocol
- **Flask Dashboard** - Web UI
- **Time Sync Server** - Timestamp synchronization

### Background Services
- **Ollama** (optional) - Local LLM for embeddings

## 📊 Memory Storage

### PostgreSQL Schema
```sql
CREATE TABLE memories (
    id UUID PRIMARY KEY,
    user_id VARCHAR,
    content TEXT,
    embedding VECTOR(384),
    created_at TIMESTAMP,
    metadata JSONB
);
```

### Neo4j Graph
```cypher
(User)-[:CREATED]->(Memory)
(Memory)-[:MENTIONS]->(Entity)
(Entity)-[:RELATES_TO]->(Entity)
```

## 🔴 AMD ROCM Support

### Job Agent with ROCM

Located in `server/Job Agent/`:
- `ollama_job_rocm.py` - ROCM-enabled Ollama client
- `ollama_job_async.py` - Async job processing
- `ollama_job_batch.py` - Batch inference

### Launch with ROCM

```bash
docker compose -f docker-compose.job-agent.yml up -d
```

Requires:
- AMD GPU with ROCM drivers
- `/dev/kfd` and `/dev/dri` device access

## 🧪 Development

### Install Dependencies

**Backend:**
```bash
cd server
pip install -r requirements.txt
```

**Frontend:**
```bash
cd wolf-logic/ui-flask
pip install -r requirements.txt
```

**TypeScript MCP Servers:**
```bash
cd servers
npm install
npm run build
```

### Run Tests

```bash
# Python tests
cd tests
pytest

# TypeScript tests
cd servers
npm test
```

## 📝 Project Structure

```
wolf-logic-mcp/
├── server/                 # FastAPI backend
│   ├── main.py            # REST API
│   ├── timesync_app.py    # Time sync server
│   ├── redis_manager.py   # Redis cache (optional)
│   ├── celery_*.py        # Background tasks
│   └── Job Agent/         # AMD ROCM jobs
├── servers/               # TypeScript MCP servers
│   └── src/
│       ├── memory/        # Memory MCP server
│       ├── timesync/      # Time sync MCP
│       └── everything/    # Demo server
├── wolf-logic/            # Wolf-Logic library
│   └── ui-flask/          # Flask dashboard
├── tests/                 # Test suite
├── docker-compose.yml     # Main services
└── docker-compose.job-agent.yml  # ROCM job agent
```

## 🔐 Security Notes

- Change default passwords in production
- Use environment variables for secrets
- Enable authentication for Neo4j/Qdrant
- Run behind reverse proxy (nginx) in production

## 📚 Documentation

- **AMD ROCM Setup**: See `AMD_ROCM_SETUP.md`
- **API Documentation**: http://localhost:8888/docs
- **Architecture Details**: See inline comments

## 🤝 Contributing

This is a Complex Simplicity Media project. Contributions welcome.

## 📄 License

MIT License - See LICENSE file

## 🏷️ Version

Current: 1.0.0  
Protocol: MCP 0.6.2  
Python SDK: Compatible with wolf-logicai>=0.1.48

---

**Built with ❤️ by Complex Simplicity Media**  
**No Nvidia - Pure AMD ROCM** 🔴

