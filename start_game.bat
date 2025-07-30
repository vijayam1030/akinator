@echo off
echo ========================================
echo    Akinator Game - One-Click Start
echo ========================================
echo.

echo Starting Akinator Game...
echo.

echo [1/4] Checking Python dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Could not install Python dependencies
    echo Continuing anyway...
)
echo ✓ Python dependencies checked
echo.

echo [2/4] Checking Node.js dependencies...
npm install >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Could not install Node.js dependencies
    echo Continuing anyway...
)
echo ✓ Node.js dependencies checked
echo.

echo [3/4] Starting Flask backend server...
start "Akinator Backend" cmd /k "python app.py"
echo ✓ Backend server starting on http://localhost:5000
echo.

echo [4/4] Starting React frontend server...
start "Akinator Frontend" cmd /k "npm start"
echo ✓ Frontend server starting on http://localhost:3000
echo.

echo Waiting for servers to start...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo    🎮 Akinator Game is Starting!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo The browser should open automatically in a few seconds...
echo If not, manually open: http://localhost:3000
echo.
echo Press any key to open the game in your browser...
pause >nul

start http://localhost:3000

echo.
echo ========================================
echo    🎯 Game Started Successfully!
echo ========================================
echo.
echo To stop the servers:
echo 1. Close the command windows that opened
echo 2. Or press Ctrl+C in each window
echo.
echo Enjoy playing Akinator! 🎮
echo.
pause 