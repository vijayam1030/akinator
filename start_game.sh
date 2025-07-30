#!/bin/bash

echo "========================================"
echo "   Akinator Game - One-Click Start"
echo "========================================"
echo

echo "Starting Akinator Game..."
echo

echo "[1/4] Checking Python dependencies..."
pip install -r requirements.txt >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Warning: Could not install Python dependencies"
    echo "Continuing anyway..."
fi
echo "✓ Python dependencies checked"
echo

echo "[2/4] Checking Node.js dependencies..."
npm install >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Warning: Could not install Node.js dependencies"
    echo "Continuing anyway..."
fi
echo "✓ Node.js dependencies checked"
echo

echo "[3/4] Starting Flask backend server..."
python app.py &
BACKEND_PID=$!
echo "✓ Backend server starting on http://localhost:5000"
echo

echo "[4/4] Starting React frontend server..."
npm start &
FRONTEND_PID=$!
echo "✓ Frontend server starting on http://localhost:3000"
echo

echo "Waiting for servers to start..."
sleep 5

echo
echo "========================================"
echo "   🎮 Akinator Game is Starting!"
echo "========================================"
echo
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo
echo "The browser should open automatically in a few seconds..."
echo "If not, manually open: http://localhost:3000"
echo

# Try to open browser (works on macOS and some Linux distros)
if command -v open >/dev/null 2>&1; then
    # macOS
    open http://localhost:3000
elif command -v xdg-open >/dev/null 2>&1; then
    # Linux
    xdg-open http://localhost:3000
elif command -v sensible-browser >/dev/null 2>&1; then
    # Debian/Ubuntu
    sensible-browser http://localhost:3000
else
    echo "Please manually open: http://localhost:3000"
fi

echo
echo "========================================"
echo "   🎯 Game Started Successfully!"
echo "========================================"
echo
echo "To stop the servers:"
echo "1. Press Ctrl+C in this terminal"
echo "2. Or run: kill $BACKEND_PID $FRONTEND_PID"
echo
echo "Enjoy playing Akinator! 🎮"
echo

# Function to cleanup on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
echo "Press Ctrl+C to stop the servers..."
wait 