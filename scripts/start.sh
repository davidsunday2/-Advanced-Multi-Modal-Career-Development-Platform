#!/bin/bash

# AI Career Coach & Simulator Start Script
echo "🚀 Starting AI Career Coach & Simulator..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if .env files exist
if [ ! -f backend/.env ]; then
    print_warning "Backend .env file not found. Running setup first..."
    ./scripts/setup.sh
fi

# Start the services
print_status "Starting services with Docker Compose..."
docker-compose up -d postgres redis

print_status "Waiting for database to be ready..."
sleep 10

print_status "Starting backend and frontend..."
docker-compose up -d backend frontend

print_status "Services are starting up..."
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Database: localhost:5432"
echo "   Redis: localhost:6379"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f [service_name]"
echo ""
echo "🛑 To stop the application:"
echo "   ./scripts/stop.sh"
