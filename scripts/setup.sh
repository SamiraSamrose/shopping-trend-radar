#!/bin/bash
# scripts/setup.sh
# Setup script for Shopping Trend Radar Agent

set -e

echo "🚀 Setting up Shopping Trend Radar Agent..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Setup environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and credentials"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/logs
mkdir -p backend/data
mkdir -p frontend/static/uploads

# Setup database
echo "🗄️  Setting up database..."
if command -v createdb >/dev/null 2>&1; then
    createdb trendradar || echo "Database already exists"
    cd backend
    alembic upgrade head
    cd ..
else
    echo "⚠️  PostgreSQL command not found. Please create database manually"
fi

# Start services with Docker
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 10

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Edit .env file with your credentials"
echo "  2. Run: docker-compose up"
echo "  3. Visit: http://localhost:8000"
echo ""
echo "For development:"
echo "  source venv/bin/activate"
echo "  cd backend"
echo "  uvicorn app.main:app --reload"
