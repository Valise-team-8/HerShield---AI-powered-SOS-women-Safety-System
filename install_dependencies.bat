@echo off
echo ========================================
echo   AI SOS - Installing Dependencies
echo ========================================
echo.
echo This will install all required packages...
echo.
pause
echo.
echo Installing desktop dependencies...
pip install -r requirements.txt
echo.
echo Installing web dependencies...
pip install flask flask-socketio
echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo You can now run:
echo   - run_desktop.bat (Desktop version)
echo   - run_web.bat (Web version)
echo   - test_features.bat (Test all features)
echo.
pause
