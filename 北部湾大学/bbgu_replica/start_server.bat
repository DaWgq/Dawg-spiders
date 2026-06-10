@echo off
echo ========================================
echo  北部湾大学 - 本地复刻版
echo ========================================
echo Starting HTTP server at http://localhost:8080
echo Press Ctrl+C to stop
echo ========================================
python -m http.server 8080 --directory "%~dp0"
pause
