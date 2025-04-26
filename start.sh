#!/bin/bash

# === Python 虛擬環境設定 ===
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

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
    cd backend
    pip install -r requirements.txt
    python3 test_env.py
    exit $?
fi

# === 安裝後端依賴 ===
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# === 安裝前端依賴（可加檢查）===
echo "Setting up frontend..."
cd ..

# === 啟動後端服務 ===
echo "Starting backend server..."
cd backend
python3 app.py &
BACKEND_PID=$!

# === 啟動前端服務 ===
echo "Starting frontend server..."
cd ../frontend
node server.js &
FRONTEND_PID=$!

# === 顯示運行狀態 ===
echo "Servers started!"
echo "Frontend is running at: http://localhost:8080"
echo "Backend is running at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"

# === 清理程序 ===
function cleanup {
    echo "Stopping servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    deactivate
    exit 0
}
trap cleanup SIGINT

# === 保持前景程序運行中 ===
wait
