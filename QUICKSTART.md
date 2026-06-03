# SlideX Quick Start Guide 🚀

Get SlideX up and running in 10 minutes!

## Prerequisites Checklist

Before you begin, make sure you have:
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ PostgreSQL 15+ installed and running
- ✅ Git installed
- ✅ VS Code (or your preferred editor)
- ✅ OpenAI or Anthropic API key (get one at [platform.openai.com](https://platform.openai.com) or [console.anthropic.com](https://console.anthropic.com))

## Step 1: Clone and Open Project

```bash
# Navigate to Desktop (or your preferred location)
cd ~/Desktop

# Clone the repository
git clone https://github.com/BlakelyPritchard/SlideX.git

# Open in VS Code
cd SlideX
code .
```

## Step 2: Backend Setup (5 minutes)

```bash
# Open terminal in VS Code (Ctrl+` or Cmd+`)
cd backend

# Run the automated setup script
./setup.sh

# This script will:
# - Create virtual environment
# - Install all Python dependencies
# - Create .env file
# - Create necessary directories
```

## Step 3: Configure Environment

Edit `backend/.env` file:

```env
# Required: Database connection
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/slidex

# Required: AI API key (choose one)
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: Keep defaults for development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
```

## Step 4: Create Database

```bash
# Option 1: Using createdb command
createdb slidex

# Option 2: Using psql
psql -U postgres
CREATE DATABASE slidex;
\q
```

## Step 5: Start Backend Server

```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload

# You should see:
# ✅ Database initialized
# 🚀 SlideX API running on http://0.0.0.0:8000
```

**Test it:** Open http://localhost:8000/docs in your browser to see the API documentation!

## Step 6: Frontend Setup (Coming Soon)

The frontend will be set up in the next phase. For now, you can:
- Use the API directly via http://localhost:8000/docs
- Test with curl or Postman
- Build a simple HTML interface

## Quick Test

### Upload a PowerPoint File

```bash
# Using curl (replace with your actual .pptx file)
curl -X POST "http://localhost:8000/api/slides/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/presentation.pptx"
```

### Search for Slides

```bash
# Search by keyword
curl "http://localhost:8000/api/search/?q=analytics"

# Get all slides
curl "http://localhost:8000/api/slides/"

# Get all tags
curl "http://localhost:8000/api/tags/"
```

## Common Issues & Solutions

### Issue: "Command not found: createdb"
**Solution:** PostgreSQL is not in your PATH. Use psql instead or add PostgreSQL to PATH.

### Issue: "Port 8000 already in use"
**Solution:** 
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Issue: "Module not found" errors
**Solution:**
```bash
# Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Issue: Database connection failed
**Solution:**
1. Check PostgreSQL is running: `pg_isready`
2. Verify database exists: `psql -l | grep slidex`
3. Check DATABASE_URL in .env matches your PostgreSQL credentials

### Issue: AI tagging not working
**Solution:**
1. Verify API key is set in .env
2. Check API key is valid
3. The system will fall back to basic keyword matching if AI fails

## Next Steps

1. **Upload Test Data**: Upload 5-10 PowerPoint files to test the system
2. **Explore API**: Use the interactive docs at http://localhost:8000/docs
3. **Customize Tags**: Modify `backend/app/services/ai_tagger.py` to adjust tag categories
4. **Team Onboarding**: Share this guide with your team members

## Development Workflow

```bash
# Daily workflow
cd SlideX/backend
source venv/bin/activate
uvicorn app.main:app --reload

# In another terminal for frontend (when ready)
cd SlideX/frontend
npm run dev
```

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Project README**: See README.md for detailed information
- **Issues**: Open an issue on GitHub
- **Team**: Contact your team lead

## What's Next?

After the backend is running:
1. ✅ Backend API is working
2. 🔄 Frontend development (Week 5-6)
3. 🔄 Advanced features (Week 7-8)
4. 🔄 Testing and deployment

---

**Ready to build?** Start uploading slides and testing the search functionality! 🎉