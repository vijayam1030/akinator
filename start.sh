#!/bin/bash

echo "Starting Akinator Game..."
echo

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo
echo "Installing Node.js dependencies..."
npm install

echo
echo "Starting Flask backend server..."
python app.py &
BACKEND_PID=$!

echo
echo "Waiting 3 seconds for backend to start..."
sleep 3

echo
echo "Starting React frontend server..."
npm start &
FRONTEND_PID=$!

echo
echo "Both servers are starting..."
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo
echo "Press Ctrl+C to stop both servers..."

# Wait for user to stop
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait 