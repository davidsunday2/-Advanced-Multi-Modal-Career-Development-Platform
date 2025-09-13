#!/bin/bash

# AI Career Coach & Simulator Stop Script
echo "🛑 Stopping AI Career Coach & Simulator..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Stop all services
print_status "Stopping all services..."
docker-compose down

print_status "All services stopped successfully! 🎉"
echo ""
echo "To start again: ./scripts/start.sh"
echo "To remove volumes: docker-compose down -v"
