#!/bin/bash

# GTFS Chat - ADK Web Server Startup Script
# Starts the Google ADK web interface for testing the agent

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${GREEN}🤖 Starting ADK Web Server...${NC}\n"

# Check if .env file exists in backend
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ Error: backend/.env not found. Copy backend/env.example to backend/.env and configure it.${NC}"
    exit 1
fi

# Start ADK Web Server
cd backend
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run: cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

source .venv/bin/activate
set -a
source .env
set +a

echo -e "${GREEN}🌐 ADK Web Interface: http://127.0.0.1:8001${NC}\n"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}\n"

adk web agents --port 8001 --host 127.0.0.1

