import torch
import mlflow
import mlflow.pytorch
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= AMD ROCM Configuration =============

def setup_rocm():
    """Configure PyTorch for AMD ROCM GPUs"""

    # Check if ROCM is available
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        logger.info(f"✓ GPU Detected: {device_name}")

        # Verify ROCM
        if "MI" in device_name or "Radeon" in device_name:
            logger.info("✓ AMD ROCM GPU detected")
            logger.info(f"  CUDA Compute Capability: {torch.cuda.get_device_capability(0)}")
            logger.info(f"  Total VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
            return True
    else:
        logger.warning("⚠ No GPU detected - falling back to CPU")
        return False

# Setup ROCM
gpu_available = setup_rocm()

# ============= MLflow AutoLog for PyTorch =============

# Enable MLflow autologging for PyTorch
mlflow.pytorch.autolog(
    log_models=True,
    disable=False,
    exclusive=False,
    disable_for_unsupported_versions=False,
    silent=False
)

logger.info("✓ MLflow PyTorch autolog enabled")
