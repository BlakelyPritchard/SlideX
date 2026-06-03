#!/bin/bash

# SlideX Backend Setup Script
# This script automates the backend setup process

echo "🚀 Setting up SlideX Backend..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
else
    echo ""
    echo "ℹ️  .env file already exists."
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p uploads slides thumbnails

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your database URL and API keys"
echo "2. Create PostgreSQL database: createdb slidex"
echo "3. Activate virtual environment: source venv/bin/activate"
echo "4. Run the server: uvicorn app.main:app --reload"
echo ""
echo "🌐 API will be available at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"

# Made with Bob
