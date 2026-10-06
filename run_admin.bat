@echo off
title PurrfectMatch - Staff Management Dashboard
echo Starting PurrfectMatch Staff Management Dashboard...
python admin_app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error.
    pause
)
