#!/bin/bash

# AI Career Coach & Simulator Setup Script
echo "🚀 Setting up AI Career Coach & Simulator..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating project directories..."
mkdir -p backend/uploads backend/temp backend/logs
mkdir -p database/backups
mkdir -p docs/screenshots

# Copy environment template files
print_status "Setting up environment files..."

# Backend environment
if [ ! -f backend/.env ]; then
    cp backend/env_template.txt backend/.env
    print_warning "Please edit backend/.env with your API keys before starting the application"
fi

# Frontend environment
if [ ! -f frontend/.env ]; then
    cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
EOF
    print_status "Created frontend/.env with default values"
fi

# Set proper permissions
print_status "Setting file permissions..."
chmod +x scripts/*.sh
chmod 644 backend/.env frontend/.env

# Generate a secret key for the backend
print_status "Generating application secret key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/your_super_secret_key_here_change_in_production/$SECRET_KEY/" backend/.env
else
    # Linux
    sed -i "s/your_super_secret_key_here_change_in_production/$SECRET_KEY/" backend/.env
fi

print_status "Setup completed successfully! 🎉"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - PINECONE_API_KEY"
echo "   - SERPAPI_API_KEY"
echo ""
echo "2. Start the application:"
echo "   ./scripts/start.sh"
echo ""
echo "3. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
