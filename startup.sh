#!/bin/bash

# 🚀 Moon Dev Flow UI - Startup Script
# Launches both backend and frontend services for testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🌙 Moon Dev Flow UI - Startup Script                   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}[1/5] Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js ${NODE_VERSION} found${NC}"

# Check PostgreSQL
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL client found${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL client not found (optional, but backend will fail if DB isn't running)${NC}"
fi

# Check if database is running
echo ""
echo -e "${YELLOW}[2/5] Checking database connection...${NC}"
if psql -h localhost -U postgres -tc "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL not responding on localhost${NC}"
    echo -e "${YELLOW}   Start with: docker run -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:14${NC}"
    echo -e "${YELLOW}   Or ensure your local PostgreSQL service is running${NC}"
fi

# Setup backend
echo ""
echo -e "${YELLOW}[3/5] Setting up backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment (different for macOS/Linux vs Windows)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q -r requirements.txt

echo -e "${GREEN}✓ Backend setup complete${NC}"

# Setup frontend
echo ""
echo -e "${YELLOW}[4/5] Setting up frontend...${NC}"
cd ../ui

if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing npm dependencies...${NC}"
    npm install -q
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"

# Start services
echo ""
echo -e "${YELLOW}[5/5] Starting services...${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Starting backend on http://localhost:8000${NC}"
echo -e "${GREEN}Starting frontend on http://localhost:5173${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}TIP: Press Ctrl+C to stop both services${NC}"
echo ""

# Start backend in background
cd ../backend
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
python -m uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: ${BACKEND_PID})${NC}"

# Wait for backend to start
sleep 2

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend health check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Backend is running but health check failed (may still be starting)${NC}"
    fi
else
    echo -e "${RED}✗ Backend failed to start. Check /tmp/backend.log${NC}"
    cat /tmp/backend.log
    exit 1
fi

# Start frontend in background
cd ../ui
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: ${FRONTEND_PID})${NC}"

# Wait for frontend to start
sleep 3

if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend failed to start. Check /tmp/frontend.log${NC}"
    cat /tmp/frontend.log
    kill $BACKEND_PID
    exit 1
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Both services are running!                          ║${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}║  Backend:  http://localhost:8000                        ║${NC}"
echo -e "${GREEN}║  Frontend: http://localhost:5173                        ║${NC}"
echo -e "${GREEN}║  API Docs: http://localhost:8000/docs                   ║${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}║  Backend logs:  tail -f /tmp/backend.log                ║${NC}"
echo -e "${GREEN}║  Frontend logs: tail -f /tmp/frontend.log               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Cleanup on exit
trap "echo -e '\n${YELLOW}Stopping services...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e '${GREEN}✓ Services stopped${NC}'" EXIT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
