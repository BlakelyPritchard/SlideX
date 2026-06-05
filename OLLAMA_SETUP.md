# Ollama + PaddleOCR Setup Guide

This guide will help you set up SlideX with **Ollama** (open-source LLM) and **PaddleOCR** for completely free, local AI tagging.

## 🎯 Why Ollama + PaddleOCR?

- ✅ **100% Free** - No API costs
- ✅ **Privacy** - All processing happens locally
- ✅ **No Rate Limits** - Process unlimited slides
- ✅ **High Quality** - Combines vision AI with OCR for best results
- ✅ **Offline Capable** - Works without internet

---

## 📋 Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8GB | 16GB+ |
| **GPU** | None (CPU works) | NVIDIA GPU with 8GB+ VRAM |
| **Storage** | 10GB free | 20GB+ free |
| **OS** | macOS, Linux, Windows | Any |

**Note:** LLaVA 7B model is ~4.5GB. With GPU, tagging is fast. CPU-only works but is slower.

---

## 🚀 Installation Steps

### Step 1: Install Ollama

#### macOS / Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Windows:
Download from: https://ollama.com/download/windows

### Step 2: Pull the LLaVA Model

```bash
# Pull the default LLaVA model (7B - recommended)
ollama pull llava

# OR for better quality (requires more VRAM):
ollama pull llava:13b

# OR for lower resource usage:
ollama pull llava:7b
```

**Wait for download to complete** (~4.5GB for 7B model)

### Step 3: Verify Ollama is Running

```bash
# Check if Ollama is running
ollama list

# You should see llava in the list
```

### Step 4: Install Python Dependencies

```bash
cd SlideX/backend

# Activate your virtual environment first
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install Ollama and PaddleOCR
pip install ollama==0.1.6
pip install paddleocr==2.7.3
pip install paddlepaddle==3.0.0

# If you have NVIDIA GPU, install GPU version instead:
# pip install paddlepaddle-gpu==3.0.0
```

### Step 5: Configure SlideX

Edit your `.env` file:

```bash
# Open .env file
nano backend/.env  # or use your preferred editor
```

Add these settings:

```env
# Enable Ollama
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava
USE_OCR=true

# Disable cloud APIs (optional - keeps them as fallback)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
WATSONX_IAM_API_KEY=
```

### Step 6: Test the Setup

```bash
# Start the backend
cd backend
uvicorn app.main:app --reload

# In another terminal, test Ollama directly:
ollama run llava "Describe this image" --image /path/to/test/image.png
```

---

## 🎨 How It Works

### The Pipeline

```
PowerPoint Slide
    ↓
1. Extract slide as image (LibreOffice)
    ↓
2. OCR text extraction (PaddleOCR)
    ↓
3. Vision analysis (LLaVA via Ollama)
    ↓
4. Combined analysis → Tags
```

### What Each Component Does

1. **PaddleOCR**: Extracts text from slide images
   - Handles small text, charts, labels
   - Works with multiple languages
   - Very accurate for presentation slides

2. **LLaVA (via Ollama)**: Analyzes slide visually
   - Understands layout and structure
   - Identifies charts, diagrams, images
   - Generates contextual tags

3. **Combined**: Best of both worlds
   - OCR provides precise text
   - LLaVA provides visual context
   - Together = highly accurate tagging

---

## ⚙️ Configuration Options

### Model Selection

Edit `backend/.env`:

```env
# Default (balanced)
OLLAMA_MODEL=llava

# Better quality (needs more VRAM)
OLLAMA_MODEL=llava:13b

# Faster/lighter (less accurate)
OLLAMA_MODEL=llava:7b
```

### OCR Settings

```env
# Enable/disable OCR
USE_OCR=true

# OCR only works when USE_OLLAMA=true
```

### Fallback Behavior

If Ollama fails, SlideX automatically falls back to:
1. WatsonX (if configured)
2. OpenAI (if configured)
3. Anthropic (if configured)
4. Basic keyword matching (always available)

---

## 🐛 Troubleshooting

### Issue: "Ollama connection refused"

**Solution:**
```bash
# Check if Ollama is running
ollama list

# If not, start it:
ollama serve
```

### Issue: "Model not found"

**Solution:**
```bash
# Pull the model again
ollama pull llava
```

### Issue: "Out of memory"

**Solutions:**
1. Use smaller model: `OLLAMA_MODEL=llava:7b`
2. Close other applications
3. Disable OCR: `USE_OCR=false`
4. Process fewer slides at once

### Issue: "Slow tagging speed"

**Solutions:**
1. **With GPU**: Install CUDA and GPU-enabled PaddlePaddle
2. **CPU only**: 
   - Use smaller model
   - Process slides in smaller batches
   - Disable OCR for faster (but less accurate) tagging

### Issue: "PaddleOCR errors"

**Solution:**
```bash
# Reinstall PaddleOCR
pip uninstall paddleocr paddlepaddle
pip install paddleocr==2.7.0.3 paddlepaddle==2.6.0
```

---

## 📊 Performance Comparison

| Setup | Speed (per slide) | Quality | Cost |
|-------|------------------|---------|------|
| **Ollama + OCR** | 3-10s (GPU) / 15-30s (CPU) | ⭐⭐⭐⭐⭐ | $0 |
| **WatsonX** | 2-5s | ⭐⭐⭐⭐⭐ | ~$0.01/slide |
| **OpenAI GPT-4** | 1-3s | ⭐⭐⭐⭐ | ~$0.02/slide |
| **Basic Keywords** | <1s | ⭐⭐ | $0 |

---

## 🔄 Switching Between AI Providers

You can easily switch between providers by changing `.env`:

### Use Ollama (Free, Local)
```env
USE_OLLAMA=true
WATSONX_IAM_API_KEY=
OPENAI_API_KEY=
```

### Use WatsonX (Enterprise)
```env
USE_OLLAMA=false
WATSONX_IAM_API_KEY=your_key_here
WATSONX_PROJECT_ID=your_project_id
```

### Use OpenAI (Cloud)
```env
USE_OLLAMA=false
WATSONX_IAM_API_KEY=
OPENAI_API_KEY=your_key_here
```

---

## 🎓 Advanced: GPU Acceleration

### For NVIDIA GPUs:

```bash
# Install CUDA toolkit (if not already installed)
# Visit: https://developer.nvidia.com/cuda-downloads

# Install GPU-enabled PaddlePaddle
pip uninstall paddlepaddle
pip install paddlepaddle-gpu==2.6.0

# Verify GPU is detected
python -c "import paddle; print(paddle.device.get_device())"
```

### For Apple Silicon (M1/M2/M3):

```bash
# PaddlePaddle doesn't fully support Apple Silicon yet
# Use CPU version - still reasonably fast on M-series chips
pip install paddlepaddle==2.6.0
```

---

## 📝 Example Usage

### Upload and Tag Slides

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Upload PowerPoint file
4. Watch as Ollama + OCR automatically tags each slide
5. Search using generated tags!

### Expected Output

For a slide about "IBM Maximo Asset Management":

```json
{
  "client_painpoint": ["asset_management", "maintenance_optimization"],
  "client_type": ["enterprise", "manufacturing"],
  "software_type": ["Maximo", "EAM"],
  "software_function": ["asset_tracking", "predictive_maintenance"],
  "slide_type": ["feature_highlight"]
}
```

---

## 🆘 Need Help?

1. Check Ollama logs: `ollama logs`
2. Check SlideX backend logs in terminal
3. Verify model is downloaded: `ollama list`
4. Test Ollama directly: `ollama run llava "test"`

---

## 🎉 Success!

You now have a completely free, local AI tagging system for SlideX!

**Next Steps:**
- Upload your first presentation
- Review the generated tags
- Adjust `OLLAMA_MODEL` if needed for your hardware
- Share with your team!