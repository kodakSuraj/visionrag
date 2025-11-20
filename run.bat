@echo off
REM VisionRAG Launcher Script for Windows

echo ========================================
echo VisionRAG - CCTV Video Q^&A System (V1)
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\activate ^& pip install -r requirements.txt
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Streamlit application...
echo.
echo Open your browser to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app/main.py
