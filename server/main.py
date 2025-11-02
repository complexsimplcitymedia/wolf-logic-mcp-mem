import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from wolf-logic import Memory
from redis_manager import init_redis, memory_cache, session_manager, rate_limiter
from celery_tasks import process_memory_batch, generate_embeddings, compute_user_stats
# from memory_collection_routes import memory_collection_router, initialize_agent  # DISABLED - module not found

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()


POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_COLLECTION_NAME = os.environ.get("POSTGRES_COLLECTION_NAME", "memories")

# Neo4j configuration - Optional, only set if NEO4J_URI is explicitly provided
NEO4J_URI = os.environ.get("NEO4J_URI", "").strip() or None
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "").strip() or None
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "").strip() or None

MEMGRAPH_URI = os.environ.get("MEMGRAPH_URI", "").strip() or None
MEMGRAPH_USERNAME = os.environ.get("MEMGRAPH_USERNAME", "").strip() or None
MEMGRAPH_PASSWORD = os.environ.get("MEMGRAPH_PASSWORD", "").strip() or None

# Ollama Configuration for local LLM and embeddings
# Try multiple Ollama endpoints (Windows can be accessed via multiple IPs)
def find_ollama_url():
    """Try to find accessible Ollama instance"""
    import requests
    possible_urls = [
        "http://100.110.82.180:11434",  # Tailscale
        "http://10.0.0.209:11434",       # Local network
        "http://127.0.0.1:11434",        # Localhost
        "http://localhost:11434",        # Localhost alternative
    ]
    for url in possible_urls:
        try:
            requests.get(f"{url}/api/tags", timeout=2)
            logging.info(f"✓ Found Ollama at: {url}")
            return url
        except:
            continue
    logging.warning("⚠ Ollama not found at any known URL, using default")
    return "http://100.110.82.180:11434"

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL") or find_ollama_url()
OLLAMA_LLM_MODEL = os.environ.get("OLLAMA_LLM_MODEL", "llama3.2:3b")
OLLAMA_EMBEDDER_MODEL = os.environ.get("OLLAMA_EMBEDDER_MODEL", "nomic-embed-text")

# Fallback OpenAI (optional)
OLLAMA_URL = os.environ.get("OLLAMA_URL")
HISTORY_DB_PATH = os.environ.get("HISTORY_DB_PATH", "/app/history/history.db")

# Determine which LLM provider to use
USE_OLLAMA = os.environ.get("USE_OLLAMA", "true").lower() == "true"

# Log environment variables for debugging
logging.info(f"NEO4J_URI: {NEO4J_URI}")
logging.info(f"NEO4J_USERNAME: {NEO4J_USERNAME}")
logging.info(f"NEO4J_PASSWORD: {'***' if NEO4J_PASSWORD else 'Not set'}")

if USE_OLLAMA:
    logging.info(f"🚀 Using Ollama (Local LLM)")
    logging.info(f"  Ollama URL: {OLLAMA_BASE_URL}")
    logging.info(f"  LLM Model: {OLLAMA_LLM_MODEL}")
    logging.info(f"  Embedder Model: {OLLAMA_EMBEDDER_MODEL}")
else:
    logging.info(f"🔑 Using OpenAI")

# Build graph_store config only if Neo4j credentials are available
graph_store_config = None
if NEO4J_URI and NEO4J_USERNAME and NEO4J_PASSWORD:
    graph_store_config = {
        "provider": "neo4j",
        "config": {"url": NEO4J_URI, "username": NEO4J_USERNAME, "password": NEO4J_PASSWORD},
    }
    logging.info("Neo4j graph store configured")
elif MEMGRAPH_URI and MEMGRAPH_USERNAME and MEMGRAPH_PASSWORD:
    graph_store_config = {
        "provider": "memgraph",
        "config": {"url": MEMGRAPH_URI, "username": MEMGRAPH_USERNAME, "password": MEMGRAPH_PASSWORD},
    }
    logging.info("Memgraph graph store configured")
else:
    logging.warning("No graph store credentials provided - graph store will be disabled")

DEFAULT_CONFIG = {
    "version": "v1.1",
    "vector_store": {
        "provider": "pgvector",
        "config": {
            "host": POSTGRES_HOST,
            "port": int(POSTGRES_PORT),
            "dbname": POSTGRES_DB,
            "user": POSTGRES_USER,
            "password": POSTGRES_PASSWORD,
            "collection_name": POSTGRES_COLLECTION_NAME,
        },
    },
    "graph_store": graph_store_config,
    "llm": {
        "provider": "ollama" if USE_OLLAMA else "ollama",
        "config": (
            {
                "model": OLLAMA_LLM_MODEL,
                "temperature": 0.1,
                "max_tokens": 2000,
                "ollama_base_url": OLLAMA_BASE_URL,
            }
            if USE_OLLAMA
            else {
                "api_key": OLLAMA_URL,
                "temperature": 0.2,
                "model": "gpt-4o",
            }
        ),
    },
    "embedder": {
        "provider": "ollama" if USE_OLLAMA else "ollama",
        "config": (
            {
                "model": OLLAMA_EMBEDDER_MODEL,
                "ollama_base_url": OLLAMA_BASE_URL,
            }
            if USE_OLLAMA
            else {
                "api_key": OLLAMA_URL,
                "model": "text-embedding-3-small",
            }
        ),
    },
    "history_db_path": HISTORY_DB_PATH,
}


MEMORY_INSTANCE = Memory.from_config(DEFAULT_CONFIG)

# Initialize the memory collection agent
# initialize_agent(  # DISABLED - module not found
#     memory_instance=MEMORY_INSTANCE,
#     user_id="default_user",
#     agent_id="memory_collector"
# )

app = FastAPI(
    title="Mem0 REST APIs",
    description="A REST API for managing and searching memories for your AI Agents and Apps.",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis on startup
@app.on_event("startup")
async def startup_event():
    """Initialize Redis cache on app startup"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    logging.info(f"Initializing Redis: {redis_url}")
    init_redis(redis_url)
    logging.info("✓ Application startup complete")


@app.get("/health", summary="Health check")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "wolf-logic-api",
        "redis": "connected" if memory_cache and memory_cache.cache.connected else "disconnected",
    }


@app.get("/stats", summary="Get system statistics")
def get_stats():
    """Get system statistics"""
    # Check cache first
    cached = memory_cache.get_cached_stats("system") if memory_cache else None
    if cached:
        return cached

    # Compute stats
    stats = {
        "timestamp": os.popen("date -Iseconds").read().strip(),
        "service": "wolf-logic-api",
        "redis_enabled": memory_cache is not None,
    }

    # Cache stats for 5 minutes
    if memory_cache:
        memory_cache.cache_stats("system", stats)

    return stats


class Message(BaseModel):
    role: str = Field(..., description="Role of the message (user or assistant).")
    content: str = Field(..., description="Message content.")


class MemoryCreate(BaseModel):
    messages: List[Message] = Field(..., description="List of messages to store.")
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    run_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query.")
    user_id: Optional[str] = None
    run_id: Optional[str] = None
    agent_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


@app.post("/configure", summary="Configure Mem0")
def set_config(config: Dict[str, Any]):
    """Set memory configuration."""
    global MEMORY_INSTANCE
    MEMORY_INSTANCE = Memory.from_config(config)
    return {"message": "Configuration set successfully"}


@app.post("/memories", summary="Create memories")
def add_memory(memory_create: MemoryCreate):
    """Store new memories."""
    if not any([memory_create.user_id, memory_create.agent_id, memory_create.run_id]):
        raise HTTPException(status_code=400, detail="At least one identifier (user_id, agent_id, run_id) is required.")

    params = {k: v for k, v in memory_create.model_dump().items() if v is not None and k != "messages"}
    try:
        response = MEMORY_INSTANCE.add(messages=[m.model_dump() for m in memory_create.messages], **params)
        return JSONResponse(content=response)
    except Exception as e:
        logging.exception("Error in add_memory:")  # This will log the full traceback
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories", summary="Get memories")
def get_all_memories(
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    agent_id: Optional[str] = None,
):
    """Retrieve stored memories."""
    if not any([user_id, run_id, agent_id]):
        raise HTTPException(status_code=400, detail="At least one identifier is required.")
    try:
        params = {
            k: v for k, v in {"user_id": user_id, "run_id": run_id, "agent_id": agent_id}.items() if v is not None
        }
        return MEMORY_INSTANCE.get_all(**params)
    except Exception as e:
        logging.exception("Error in get_all_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories/{memory_id}", summary="Get a memory")
def get_memory(memory_id: str):
    """Retrieve a specific memory by ID."""
    try:
        return MEMORY_INSTANCE.get(memory_id)
    except Exception as e:
        logging.exception("Error in get_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", summary="Search memories")
def search_memories(search_req: SearchRequest):
    """Search for memories based on a query."""
    try:
        params = {k: v for k, v in search_req.model_dump().items() if v is not None and k != "query"}
        return MEMORY_INSTANCE.search(query=search_req.query, **params)
    except Exception as e:
        logging.exception("Error in search_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/memories/{memory_id}", summary="Update a memory")
def update_memory(memory_id: str, updated_memory: Dict[str, Any]):
    """Update an existing memory with new content.
    
    Args:
        memory_id (str): ID of the memory to update
        updated_memory (str): New content to update the memory with
        
    Returns:
        dict: Success message indicating the memory was updated
    """
    try:
        return MEMORY_INSTANCE.update(memory_id=memory_id, data=updated_memory)
    except Exception as e:
        logging.exception("Error in update_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories/{memory_id}/history", summary="Get memory history")
def memory_history(memory_id: str):
    """Retrieve memory history."""
    try:
        return MEMORY_INSTANCE.history(memory_id=memory_id)
    except Exception as e:
        logging.exception("Error in memory_history:")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memories/{memory_id}", summary="Delete a memory")
def delete_memory(memory_id: str):
    """Delete a specific memory by ID."""
    try:
        MEMORY_INSTANCE.delete(memory_id=memory_id)
        return {"message": "Memory deleted successfully"}
    except Exception as e:
        logging.exception("Error in delete_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memories", summary="Delete all memories")
def delete_all_memories(
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    agent_id: Optional[str] = None,
):
    """Delete all memories for a given identifier."""
    if not any([user_id, run_id, agent_id]):
        raise HTTPException(status_code=400, detail="At least one identifier is required.")
    try:
        params = {
            k: v for k, v in {"user_id": user_id, "run_id": run_id, "agent_id": agent_id}.items() if v is not None
        }
        MEMORY_INSTANCE.delete_all(**params)
        return {"message": "All relevant memories deleted"}
    except Exception as e:
        logging.exception("Error in delete_all_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset", summary="Reset all memories")
def reset_memory():
    """Completely reset stored memories."""
    try:
        MEMORY_INSTANCE.reset()
        return {"message": "All memories reset"}
    except Exception as e:
        logging.exception("Error in reset_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", summary="Redirect to the OpenAPI documentation", include_in_schema=False)
def home():
    """Redirect to the OpenAPI documentation."""
    return RedirectResponse(url="/docs")


# Include memory collection agent routes
# app.include_router(memory_collection_router)  # DISABLED - module not found
