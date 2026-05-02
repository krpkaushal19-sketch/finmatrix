@echo off
title FINMATRIX - Backend Server
color 0A
echo ========================================
echo    🏦 FINMATRIX BACKEND SERVER
echo ========================================
echo.
echo 📂 Changing to backend folder...
cd /d "C:\Users\kaush\Desktop\finmatrix\backend"
echo.
echo ✅ Current directory: %cd%
echo.
echo 📦 Checking Python...
python --version
echo.
echo 🚀 Starting Flask Server...
echo ========================================
echo.
echo 📊 Server will run at: http://localhost:5000
echo 📱 Then open frontend/index.html in browser
echo.
echo ========================================
echo    PRESS CTRL+C TO STOP SERVER
echo ========================================
echo.
python app.py
pause