#!/bin/bash

# === Python 虛擬環境設定 ===
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv || { echo "❌ Failed to create venv"; exit 1; }
fi

echo "Activating virtual environment..."
source venv/bin/activate || { echo "❌ Failed to activate venv"; exit 1; }

# === 載入 .env 環境變數（若存在） ===
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "No .env file found. Please create one based on .env.example if needed."
    echo "Continuing with default or system environment variables..."
fi

# === 執行環境測試 ===
if [ "$1" = "test-env" ]; then
    echo "Running environment variable test..."
    cd backend || exit 1
    pip install -r requirements.txt || exit 1
    python3 test_env.py
    exit $?
fi

# === 安裝後端依賴 ===
echo "Installing backend dependencies..."
cd backend || exit 1
pip install -r requirements.txt || { echo "❌ Failed to install backend dependencies"; exit 1; }

# === 安裝前端依賴 ===
echo "Setting up frontend..."
cd ../frontend || exit 1
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install || { echo "❌ npm install failed"; exit 1; }
else
    echo "Frontend dependencies already installed."
fi

# === 啟動後端服務 ===
echo "Starting backend server..."
cd ../backend || exit 1
python3 app.py &
BACKEND_PID=$!

# === 啟動前端服務 ===
echo "Starting frontend server..."
cd ../frontend || exit 1
node server.js &
FRONTEND_PID=$!

# === 顯示運行狀態 ===
echo "✅ Servers started!"
echo "Frontend is running at: http://localhost:8080"
echo "Backend is running at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"

# === 清理程序 ===
function cleanup {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    deactivate
    exit 0
}
trap cleanup SIGINT

# === 保持前景程序運行中 ===
wait
