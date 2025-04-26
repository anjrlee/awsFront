#!/bin/bash

# Make the script executable
chmod +x /workspace/start.sh

# Check for .env file and source it if it exists
if [ -f /.env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' /workspace/.env | xargs)
else
    echo "No .env file found. Please create one based on .env.example if you need to set environment variables."
    echo "Continuing with default or system environment variables..."
fi

# Check if we should run the environment test
if [ "$1" = "test-env" ]; then
    echo "Running environment variable test..."
    cd backend
    pip install -r requirements.txt
    python3 test_env.py
    exit $?
fi

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Install frontend dependencies (if needed)
echo "Setting up frontend..."
cd ..

# Start backend server in the background
echo "Starting backend server..."
cd backend
python3 app.py &
BACKEND_PID=$!

# Start frontend server in the background
echo "Starting frontend server..."
cd ../frontend
node server.js &
FRONTEND_PID=$!

echo "Servers started!"
echo "Frontend is running at: http://localhost:8080"
echo "Backend is running at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to kill both servers on exit
function cleanup {
    echo "Stopping servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup SIGINT

# Keep the script running
wait


