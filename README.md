# SlideX 🎯

AI-powered slide repository for sales teams. Upload PowerPoint decks, automatically tag slides, and instantly find the perfect slides for your next client presentation.

## 🚀 Features

- **Smart Upload**: Upload PowerPoint files and automatically extract individual slides
- **AI Tagging**: Automatically categorize slides by:
  - Client Painpoints (data security, scalability, cost reduction, etc.)
  - Client Type (enterprise, SMB, startup)
  - Software Type (CRM, analytics, automation)
  - Software Function (reporting, integration, dashboard)
- **Powerful Search**: Find slides by keywords, tags, or categories
- **Quick Export**: Select slides and export as a new presentation
- **Team Collaboration**: Share and discover slides across your sales team

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- OpenAI or Anthropic API key (for AI tagging)

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/BlakelyPritchard/SlideX.git
cd SlideX
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your configuration:
# - Database URL
# - OpenAI or Anthropic API key
# - Other settings
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb slidex

# Or using psql:
psql -U postgres
CREATE DATABASE slidex;
\q

# Update DATABASE_URL in .env file:
# DATABASE_URL=postgresql://username:password@localhost:5432/slidex
```

### 4. Run Backend

```bash
# Make sure you're in the backend directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API will be available at:
# http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### 5. Frontend Setup

```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at:
# http://localhost:5173
```

## 📁 Project Structure

```
SlideX/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   │   ├── slides.py  # Slide upload & management
│   │   │   ├── tags.py    # Tag management
│   │   │   └── search.py  # Search functionality
│   │   ├── core/          # Core configuration
│   │   │   ├── config.py  # Settings
│   │   │   └── database.py # Database connection
│   │   ├── models/        # Database models
│   │   │   ├── slide.py   # Slide model
│   │   │   └── tag.py     # Tag model
│   │   ├── services/      # Business logic
│   │   │   ├── slide_processor.py # PowerPoint processing
│   │   │   └── ai_tagger.py       # AI tagging
│   │   └── main.py        # FastAPI application
│   ├── uploads/           # Temporary upload storage
│   ├── slides/            # Processed slide images
│   ├── thumbnails/        # Slide thumbnails
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment variables template
├── frontend/              # React frontend (to be created)
└── README.md
```

## 🔑 API Endpoints

### Slides
- `POST /api/slides/upload` - Upload PowerPoint file
- `GET /api/slides/` - Get all slides
- `GET /api/slides/{id}` - Get specific slide
- `DELETE /api/slides/{id}` - Delete slide

### Tags
- `GET /api/tags/` - Get all tags grouped by category
- `GET /api/tags/categories` - Get available categories
- `GET /api/tags/{id}/slides` - Get slides for a tag

### Search
- `GET /api/search/?q=keyword` - Search by text
- `GET /api/search/?tags=tag1&tags=tag2` - Filter by tags
- `GET /api/search/?categories=client_type` - Filter by category
- `POST /api/search/export` - Export selected slides

## 🎨 Usage Examples

### Upload a Presentation

```bash
curl -X POST "http://localhost:8000/api/slides/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@presentation.pptx"
```

### Search for Slides

```bash
# Search by keyword
curl "http://localhost:8000/api/search/?q=analytics"

# Filter by tags
curl "http://localhost:8000/api/search/?tags=enterprise&tags=CRM"

# Filter by category
curl "http://localhost:8000/api/search/?categories=client_type"
```

## 🔧 Configuration

Edit `backend/.env` to configure:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/slidex

# AI API (choose one)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Application
DEBUG=True
SECRET_KEY=your-secret-key

# File Upload
MAX_UPLOAD_SIZE=50000000  # 50MB

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🚀 Deployment

### Backend (Railway/Render)
1. Push code to GitHub
2. Connect repository to Railway/Render
3. Add environment variables
4. Deploy

### Frontend (Vercel)
1. Push code to GitHub
2. Connect repository to Vercel
3. Configure build settings
4. Deploy

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📝 Development Roadmap

### MVP (8 weeks)
- [x] Project setup
- [ ] Backend API implementation
- [ ] Frontend development
- [ ] AI tagging integration
- [ ] Search functionality
- [ ] Export feature
- [ ] Testing & deployment

### Future Enhancements
- User authentication
- Manual tag editing
- Vector/semantic search
- Analytics dashboard
- Batch processing
- Version control
- Slide templates
- Collaboration features

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Verify database exists
psql -l | grep slidex
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

## 📄 License

MIT License - feel free to use for your sales team!

## 👥 Team

Built by the sales engineering team to make demo prep faster and more efficient.

---

**Questions?** Open an issue or contact the team lead.
