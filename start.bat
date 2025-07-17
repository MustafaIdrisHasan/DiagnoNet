@echo off
echo.
echo ========================================
echo    Starting DiagnoNET 2.0
echo ========================================
echo.

echo [1/3] Starting Backend Server...
start "DiagnoNET Backend" cmd /k "cd diagnonet-backend && echo Starting DiagnoNET Backend Server... && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

echo [2/3] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo [3/3] Starting Frontend Server...
start "DiagnoNET Frontend" cmd /k "cd diagnonet-frontend && echo Starting DiagnoNET Frontend... && npm start"

echo.
echo ========================================
echo    DiagnoNET 2.0 is starting...
echo ========================================
echo.
echo Backend API:     http://localhost:8001
echo Frontend App:    http://localhost:3000
echo API Docs:        http://localhost:8001/docs
echo.
echo Note: Both servers will open in separate windows.
echo Close those windows to stop the servers.
echo.
echo Press any key to exit this launcher...
pause >nul
