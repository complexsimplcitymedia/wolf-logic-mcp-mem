#!/usr/bin/env python3
"""
Wolf-Logic Job Agent - AMD ROCM Alternative Implementation
Simplified async job processing with AMD GPU support
"""

import os
import asyncio
import torch
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= AMD GPU Detection =============

@dataclass
class GPUInfo:
    """AMD GPU Information"""
    available: bool = False
    name: str = "CPU"
    vram_gb: float = 0.0
    compute_capability: tuple = (0, 0)
    device_id: int = 0

def detect_amd_gpu() -> GPUInfo:
    """Detect AMD GPU with ROCM"""
    try:
        if torch.cuda.is_available():
            return GPUInfo(
                available=True,
                name=torch.cuda.get_device_name(0),
                vram_gb=torch.cuda.get_device_properties(0).total_memory / 1e9,
                compute_capability=torch.cuda.get_device_capability(0),
                device_id=0
            )
    except Exception as e:
        logger.warning(f"GPU detection failed: {e}")

    return GPUInfo()

# ============= Async Ollama Client =============

class AsyncOllamaClient:
    """Async Ollama client for AMD ROCM"""

    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3.2:latest"):
        self.host = host
        self.model = model
        self.gpu_info = detect_amd_gpu()

        # Setup PyTorch device
        self.device = torch.device("cuda" if self.gpu_info.available else "cpu")

        logger.info(f"🔴 AMD ROCM Client Initialized")
        logger.info(f"  Host: {self.host}")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Device: {self.device}")
        logger.info(f"  GPU: {self.gpu_info.name}")
        logger.info(f"  VRAM: {self.gpu_info.vram_gb:.2f} GB")

    async def generate(self, prompt: str, system: str = None, **kwargs) -> str:
        """Generate response from Ollama"""
        try:
            from ollama import AsyncClient

            client = AsyncClient(host=self.host)

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat(
                model=self.model,
                messages=messages,
                **kwargs
            )

            return response['message']['content']

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"Error: {str(e)}"

    async def stream_generate(self, prompt: str, system: str = None):
        """Stream response from Ollama"""
        try:
            from ollama import AsyncClient

            client = AsyncClient(host=self.host)

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            async for chunk in await client.chat(
                model=self.model,
                messages=messages,
                stream=True
            ):
                yield chunk['message']['content']

        except Exception as e:
            logger.error(f"Stream failed: {e}")
            yield f"Error: {str(e)}"

# ============= Job Queue =============

class JobQueue:
    """Simple async job queue for inference tasks"""

    def __init__(self, max_workers: int = 4):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.max_workers = max_workers
        self.results: Dict[str, Any] = {}
        self.running = False

    async def add_job(self, job_id: str, prompt: str, **kwargs):
        """Add job to queue"""
        await self.queue.put({
            "id": job_id,
            "prompt": prompt,
            "timestamp": datetime.now().isoformat(),
            "kwargs": kwargs
        })
        logger.info(f"Job {job_id} added to queue")

    async def worker(self, worker_id: int, client: AsyncOllamaClient):
        """Worker process for jobs"""
        logger.info(f"Worker {worker_id} started")

        while self.running:
            try:
                job = await asyncio.wait_for(self.queue.get(), timeout=1.0)

                logger.info(f"Worker {worker_id} processing job {job['id']}")

                # Run inference
                start_time = datetime.now()
                result = await client.generate(job['prompt'], **job.get('kwargs', {}))
                elapsed = (datetime.now() - start_time).total_seconds()

                # Store result
                self.results[job['id']] = {
                    "result": result,
                    "elapsed": elapsed,
                    "completed": datetime.now().isoformat()
                }

                logger.info(f"Job {job['id']} completed in {elapsed:.2f}s")

                self.queue.task_done()

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")

    async def start(self, client: AsyncOllamaClient):
        """Start workers"""
        self.running = True
        workers = [
            asyncio.create_task(self.worker(i, client))
            for i in range(self.max_workers)
        ]
        await asyncio.gather(*workers)

    def stop(self):
        """Stop workers"""
        self.running = False

# ============= Main Job Agent =============

async def main():
    """Main async job agent"""

    # Environment setup
    os.environ.setdefault("HIP_VISIBLE_DEVICES", "0")
    os.environ.setdefault("ROCM_HOME", "/opt/rocm")

    # Initialize client
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

    client = AsyncOllamaClient(host=ollama_host, model=ollama_model)

    # Test single generation
    logger.info("\n=== Testing Single Generation ===")
    response = await client.generate(
        prompt="Explain quantum computing in one sentence.",
        system="You are a physics teacher."
    )
    logger.info(f"Response: {response}")

    # Test streaming
    logger.info("\n=== Testing Streaming ===")
    print("Stream: ", end="", flush=True)
    async for chunk in client.stream_generate(
        prompt="What is machine learning?",
        system="You are a helpful AI assistant."
    ):
        print(chunk, end="", flush=True)
    print("\n")

    # Test job queue
    logger.info("\n=== Testing Job Queue ===")
    queue = JobQueue(max_workers=2)

    # Add jobs
    for i in range(5):
        await queue.add_job(
            job_id=f"job_{i}",
            prompt=f"What is the number {i}?",
            system="You are a math teacher."
        )

    # Process jobs (run for 10 seconds)
    try:
        await asyncio.wait_for(queue.start(client), timeout=10.0)
    except asyncio.TimeoutError:
        queue.stop()

    # Show results
    logger.info("\n=== Job Results ===")
    for job_id, result in queue.results.items():
        logger.info(f"{job_id}: {result['elapsed']:.2f}s - {result['result'][:50]}...")

if __name__ == "__main__":
    asyncio.run(main())

