# 🔴 AMD ROCM Job Agent - Wolf-Logic MCP

## AMD GPU Support (No Nvidia Bullshit)

This is the Job Agent optimized for **AMD GPUs with ROCM** (Radeon Open Compute).

### Supported AMD GPUs:
- Radeon RX 7900 XTX
- Radeon RX 7900 XT
- Radeon RX 6900 XT
- Radeon RX 6800 XT
- MI300X, MI300, MI250X, MI250
- FirePro GPUs

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure AMD ROCM drivers are installed:
```bash
# For Ubuntu/Debian
sudo apt-get install rocm-core rocm-dkms rocm-libs rocm-dev

# Verify installation
rocminfo
```

### 2. Launch Job Agent with Ollama
```bash
cd /mnt/s/wolf-logic-mcp

# Start Job Agent, Ollama, and MLflow
docker compose -f docker-compose.job-agent.yml up -d
```

### 3. Access Services
- **Ollama API**: http://localhost:11434
- **MLflow Tracking**: http://localhost:5000

---

## 📋 Environment Variables

Set these before running:

```bash
# GPU Configuration
export HIP_VISIBLE_DEVICES=0              # Which GPU to use (0, 1, 2, ...)
export HIP_DEVICE_ORDER=PCI               # Device ordering
export ROCM_HOME=/opt/rocm                # ROCM installation path

# Ollama Configuration
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.2:latest

# MLflow Configuration
export MLFLOW_TRACKING_URI=http://localhost:5000
export MLFLOW_EXPERIMENT_NAME=wolf-logic-job-agent

# GPU Optimization
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
```

---

## 🔧 GPU Device Mounting

The Job Agent mounts GPU devices directly:
```yaml
devices:
  - /dev/kfd:/dev/kfd      # KFD (Kernel Fusion Driver)
  - /dev/dri:/dev/dri      # DRI (Direct Rendering Interface)
```

This allows PyTorch/Ollama to access AMD GPUs inside containers.

---

## 📊 MLflow Integration

Track experiments automatically:

```python
from ollama_job_rocm import OllamaJobAgent
import mlflow

agent = OllamaJobAgent()

with mlflow.start_run():
    response = agent.chat(
        messages=[{"role": "user", "content": "Test"}]
    )
    mlflow.log_metric("inference_latency", 0.5)
```

View results at: http://localhost:5000

---

## 🐳 Docker Commands

### View Job Agent Logs
```bash
docker compose -f docker-compose.job-agent.yml logs -f job-agent
```

### View Ollama Logs
```bash
docker compose -f docker-compose.job-agent.yml logs -f ollama
```

### Stop Job Agent
```bash
docker compose -f docker-compose.job-agent.yml down
```

### Stop & Remove Volumes
```bash
docker compose -f docker-compose.job-agent.yml down -v
```

---

## 🔍 Verify GPU Access

Check if GPU is detected:
```bash
docker compose -f docker-compose.job-agent.yml exec job-agent python3 -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

---

## 💡 Ollama Model Management

### Pull a model
```bash
docker compose -f docker-compose.job-agent.yml exec ollama ollama pull llama3.2
```

### List available models
```bash
docker compose -f docker-compose.job-agent.yml exec ollama ollama list
```

### Remove a model
```bash
docker compose -f docker-compose.job-agent.yml exec ollama ollama rm llama3.2
```

---

## 🎯 Performance Tips

1. **Maximize GPU Utilization**: Set `HIP_VISIBLE_DEVICES` to use all GPUs if available
2. **Memory Optimization**: Use quantized models (Q4, Q5) for better memory efficiency
3. **Batch Processing**: Process multiple requests together
4. **Model Caching**: Models are cached in `ollama_models` volume - reuse them

---

## ⚙️ Troubleshooting

### GPU Not Detected
```bash
# Check ROCM drivers
rocminfo

# Verify HIP detection
hipDeviceGetName

# Check Docker GPU access
docker run --rm --device /dev/kfd --device /dev/dri rocm/pytorch:latest rocminfo
```

### Ollama Connection Issues
```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# Check from inside container
docker compose -f docker-compose.job-agent.yml exec job-agent curl http://ollama:11434/api/tags
```

### VRAM Issues
```bash
# Monitor GPU memory
watch rocm-smi

# Use smaller models
export OLLAMA_MODEL=phi:latest  # Smaller, faster
```

---

## 📝 Files

- `ollama_job_rocm.py` - Main Job Agent with ROCM support
- `Dockerfile.rocm` - Container image with ROCM PyTorch
- `docker-compose.job-agent.yml` - Complete stack (Agent + Ollama + MLflow)
- `.env` - Environment configuration

---

## 🎬 Full AMD ROCM Stack

```
┌─────────────────────────────────────┐
│     Wolf-Logic Job Agent (AMD)      │
│   - PyTorch with ROCM               │
│   - Ollama client integration       │
└──────────────┬──────────────────────┘
               │
               │
          ┌────▼────┐
          │ Ollama  │
          │ (ROCM)  │
          └────┬────┘
               │
        ┌──────▼──────┐
        │  AMD GPUs   │
        │  KFD/DRI    │
        └─────────────┘
```

---

**Ready to run on pure AMD ROCM with PyTorch! 🔴**

