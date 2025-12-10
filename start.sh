#!/bin/bash

# GTFS Chat - Local Development Startup Script
# Starts backend and frontend servers for local development

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${GREEN}🚀 Starting GTFS Chat Development Servers...${NC}\n"

# Check if .env file exists in backend
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: backend/.env not found. Copy backend/env.example to backend/.env and configure it.${NC}"
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup SIGINT SIGTERM

# Start Backend Server
echo -e "${GREEN}📦 Starting Backend (FastAPI) on http://127.0.0.1:8000${NC}"
cd backend
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run: cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

source .venv/bin/activate
set -a
[ -f .env ] && source .env
set +a

uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start Frontend Server
echo -e "${GREEN}🎨 Starting Frontend (Vite) on http://127.0.0.1:8080${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "\n${GREEN}✅ All servers started!${NC}\n"
echo -e "${GREEN}📡 Backend API:    http://127.0.0.1:8000${NC}"
echo -e "${GREEN}🌐 Frontend:       http://127.0.0.1:8080${NC}"
echo -e "${GREEN}📚 API Docs:       http://127.0.0.1:8000/docs${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all servers${NC}\n"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

