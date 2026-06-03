# Environment Configuration Guide (.env file)

This guide will walk you through setting up your `.env` file step-by-step.

## Step 1: Create the .env File

```bash
# Navigate to backend directory
cd SlideX/backend

# Copy the example file
cp .env.example .env
```

Now you have a `.env` file that you need to edit.

## Step 2: Open .env File in VS Code

```bash
# Open in VS Code
code .env
```

Or in VS Code:
1. Click on the `backend` folder in the sidebar
2. Find the `.env` file
3. Click to open it

## Step 3: Configure Database URL

### Find Your PostgreSQL Credentials

**Default PostgreSQL setup:**
- Username: `postgres` (or your macOS username)
- Password: Usually empty or `postgres`
- Host: `localhost`
- Port: `5432`
- Database: `slidex`

**To check your PostgreSQL username:**
```bash
whoami
# This is often your PostgreSQL username on macOS
```

### Update DATABASE_URL

In your `.env` file, find this line:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/slidex
```

**Replace with your actual credentials:**

**Example 1 - No password (common on macOS):**
```env
DATABASE_URL=postgresql://blakelypritchard@localhost:5432/slidex
```

**Example 2 - With password:**
```env
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/slidex
```

**Example 3 - Default postgres user:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/slidex
```

### Test Your Database Connection

```bash
# Try connecting with psql
psql -U blakelypritchard -d slidex
# Or
psql -U postgres -d slidex

# If it connects, your DATABASE_URL is correct!
# Type \q to quit
```

## Step 4: Get an AI API Key

You need **either** OpenAI **or** Anthropic (not both required).

### Option A: OpenAI (Recommended for beginners)

1. **Go to:** https://platform.openai.com/signup
2. **Sign up** for an account (free to start)
3. **Add payment method** (required, but you get $5 free credit)
4. **Create API key:**
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Give it a name: "SlideX"
   - Copy the key (starts with `sk-...`)
   - **IMPORTANT:** Save it somewhere safe - you can't see it again!

5. **Add to .env file:**
```env
OPENAI_API_KEY=sk-proj-abc123yourkey456here789
```

### Option B: Anthropic (Claude)

1. **Go to:** https://console.anthropic.com/
2. **Sign up** for an account
3. **Add payment method** (required)
4. **Create API key:**
   - Go to Settings → API Keys
   - Click "Create Key"
   - Copy the key (starts with `sk-ant-...`)

5. **Add to .env file:**
```env
ANTHROPIC_API_KEY=sk-ant-abc123yourkey456here789
```

## Step 5: Your Complete .env File

Here's what your final `.env` file should look like:

```env
# Database Configuration
DATABASE_URL=postgresql://blakelypritchard@localhost:5432/slidex

# AI API Keys (use one)
OPENAI_API_KEY=sk-proj-your-actual-key-here
# ANTHROPIC_API_KEY=

# Application Settings (keep these as-is for development)
APP_ENV=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# File Upload Settings (keep defaults)
MAX_UPLOAD_SIZE=50000000
UPLOAD_DIR=./uploads
SLIDES_DIR=./slides
THUMBNAILS_DIR=./thumbnails

# CORS Settings (keep defaults)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Server Settings (keep defaults)
HOST=0.0.0.0
PORT=8000
```

## Step 6: Verify Your Configuration

### Check Database Connection

```bash
# In terminal
cd SlideX/backend
source venv/bin/activate
python3 -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

This should print your database URL without errors.

### Check API Key

```bash
python3 -c "from app.core.config import settings; print('OpenAI key set:', bool(settings.OPENAI_API_KEY))"
```

Should print: `OpenAI key set: True`

## Common Issues

### Issue: "Connection refused" when starting server
**Problem:** Database URL is wrong or PostgreSQL isn't running

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# If not running, start it:
brew services start postgresql@15
# Or if using Postgres.app, just open the app
```

### Issue: "Invalid API key"
**Problem:** API key is incorrect or not set

**Solution:**
1. Double-check you copied the entire key
2. Make sure there are no extra spaces
3. Verify the key works at https://platform.openai.com/playground

### Issue: "Database does not exist"
**Problem:** You haven't created the `slidex` database yet

**Solution:**
```bash
createdb slidex
# Or
psql -U postgres
CREATE DATABASE slidex;
\q
```

## Security Notes

⚠️ **IMPORTANT:**
- Never commit your `.env` file to Git (it's already in .gitignore)
- Never share your API keys publicly
- Change SECRET_KEY in production
- Keep your API keys secure

## What Each Setting Does

| Setting | Purpose | Example |
|---------|---------|---------|
| DATABASE_URL | Connects to PostgreSQL | `postgresql://user:pass@localhost:5432/slidex` |
| OPENAI_API_KEY | Enables AI tagging with GPT | `sk-proj-...` |
| ANTHROPIC_API_KEY | Alternative AI (Claude) | `sk-ant-...` |
| DEBUG | Shows detailed errors | `True` for development |
| SECRET_KEY | Secures sessions | Change in production |
| MAX_UPLOAD_SIZE | Max file size (bytes) | `50000000` = 50MB |
| ALLOWED_ORIGINS | CORS for frontend | `http://localhost:5173` |

## Next Steps

Once your `.env` is configured:

1. ✅ Create the database: `createdb slidex`
2. ✅ Start the server: `uvicorn app.main:app --reload`
3. ✅ Test at: http://localhost:8000/docs

---

**Need help?** Check the QUICKSTART.md or README.md for more details!