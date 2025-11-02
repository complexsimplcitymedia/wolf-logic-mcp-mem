"""
Time Sync HTTP Server for Wolf-Logic
Provides REST API for timestamp synchronization across all services
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service status enum
class ServiceStatus(str, Enum):
    ACTIVE = "active"
    STALE = "stale"
    DISCONNECTED = "disconnected"

# Pydantic models
class SyncRecord(BaseModel):
    service: str
    last_sync: datetime
    last_memory_update: datetime
    status: ServiceStatus

class SyncUpdate(BaseModel):
    service: str
    is_memory_update: bool = False

class TimestampCompare(BaseModel):
    service: str
    timestamp: datetime

class SyncResponse(BaseModel):
    service: str
    timestamp: datetime
    is_memory_update: bool
    success: bool

class StatusResponse(BaseModel):
    service: str
    is_stale: bool
    status: Optional[SyncRecord] = None

class CompareResponse(BaseModel):
    service: str
    client_timestamp: datetime
    server_timestamp: datetime
    is_client_newer: bool
    diff_ms: int
    diff_seconds: float
    needs_sync: bool

# Time Sync Manager
class TimeSyncManager:
    def __init__(self, stale_threshold_ms: int = 60000):
        self.sync_records: Dict[str, SyncRecord] = {}
        self.stale_threshold_ms = stale_threshold_ms

    def register_service(self, service: str) -> None:
        now = datetime.now()
        self.sync_records[service] = SyncRecord(
            service=service,
            last_sync=now,
            last_memory_update=now,
            status=ServiceStatus.ACTIVE
        )
        logger.info(f"[TIME-SYNC] Registered service: {service}")

    def update_sync(self, service: str, is_memory_update: bool = False) -> datetime:
        now = datetime.now()

        if service in self.sync_records:
            record = self.sync_records[service]
            record.last_sync = now
            if is_memory_update:
                record.last_memory_update = now
            record.status = ServiceStatus.ACTIVE
        else:
            self.register_service(service)

        logger.info(f"[TIME-SYNC] {service}: sync={now.isoformat()}, memoryUpdate={is_memory_update}")
        return now

    def check_stale(self, service: str) -> bool:
        if service not in self.sync_records:
            return True

        record = self.sync_records[service]
        now = datetime.now()
        diff_ms = (now - record.last_sync).total_seconds() * 1000
        is_stale = diff_ms > self.stale_threshold_ms

        if is_stale and record.status == ServiceStatus.ACTIVE:
            record.status = ServiceStatus.STALE
            logger.warning(f"[TIME-SYNC] Service {service} is STALE")

        return is_stale

    def get_service_status(self, service: str) -> Optional[SyncRecord]:
        return self.sync_records.get(service)

    def get_all_statuses(self) -> List[SyncRecord]:
        return list(self.sync_records.values())

    def compare_timestamps(self, service: str, client_timestamp: datetime) -> CompareResponse:
        record = self.sync_records.get(service)
        server_timestamp = record.last_memory_update if record else datetime.fromtimestamp(0)

        diff_ms = int((client_timestamp - server_timestamp).total_seconds() * 1000)

        return CompareResponse(
            service=service,
            client_timestamp=client_timestamp,
            server_timestamp=server_timestamp,
            is_client_newer=diff_ms > 0,
            diff_ms=diff_ms,
            diff_seconds=diff_ms / 1000,
            needs_sync=abs(diff_ms) > 1000
        )

    def get_latest_timestamp(self) -> Optional[Dict[str, datetime]]:
        if not self.sync_records:
            return None

        latest = max(
            self.sync_records.items(),
            key=lambda x: x[1].last_memory_update
        )

        return {
            "service": latest[0],
            "timestamp": latest[1].last_memory_update
        }

# Initialize manager and FastAPI app
sync_manager = TimeSyncManager()

# Register known services
SERVICES = ['flask-ui', 'fastapi-rest', 'fastapi-mcp', 'sse-server', 'pgvector', 'neo4j']
for service in SERVICES:
    sync_manager.register_service(service)

app = FastAPI(
    title="Wolf-Logic Time Sync Server",
    description="Timestamp synchronization for distributed memory services",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Endpoints =============

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "wolf-logic-timesync",
        "registered_services": len(sync_manager.sync_records)
    }

@app.post("/sync", response_model=SyncResponse)
def sync_timestamp(update: SyncUpdate):
    """Update sync timestamp for a service"""
    timestamp = sync_manager.update_sync(update.service, update.is_memory_update)
    return SyncResponse(
        service=update.service,
        timestamp=timestamp,
        is_memory_update=update.is_memory_update,
        success=True
    )

@app.get("/sync/status/{service}", response_model=StatusResponse)
def check_sync_status(service: str):
    """Check if a service is in sync or stale"""
    is_stale = sync_manager.check_stale(service)
    status = sync_manager.get_service_status(service)

    return StatusResponse(
        service=service,
        is_stale=is_stale,
        status=status
    )

@app.get("/sync/status")
def get_all_sync_status():
    """Get sync status for all services"""
    statuses = sync_manager.get_all_statuses()

    return {
        "services": [
            {
                "service": s.service,
                "last_sync": s.last_sync.isoformat(),
                "last_memory_update": s.last_memory_update.isoformat(),
                "status": s.status,
                "is_stale": sync_manager.check_stale(s.service)
            }
            for s in statuses
        ],
        "total_services": len(statuses),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/sync/compare", response_model=CompareResponse)
def compare_timestamps(compare: TimestampCompare):
    """Compare client timestamp with server timestamp"""
    return sync_manager.compare_timestamps(compare.service, compare.timestamp)

@app.get("/sync/latest")
def get_latest_timestamp():
    """Get the most recent memory update timestamp across all services"""
    latest = sync_manager.get_latest_timestamp()

    return {
        "latest": {
            "service": latest["service"],
            "timestamp": latest["timestamp"].isoformat()
        } if latest else None,
        "current_time": datetime.now().isoformat()
    }

@app.post("/sync/register/{service}")
def register_service(service: str):
    """Register a new service for time synchronization"""
    sync_manager.register_service(service)

    return {
        "service": service,
        "registered": True,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("TIMESYNC_PORT", 8900))

    logger.info(f"Starting Wolf-Logic Time Sync Server on port {port}")
    logger.info(f"Registered services: {', '.join(SERVICES)}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

