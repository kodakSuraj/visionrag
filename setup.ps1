# VisionRAG Setup Script for PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VisionRAG - Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create virtual environment
if (Test-Path "venv") {
    Write-Host "[!] Virtual environment already exists" -ForegroundColor Yellow
} else {
    Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 2: Activate and install dependencies
Write-Host "[2/4] Installing Python dependencies..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Check Ollama
Write-Host "[3/4] Checking Ollama..." -ForegroundColor Green
$ollamaRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:11434/api/tags" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $ollamaRunning = $true
        Write-Host "  ✓ Ollama server is running" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Ollama server is not running" -ForegroundColor Red
    Write-Host "    Please install and start Ollama from: https://ollama.ai/" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Check Ollama models
if ($ollamaRunning) {
    Write-Host "[4/4] Checking Ollama models..." -ForegroundColor Green
    
    Write-Host "  Checking for llama3:instruct..." -ForegroundColor Cyan
    $llamaCheck = ollama list | Select-String "llama3:instruct"
    if ($llamaCheck) {
        Write-Host "    ✓ llama3:instruct found" -ForegroundColor Green
    } else {
        Write-Host "    ✗ llama3:instruct not found" -ForegroundColor Red
        Write-Host "    Run: ollama pull llama3:instruct" -ForegroundColor Yellow
    }
    
    Write-Host "  Checking for nomic-embed-text..." -ForegroundColor Cyan
    $nomicCheck = ollama list | Select-String "nomic-embed-text"
    if ($nomicCheck) {
        Write-Host "    ✓ nomic-embed-text found" -ForegroundColor Green
    } else {
        Write-Host "    ✗ nomic-embed-text not found" -ForegroundColor Red
        Write-Host "    Run: ollama pull nomic-embed-text" -ForegroundColor Yellow
    }
} else {
    Write-Host "[4/4] Skipping model check (Ollama not running)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "  .\run.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or manually:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "  streamlit run app/main.py" -ForegroundColor Yellow
Write-Host ""
