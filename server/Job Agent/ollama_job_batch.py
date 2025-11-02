#!/usr/bin/env python3
"""
Wolf-Logic Job Agent - AMD ROCM Batch Processing
High-throughput batch inference for AMD GPUs
"""

import os
import torch
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= AMD ROCM Setup =============

class ROCMBatchProcessor:
    """Batch processor optimized for AMD ROCM"""

    def __init__(self):
        self.device = self._setup_device()
        self.device_info = self._get_device_info()
        self._log_device_info()

    def _setup_device(self) -> torch.device:
        """Setup PyTorch device"""
        if torch.cuda.is_available():
            return torch.device("cuda:0")
        return torch.device("cpu")

    def _get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        if self.device.type == "cuda":
            return {
                "name": torch.cuda.get_device_name(0),
                "vram_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
                "compute": torch.cuda.get_device_capability(0),
                "available": True
            }
        return {"name": "CPU", "available": False}

    def _log_device_info(self):
        """Log device information"""
        logger.info("🔴 AMD ROCM Batch Processor")
        logger.info(f"  Device: {self.device}")
        logger.info(f"  Name: {self.device_info.get('name', 'CPU')}")
        if self.device_info.get('available'):
            logger.info(f"  VRAM: {self.device_info['vram_gb']:.2f} GB")
            logger.info(f"  Compute: {self.device_info['compute']}")

# ============= Batch Job Definition =============

@dataclass
class BatchJob:
    """Single batch job"""
    id: str
    prompt: str
    system: str = "You are a helpful AI assistant."
    model: str = "llama3.2:latest"
    temperature: float = 0.7
    max_tokens: int = 512
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Results
    result: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def elapsed(self) -> float:
        """Calculate elapsed time"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def status(self) -> str:
        """Get job status"""
        if self.error:
            return "error"
        if self.result:
            return "completed"
        if self.start_time:
            return "running"
        return "pending"

# ============= Batch Inference Engine =============

class BatchInferenceEngine:
    """Batch inference engine for Ollama"""

    def __init__(self, ollama_host: str = "http://localhost:11434", max_workers: int = 4):
        self.ollama_host = ollama_host
        self.max_workers = max_workers
        self.processor = ROCMBatchProcessor()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def _process_single_job(self, job: BatchJob) -> BatchJob:
        """Process a single job"""
        job.start_time = datetime.now()

        try:
            from ollama import Client

            client = Client(host=self.ollama_host)

            messages = [
                {"role": "system", "content": job.system},
                {"role": "user", "content": job.prompt}
            ]

            response = client.chat(
                model=job.model,
                messages=messages,
                options={
                    "temperature": job.temperature,
                    "num_predict": job.max_tokens
                }
            )

            job.result = response['message']['content']
            logger.info(f"✓ Job {job.id} completed")

        except Exception as e:
            job.error = str(e)
            logger.error(f"✗ Job {job.id} failed: {e}")

        finally:
            job.end_time = datetime.now()

        return job

    def process_batch(self, jobs: List[BatchJob]) -> List[BatchJob]:
        """Process batch of jobs in parallel"""
        logger.info(f"Processing batch of {len(jobs)} jobs with {self.max_workers} workers")

        futures = {
            self.executor.submit(self._process_single_job, job): job
            for job in jobs
        }

        completed_jobs = []
        for future in as_completed(futures):
            job = future.result()
            completed_jobs.append(job)

        return completed_jobs

    def get_batch_stats(self, jobs: List[BatchJob]) -> Dict[str, Any]:
        """Get batch processing statistics"""
        total = len(jobs)
        completed = sum(1 for j in jobs if j.status == "completed")
        failed = sum(1 for j in jobs if j.status == "error")
        avg_time = sum(j.elapsed for j in jobs if j.elapsed > 0) / max(completed, 1)

        return {
            "total_jobs": total,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total * 100) if total > 0 else 0,
            "avg_time_seconds": avg_time,
            "throughput_jobs_per_sec": completed / avg_time if avg_time > 0 else 0
        }

    def shutdown(self):
        """Shutdown executor"""
        self.executor.shutdown(wait=True)

# ============= Example Usage =============

def run_batch_example():
    """Example batch processing"""

    # Initialize engine
    engine = BatchInferenceEngine(
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        max_workers=4
    )

    # Create batch jobs
    batch_jobs = [
        BatchJob(
            id=f"batch_{i}",
            prompt=f"What is {i} + {i}?",
            system="You are a math teacher.",
            model=os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        )
        for i in range(10)
    ]

    # Process batch
    logger.info("\n=== Starting Batch Processing ===")
    start_time = datetime.now()

    completed_jobs = engine.process_batch(batch_jobs)

    total_time = (datetime.now() - start_time).total_seconds()

    # Show results
    logger.info("\n=== Batch Results ===")
    for job in completed_jobs:
        status_icon = "✓" if job.status == "completed" else "✗"
        logger.info(f"{status_icon} {job.id}: {job.elapsed:.2f}s - {job.status}")
        if job.result:
            logger.info(f"   Result: {job.result[:100]}...")

    # Show stats
    stats = engine.get_batch_stats(completed_jobs)
    logger.info("\n=== Batch Statistics ===")
    logger.info(f"Total Jobs: {stats['total_jobs']}")
    logger.info(f"Completed: {stats['completed']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Success Rate: {stats['success_rate']:.1f}%")
    logger.info(f"Avg Time: {stats['avg_time_seconds']:.2f}s")
    logger.info(f"Throughput: {stats['throughput_jobs_per_sec']:.2f} jobs/sec")
    logger.info(f"Total Time: {total_time:.2f}s")

    # Cleanup
    engine.shutdown()

if __name__ == "__main__":
    # Setup AMD environment
    os.environ.setdefault("HIP_VISIBLE_DEVICES", "0")
    os.environ.setdefault("ROCM_HOME", "/opt/rocm")

    run_batch_example()

