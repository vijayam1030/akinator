@echo off
echo ========================================
echo    Akinator Game - Ollama Setup
echo ========================================
echo.

echo Checking if Ollama is installed...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama is not installed!
    echo.
    echo Please install Ollama first:
    echo 1. Download from https://ollama.ai/download
    echo 2. Or run: winget install Ollama.Ollama
    echo.
    pause
    exit /b 1
)

echo Ollama is installed! Version:
ollama --version
echo.

echo Starting Ollama service...
start /B ollama serve
echo.

echo Waiting for Ollama to start...
timeout /t 3 /nobreak >nul

echo Checking if Ollama is running...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama is not running. Please start it manually:
    echo ollama serve
    echo.
    pause
    exit /b 1
)

echo Ollama is running! 
echo.

echo Available models:
curl -s http://localhost:11434/api/tags | python -m json.tool 2>nul
echo.

echo Downloading recommended models for Akinator...
echo This may take a few minutes depending on your internet speed.
echo.

echo Downloading llama2:7b (4GB)...
ollama pull llama2:7b

echo Downloading mistral:7b (4GB)...
ollama pull mistral:7b

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo Models downloaded successfully!
echo.
echo You can now start the Akinator game:
echo 1. python app.py
echo 2. npm start
echo 3. Open http://localhost:3000
echo.
echo The game will now use your local LLMs for intelligent question generation!
echo.
pause 