# Getting Started with SlideX - Quick Setup

Your OpenAI API key is configured! Let's get the backend running.

## Step 1: Create the Database

```bash
# Create PostgreSQL database
createdb slidex
```

If that doesn't work, try:
```bash
psql -U postgres
CREATE DATABASE slidex;
\q
```

## Step 2: Set Up Backend

```bash
# Navigate to backend directory
cd ~/Desktop/SlideX/backend

# Run the automated setup script
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Set up necessary directories

## Step 3: Start the Server

```bash
# Make sure you're in the backend directory
cd ~/Desktop/SlideX/backend

# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload
```

You should see:
```
✅ Database initialized
🚀 SlideX API running on http://0.0.0.0:8000
```

## Step 4: Test the API

Open your browser and go to:
**http://localhost:8000/docs**

You'll see the interactive API documentation where you can:
- Upload PowerPoint files
- Search for slides
- View all slides
- Test all endpoints

## Step 5: Upload Your First Presentation

### Option A: Using the API Docs (Easiest)

1. Go to http://localhost:8000/docs
2. Click on `POST /api/slides/upload`
3. Click "Try it out"
4. Click "Choose File" and select a .pptx file
5. Click "Execute"
6. Watch as it processes and tags your slides!

### Option B: Using curl

```bash
curl -X POST "http://localhost:8000/api/slides/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/presentation.pptx"
```

## Step 6: Search for Slides

### Search by keyword:
```bash
curl "http://localhost:8000/api/search/?q=analytics"
```

### Get all slides:
```bash
curl "http://localhost:8000/api/slides/"
```

### Get all tags:
```bash
curl "http://localhost:8000/api/tags/"
```

## Troubleshooting

### "Command not found: createdb"
PostgreSQL might not be in your PATH. Try:
```bash
/Applications/Postgres.app/Contents/Versions/latest/bin/createdb slidex
```

Or use psql directly (see Step 1 alternative)

### "Port 8000 already in use"
Kill the process:
```bash
lsof -ti:8000 | xargs kill -9
```

### "Module not found" errors
Reinstall dependencies:
```bash
cd ~/Desktop/SlideX/backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### "Database connection failed"
Check PostgreSQL is running:
```bash
pg_isready
```

If not running:
```bash
brew services start postgresql@15
# Or open Postgres.app
```

## What Happens When You Upload?

1. **Upload**: File is saved temporarily
2. **Extract**: Each slide is extracted from the PowerPoint
3. **Convert**: Slides are converted to images (thumbnails created)
4. **Analyze**: Text content is extracted from each slide
5. **AI Tagging**: OpenAI analyzes the content and generates tags in 4 categories:
   - Client Painpoints (e.g., "data security", "scalability")
   - Client Type (e.g., "enterprise", "SMB")
   - Software Type (e.g., "CRM", "analytics")
   - Software Function (e.g., "reporting", "integration")
6. **Store**: Slides and tags are saved to the database
7. **Done**: You can now search for these slides!

## Next Steps

1. ✅ Upload 5-10 test presentations
2. ✅ Try different search queries
3. ✅ Check the tags that were generated
4. ✅ Share with your team to test
5. 🔄 Start building the frontend (coming next!)

## Useful Commands

```bash
# Start server
cd ~/Desktop/SlideX/backend && source venv/bin/activate && uvicorn app.main:app --reload

# Check if server is running
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Check database
psql -d slidex -c "SELECT COUNT(*) FROM slides;"
```

## API Endpoints Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API docs |
| `/api/slides/upload` | POST | Upload PowerPoint |
| `/api/slides/` | GET | Get all slides |
| `/api/slides/{id}` | GET | Get specific slide |
| `/api/slides/{id}` | DELETE | Delete slide |
| `/api/tags/` | GET | Get all tags |
| `/api/tags/categories` | GET | Get tag categories |
| `/api/search/` | GET | Search slides |
| `/api/search/export` | POST | Export selected slides |

## Your Configuration

✅ **OpenAI API**: Configured and ready
✅ **Database**: PostgreSQL (slidex)
✅ **Backend**: Python/FastAPI
✅ **Port**: 8000

---

**Ready to go!** Run the setup script and start uploading slides! 🚀