@echo off
setlocal

cd /d "%~dp0"

title JARVIS - Offline AI Assistant

echo.
echo ========================================
echo          JARVIS OFFLINE AI
echo ========================================
echo.

REM ------------------------------------------------
REM Prevent duplicate JARVIS instances
REM ------------------------------------------------

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$p = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue; if ($p) { exit 1 } else { exit 0 }"

if %errorlevel%==1 (
    echo JARVIS is already running.
    echo Opening the existing JARVIS window...
    start "" http://127.0.0.1:8501
    exit /b 0
)

REM ------------------------------------------------
REM Check Python
REM ------------------------------------------------

where python >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python was not found.
    echo Please install Python first.
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------------
REM Check Streamlit
REM ------------------------------------------------

python -m streamlit --version >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Streamlit is not installed.
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------------
REM Start JARVIS
REM ------------------------------------------------

echo Starting JARVIS...
echo.
echo JARVIS runs locally on this computer.
echo No internet connection is required.
echo.

start "" /b python -m streamlit run app.py ^
    --server.address=127.0.0.1 ^
    --server.port=8501 ^
    --server.headless=true ^
    --browser.gatherUsageStats=false

REM ------------------------------------------------
REM Wait for Streamlit
REM ------------------------------------------------

echo Waiting for JARVIS to start...

set /a attempts=0

:WAIT

set /a attempts+=1

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8501/_stcore/health' -UseBasicParsing -TimeoutSec 1; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

if %errorlevel%==0 goto OPEN

if %attempts% GEQ 30 goto FAILED

timeout /t 1 /nobreak >nul

goto WAIT


:OPEN

echo.
echo ========================================
echo       JARVIS IS READY
echo ========================================
echo.

start "" http://127.0.0.1:8501

echo JARVIS is running in your browser.
echo You can close this window.
echo.

exit /b 0


:FAILED

echo.
echo ========================================
echo       JARVIS FAILED TO START
echo ========================================
echo.
echo Check that Ollama is running.
echo.
pause

endlocal