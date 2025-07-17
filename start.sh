#!/bin/bash

echo ""
echo "========================================"
echo "    Starting DiagnoNET 2.0"
echo "========================================"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "[0/3] Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

if ! command_exists ollama; then
    echo "⚠️  Ollama is not installed. Some features may not work."
    echo "   Install from: https://ollama.ai/"
fi

echo "✅ Prerequisites check complete"

# Start backend in background
echo "[1/3] Starting Backend Server..."
cd diagnonet-backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "[2/3] Waiting for backend to initialize..."
sleep 5

# Start frontend in background
echo "[3/3] Starting Frontend Server..."
cd diagnonet-frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "    DiagnoNET 2.0 is running!"
echo "========================================"
echo ""
echo "Backend API:     http://localhost:8001"
echo "Frontend App:    http://localhost:3000"
echo "API Docs:        http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping DiagnoNET 2.0..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "All services stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
