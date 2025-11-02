"""
Celery Configuration for Wolf-Logic MCP
Handles background task processing
"""

import os
import logging
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configure Celery
celery_app = Celery(
    "wolf-logic",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/1"),
    include=[
        "celery_tasks.memory_tasks",
        "celery_tasks.embedding_tasks",
        "celery_tasks.analytics_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # Results expire after 1 hour
    task_acks_late=True,  # Acknowledge after task completes
    worker_disable_rate_limits=False,
    task_default_retry_delay=60,  # Retry after 1 minute
    task_max_retries=3,
)

logger.info("✓ Celery configured")

