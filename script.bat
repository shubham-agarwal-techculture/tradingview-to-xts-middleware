@echo off

title TradingView to XTS System
cd /d "%~dp0"

echo ==========================================
echo Starting TradingView to XTS System
echo ==========================================
echo.

:: Check if virtual environment exists
if exist ".venv" goto :VENV_FOUND
echo [ERROR] Virtual environment (.venv) not found in %CD%
echo Please create it using: python -m venv .venv
pause
exit /b

:VENV_FOUND
:: Activate virtual environment
echo [1/3] Activating virtual environment...
if exist ".venv\Scripts\activate.bat" goto :ACTIVATE_OK
echo [ERROR] Could not find .venv\Scripts\activate.bat
pause
exit /b

:ACTIVATE_OK
call ".venv\Scripts\activate.bat"

:: Open Server 1 in a new CMD window
@REM start /b cmd /c "python app.py"

wt nt --title "Middleware-app" cmd /k "cd /d D:\projects-shubham\08.05.2026\trading_view_alerts && python app.py";nt --title "ngrok server public webhook" cmd /k "cd /d D:\projects-shubham\08.05.2026\trading_view_alerts && ngrok http 5000";nt --title "dummy xts api" cmd /k "cd /d D:\projects-shubham\08.05.2026\trading_view_alerts && python dummy_xts_api.py"


:: Open Server 2 in a new CMD window
@REM start /b cmd /c "ngrok http 5000"
@REM nt cmd /k "ngrok http 5000"


:: Open Server 3 in a new CMD window
@REM start /b cmd /c "python dummy_xts_api.py"
@REM nt cmd /k "python dummy_xts_api.py"


@REM pause

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] The application stopped with error code %ERRORLEVEL%
    echo This usually means a port conflict or a missing dependency.
    echo Try running: pip install -r requirements.txt
    pause
)
