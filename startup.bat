@echo off
REM 🚀 Moon Dev Flow UI - Startup Script (Windows)
REM Launches both backend and frontend services for testing

setlocal enabledelayedexpansion

cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  🌙 Moon Dev Flow UI - Startup Script                   ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Check prerequisites
echo [1/5] Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ✗ Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
color 0A
echo ✓ Python %PYTHON_VERSION% found
color 07

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ✗ Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
color 0A
echo ✓ Node.js %NODE_VERSION% found
color 07

REM Check PostgreSQL (optional)
psql --version >nul 2>&1
if errorlevel 1 (
    color 0E
    echo ⚠ PostgreSQL client not found (backend will fail if DB isn't running^)
    color 07
) else (
    color 0A
    echo ✓ PostgreSQL client found
    color 07
)

REM Setup backend
echo.
echo [2/5] Setting up backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q -r requirements.txt

color 0A
echo ✓ Backend setup complete
color 07

REM Setup frontend
echo.
echo [3/5] Setting up frontend...
cd ..\ui

if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install -q
)

color 0A
echo ✓ Frontend setup complete
color 07

REM Start services
echo.
echo [4/5] Starting services...
echo.
color 0A
echo ═══════════════════════════════════════════════════════
echo Starting backend on http://localhost:8000
echo Starting frontend on http://localhost:5173
echo ═══════════════════════════════════════════════════════
color 07
echo.
color 0E
echo TIP: Close this window to stop both services
color 07
echo.

REM Start backend in background
cd ..\backend
call venv\Scripts\activate.bat
start "Moon Dev Backend" python -m uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000

timeout /t 2 /nobreak

REM Start frontend in background
cd ..\ui
start "Moon Dev Frontend" cmd /k npm run dev

color 0A
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  ✅ Both services are starting!                         ║
echo ║                                                          ║
echo ║  Backend:  http://localhost:8000                        ║
echo ║  Frontend: http://localhost:5173                        ║
echo ║  API Docs: http://localhost:8000/docs                   ║
echo ║                                                          ║
echo ║  Close these windows to stop services                   ║
echo ╚══════════════════════════════════════════════════════════╝
color 07

pause
