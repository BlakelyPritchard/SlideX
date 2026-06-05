#!/bin/bash

# SlideX Ollama Setup Script
# This script helps you set up Ollama + PaddleOCR for free local AI tagging

set -e  # Exit on error

echo "🚀 SlideX Ollama Setup Script"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Ollama is installed
echo "📦 Step 1: Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is installed${NC}"
    ollama --version
else
    echo -e "${YELLOW}⚠ Ollama is not installed${NC}"
    echo ""
    echo "Please install Ollama first:"
    echo "  macOS/Linux: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Windows: Download from https://ollama.com/download/windows"
    echo ""
    exit 1
fi

echo ""

# Check if Ollama is running
echo "🔍 Step 2: Checking if Ollama is running..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
else
    echo -e "${YELLOW}⚠ Ollama is not running${NC}"
    echo "Starting Ollama in background..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
    echo -e "${GREEN}✓ Ollama started${NC}"
fi

echo ""

# Check if LLaVA model is installed
echo "🤖 Step 3: Checking LLaVA model..."
if ollama list | grep -q "llava"; then
    echo -e "${GREEN}✓ LLaVA model is installed${NC}"
    ollama list | grep llava
else
    echo -e "${YELLOW}⚠ LLaVA model not found${NC}"
    echo "Downloading LLaVA model (this may take a few minutes)..."
    ollama pull llava
    echo -e "${GREEN}✓ LLaVA model downloaded${NC}"
fi

echo ""

# Install Python dependencies
echo "🐍 Step 4: Installing Python dependencies..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "Installing ollama, paddleocr, and paddlepaddle..."
pip install -q ollama==0.1.6
pip install -q paddleocr==2.7.3
pip install -q paddlepaddle==3.0.0

echo -e "${GREEN}✓ Python dependencies installed${NC}"

echo ""

# Update .env file
echo "⚙️  Step 5: Configuring .env file..."

# Backup existing .env
cp .env .env.backup

# Update or add Ollama settings
if grep -q "USE_OLLAMA" .env; then
    # Update existing settings
    sed -i.bak 's/USE_OLLAMA=.*/USE_OLLAMA=true/' .env
    sed -i.bak 's/OLLAMA_BASE_URL=.*/OLLAMA_BASE_URL=http:\/\/localhost:11434/' .env
    sed -i.bak 's/OLLAMA_MODEL=.*/OLLAMA_MODEL=llava/' .env
    sed -i.bak 's/USE_OCR=.*/USE_OCR=true/' .env
    rm .env.bak
else
    # Add new settings
    echo "" >> .env
    echo "# Ollama Configuration" >> .env
    echo "USE_OLLAMA=true" >> .env
    echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
    echo "OLLAMA_MODEL=llava" >> .env
    echo "USE_OCR=true" >> .env
fi

# Disable other AI providers
sed -i.bak 's/WATSONX_IAM_API_KEY=.*/WATSONX_IAM_API_KEY=/' .env
sed -i.bak 's/OPENAI_API_KEY=.*/OPENAI_API_KEY=/' .env
sed -i.bak 's/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=/' .env
rm .env.bak

echo -e "${GREEN}✓ .env file configured for Ollama${NC}"
echo "  (Backup saved as .env.backup)"

echo ""

# Test Ollama
echo "🧪 Step 6: Testing Ollama..."
echo "Sending test prompt to LLaVA..."

TEST_RESPONSE=$(ollama run llava "Say 'Hello from SlideX!' in exactly 5 words." 2>&1 | head -n 1)

if [ ! -z "$TEST_RESPONSE" ]; then
    echo -e "${GREEN}✓ Ollama is working!${NC}"
    echo "  Response: $TEST_RESPONSE"
else
    echo -e "${RED}✗ Ollama test failed${NC}"
    exit 1
fi

echo ""
echo "================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Start the backend:"
echo "     cd backend"
echo "     source venv/bin/activate"
echo "     uvicorn app.main:app --reload"
echo ""
echo "  2. Start the frontend (in another terminal):"
echo "     cd frontend"
echo "     npm run dev"
echo ""
echo "  3. Upload a PowerPoint file and watch Ollama tag it!"
echo ""
echo "📖 For more info, see: OLLAMA_SETUP.md"
echo ""

# Made with Bob
