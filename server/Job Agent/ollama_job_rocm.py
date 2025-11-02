#!/usr/bin/env python3
"""
Wolf-Logic Job Agent - AMD ROCM GPU Support with PyTorch
Handles Ollama inference with AMD GPUs (ROCM)
No MLflow - Pure PyTorch inference
"""

import os
import torch
import logging
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= AMD ROCM Configuration =============

class ROCMConfig:
    """Manage AMD ROCM GPU configuration"""

    def __init__(self):
        self.device = None
        self.gpu_available = False
        self.device_name = None
        self.vram = None
        self.setup_rocm()

    def setup_rocm(self):
        """Configure PyTorch for AMD ROCM"""
        try:
            # Check CUDA availability (ROCM uses CUDA API)
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                self.gpu_available = True
                self.device_name = torch.cuda.get_device_name(0)
                self.vram = torch.cuda.get_device_properties(0).total_memory / 1e9

                logger.info(f"✓ AMD GPU Detected: {self.device_name}")
                logger.info(f"  Device: {self.device}")
                logger.info(f"  VRAM: {self.vram:.2f} GB")
                logger.info(f"  Compute Capability: {torch.cuda.get_device_capability(0)}")
            else:
                self.device = torch.device("cpu")
                logger.warning("⚠ No GPU detected - using CPU")
                logger.warning("  To use AMD GPU: export HIP_VISIBLE_DEVICES=0")
                logger.warning("  Or install ROCm drivers")
        except Exception as e:
            logger.error(f"Error setting up ROCM: {e}")
            self.device = torch.device("cpu")

    def get_device(self):
        """Return torch device (cuda or cpu)"""
        return self.device

    def is_gpu_available(self):
        """Check if GPU is available"""
        return self.gpu_available


# ============= Ollama Configuration =============

class OllamaJobAgent:
    """Job agent for Ollama inference with ROCM support"""

    def __init__(self, ollama_host: str = None, model: str = "llama3.2:latest"):
        """
        Initialize Ollama Job Agent

        Args:
            ollama_host: Ollama server URL (default: localhost:11434)
            model: Model name to use
        """
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model
        self.rocm_config = ROCMConfig()

        # Import OpenAI client for Ollama API
        try:
            from ollama import OpenAI
            self.client = OpenAI(
                base_url=f"{self.ollama_host}/v1",
                api_key="ollama"
            )
            logger.info(f"✓ Ollama client initialized")
            logger.info(f"  Host: {self.ollama_host}")
            logger.info(f"  Model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            self.client = None

    def chat(self, messages: list, system_prompt: str = None, **kwargs) -> str:
        """
        Send chat request to Ollama

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            **kwargs: Additional arguments for the API call

        Returns:
            Response text from model
        """
        if not self.client:
            return "Error: Ollama client not initialized"

        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return f"Error: {str(e)}"

    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        return {
            "device": str(self.rocm_config.device),
            "gpu_available": self.rocm_config.gpu_available,
            "device_name": self.rocm_config.device_name,
            "vram_gb": self.rocm_config.vram,
            "ollama_host": self.ollama_host,
            "model": self.model
        }


# ============= Environment Variables for AMD =============

def setup_amd_environment():
    """Setup environment variables for AMD ROCM"""

    # ROCm environment variables
    rocm_vars = {
        "HSA_OVERRIDE_GFX_VERSION": os.getenv("HSA_OVERRIDE_GFX_VERSION", ""),
        "HIP_VISIBLE_DEVICES": os.getenv("HIP_VISIBLE_DEVICES", "0"),
        "HIP_DEVICE_ORDER": os.getenv("HIP_DEVICE_ORDER", "PCI"),
        "ROCM_HOME": os.getenv("ROCM_HOME", "/opt/rocm"),
        "LD_LIBRARY_PATH": os.getenv("LD_LIBRARY_PATH", "") + ":/opt/rocm/lib",
    }

    # Log environment
    logger.info("AMD ROCM Environment:")
    for key, value in rocm_vars.items():
        if value:
            logger.info(f"  {key}={value}")
            os.environ[key] = value


# ============= Main Job Agent =============

if __name__ == "__main__":
    # Setup AMD environment
    setup_amd_environment()

    # Initialize agent
    agent = OllamaJobAgent(
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    )

    # Print device info
    logger.info("Device Information:")
    for key, value in agent.get_device_info().items():
        logger.info(f"  {key}: {value}")

    # Example chat
    logger.info("\nTesting Ollama inference...")
    response = agent.chat(
        messages=[
            {"role": "user", "content": "Why is the sky blue?"}
        ],
        system_prompt="You are a science teacher."
    )
    logger.info(f"Response: {response}")

