# 🚀 Quick Start: Test Ollama with SlideX

This guide will get you up and running with Ollama in **under 10 minutes**.

---

## Step 1: Install Ollama (2 minutes)

### macOS:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows:
Download and install from: https://ollama.com/download/windows

### Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

## Step 2: Download LLaVA Model (3-5 minutes)

```bash
# This downloads the LLaVA vision model (~4.5GB)
ollama pull llava
```

**Wait for download to complete.** You'll see progress bars.

---

## Step 3: Install Python Dependencies (1 minute)

```bash
cd SlideX/backend

# Activate your virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install Ollama + OCR packages
pip install ollama==0.1.6
pip install paddleocr==2.7.3
pip install paddlepaddle==3.0.0
```

---

## Step 4: Configure SlideX (30 seconds)

Edit `backend/.env` file:

```bash
# Open in your editor
nano backend/.env
# OR
code backend/.env
```

**Add or update these lines:**

```env
# Enable Ollama
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava
USE_OCR=true

# Disable cloud APIs (optional - they'll be used as fallback if Ollama fails)
WATSONX_IAM_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

**Save the file.**

---

## Step 5: Test Ollama (30 seconds)

```bash
# Test that Ollama is working
ollama run llava "Describe this as a test"
```

You should see a response from the model. Press `Ctrl+D` to exit.

---

## Step 6: Start SlideX (1 minute)

### Terminal 1 - Backend:
```bash
cd SlideX/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

### Terminal 2 - Frontend:
```bash
cd SlideX/frontend
npm run dev
```

---

## Step 7: Upload and Tag! 🎉

1. Open browser: http://localhost:5173
2. Click "Upload Presentation"
3. Select a PowerPoint file
4. Watch as Ollama automatically tags each slide!

---

## 🎯 What to Expect

### First Slide Processing:
- **Time:** 5-15 seconds (first run is slower)
- **What happens:**
  1. Slide converted to image
  2. PaddleOCR extracts text
  3. LLaVA analyzes the image
  4. Tags generated and saved

### Subsequent Slides:
- **Time:** 3-10 seconds per slide (faster after warmup)

### You'll See Tags Like:
```json
{
  "client_painpoint": ["cost_reduction", "efficiency"],
  "client_type": ["enterprise"],
  "software_type": ["analytics"],
  "software_function": ["reporting", "dashboard"],
  "slide_type": ["feature_highlight"]
}
```

---

## 🐛 Troubleshooting

### "Connection refused" error:

**Solution:** Start Ollama manually:
```bash
ollama serve
```

### "Model not found" error:

**Solution:** Pull the model again:
```bash
ollama pull llava
```

### Slow performance:

**Solutions:**
- Close other applications
- Use smaller model: `OLLAMA_MODEL=llava:7b`
- Disable OCR temporarily: `USE_OCR=false`

### PaddleOCR errors:

**Solution:** Reinstall:
```bash
pip uninstall paddleocr paddlepaddle
pip install paddleocr==2.7.0.3 paddlepaddle==2.6.0
```

---

## 📊 Performance Tips

### For Best Speed:
1. **GPU:** If you have NVIDIA GPU, install CUDA
2. **Model:** Use `llava:7b` (default, balanced)
3. **OCR:** Keep enabled for best accuracy

### For Lower Resource Usage:
1. **Model:** Use `llava:7b` (lighter)
2. **OCR:** Disable with `USE_OCR=false`
3. **Batch:** Upload smaller presentations first

---

## ✅ Verification Checklist

Before uploading slides, verify:

- [ ] Ollama installed: `ollama --version`
- [ ] LLaVA downloaded: `ollama list` (should show llava)
- [ ] Ollama running: `curl http://localhost:11434/api/tags`
- [ ] Python packages installed: `pip list | grep ollama`
- [ ] .env configured: `USE_OLLAMA=true`
- [ ] Backend running: http://localhost:8000/docs
- [ ] Frontend running: http://localhost:5173

---

## 🎓 Next Steps

Once you've successfully tagged slides:

1. **Search:** Use the search bar to find slides by keywords
2. **Filter:** Use tag filters to narrow results
3. **Export:** Select slides and export to new PowerPoint
4. **Share:** Show your team the free AI tagging!

---

## 💡 Pro Tips

1. **First Upload:** Start with a small deck (5-10 slides) to test
2. **Monitor:** Watch terminal output to see tagging progress
3. **Adjust:** If tags aren't accurate, try different prompts in `ai_tagger.py`
4. **GPU:** For faster processing, install GPU-enabled PaddlePaddle

---

## 🆘 Need Help?

1. Check logs in terminal where backend is running
2. Test Ollama directly: `ollama run llava "test"`
3. Verify .env settings: `cat backend/.env | grep OLLAMA`
4. See full guide: `OLLAMA_SETUP.md`

---

## 🎉 Success!

You're now using **100% free, local AI** to tag your slides!

**No API costs. No rate limits. Complete privacy.** 🚀