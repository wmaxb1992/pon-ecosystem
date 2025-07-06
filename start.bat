@echo off
chcp 65001 >nul

echo 🎥 Starting Video Scraper Application...
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed. Please install npm.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Create videos directory if it doesn't exist
if not exist "backend\videos" mkdir backend\videos

REM Start backend server
echo 🚀 Starting FastAPI backend server...
start "Backend Server" cmd /k "cd backend && python main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo ✅ Backend server started on http://localhost:8000

REM Install frontend dependencies if node_modules doesn't exist
if not exist "frontend\node_modules" (
    echo 📥 Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
)

REM Start frontend server
echo 🚀 Starting Next.js frontend server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

REM Wait a moment for frontend to start
timeout /t 5 /nobreak >nul

echo ✅ Frontend server started on http://localhost:3000
echo.
echo 🎉 Application is running!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause >nul 