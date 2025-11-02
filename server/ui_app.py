"""
FastAPI-based UI Server for Wolf-Logic MCP
Replaces Flask for better performance and async support
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MEMORY_API_URL = os.getenv("MEMORY_API_URL", "http://localhost:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Create FastAPI app
app = FastAPI(
    title="Wolf-Logic Memory Dashboard",
    description="Fast UI Dashboard for Memory Management",
    version="1.0.0",
    docs_url="/api/docs" if DEBUG else None,
    redoc_url="/api/redoc" if DEBUG else None,
    openapi_url="/api/openapi.json" if DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "wolf-logic", "ui-flask", "static")
templates_dir = os.path.join(os.path.dirname(__file__), "..", "wolf-logic", "ui-flask", "templates")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"✓ Mounted static files from {static_dir}")
else:
    logger.warning(f"⚠ Static directory not found: {static_dir}")

# ============= Pydantic Models =============

class Memory(BaseModel):
    id: Optional[str] = None
    content: str
    created_at: Optional[str] = None
    user_id: Optional[str] = None
    app: Optional[Dict[str, Any]] = None
    categories: Optional[List[str]] = []
    state: Optional[str] = "active"


class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 10
    offset: Optional[int] = 0


class DashboardStats(BaseModel):
    total_memories: int
    recent_count: int
    total_users: int


# ============= Health & Status =============

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "wolf-logic-ui"}


@app.get("/api/status")
async def status():
    """Get system status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MEMORY_API_URL}/docs", timeout=5)
            backend_status = "online" if response.status_code == 200 else "offline"
    except Exception as e:
        logger.error(f"Backend check failed: {e}")
        backend_status = "offline"

    return {
        "backend": backend_status,
        "ui": "online",
        "redis": "configured" if REDIS_URL else "not configured",
        "debug": DEBUG,
    }


# ============= Memory API Routes =============

@app.get("/api/memories")
async def list_memories(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    user_id: Optional[str] = None,
):
    """List all memories with pagination"""
    try:
        params = {
            "page": page,
            "page_size": page_size,
            "search": search or "",
        }
        if user_id:
            params["user_id"] = user_id

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MEMORY_API_URL}/memories",
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error fetching memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memories/{memory_id}")
async def get_memory(memory_id: str):
    """Get a specific memory"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MEMORY_API_URL}/memories/{memory_id}",
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error fetching memory {memory_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memories/search")
async def search_memories(query: SearchQuery):
    """Search memories"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MEMORY_API_URL}/search",
                json={
                    "query": query.query,
                    "limit": query.limit,
                    "offset": query.offset,
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/stats")
async def get_dashboard_stats(user_id: Optional[str] = None):
    """Get dashboard statistics"""
    try:
        params = {}
        if user_id:
            params["user_id"] = user_id

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MEMORY_API_URL}/stats",
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error fetching stats: {e}")
        return {
            "total_memories": 0,
            "recent_count": 0,
            "total_users": 0,
        }


# ============= Frontend Routes =============

@app.get("/", response_class=HTMLResponse)
async def index():
    """Main dashboard page"""
    return await serve_template("dashboard.html")


@app.get("/memories", response_class=HTMLResponse)
async def memories_page():
    """Memories list page"""
    return await serve_template("memories/list.html")


@app.get("/memories/{memory_id}", response_class=HTMLResponse)
async def memory_detail(memory_id: str):
    """Memory detail page"""
    return await serve_template("memories/detail.html")


@app.get("/search", response_class=HTMLResponse)
async def search_page():
    """Search page"""
    return await serve_template("search.html")


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """Admin dashboard"""
    return await serve_template("admin/dashboard.html")


async def serve_template(template_name: str) -> str:
    """Serve HTML template"""
    template_path = os.path.join(templates_dir, template_name)
    if os.path.exists(template_path):
        return FileResponse(template_path)
    else:
        # Return a simple fallback
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Wolf-Logic Memory Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
                h1 {{ color: #333; }}
                .status {{ padding: 10px; border-radius: 4px; margin: 10px 0; }}
                .ok {{ background: #d4edda; color: #155724; }}
                .error {{ background: #f8d7da; color: #721c24; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧠 Wolf-Logic Memory Dashboard</h1>
                <p>Loading template: {template_name}</p>
                <div class="status ok">✓ UI Server is running (FastAPI)</div>
                <div class="status ok">✓ Backend API connection active</div>
                <nav>
                    <a href="/">Home</a> |
                    <a href="/memories">Memories</a> |
                    <a href="/search">Search</a> |
                    <a href="/admin">Admin</a> |
                    <a href="/api/docs">API Docs</a>
                </nav>
            </div>
            <script>
                // Simple SPA routing
                document.addEventListener('DOMContentLoaded', function() {{
                    console.log('Wolf-Logic UI loaded');
                }});
            </script>
        </body>
        </html>
        """


# ============= Error Handlers =============

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": str(exc),
        "status": 500,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("UI_PORT", 3000)),
        reload=DEBUG,
        log_level="info" if DEBUG else "warning",
    )

