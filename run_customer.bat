@echo off
title PurrfectMatch - Customer Adoption Portal
echo Starting PurrfectMatch Customer Adoption Portal...
python customer_app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error.
    pause
)
