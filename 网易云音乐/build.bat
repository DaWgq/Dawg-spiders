@echo off
cd /d "%~dp0"

echo ============================================================
echo   NetEase Music Comment Crawler - Build Script
echo ============================================================
echo.

REM Check PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [!] PyInstaller not found, installing...
    pip install pyinstaller
)

echo [1/2] Cleaning old build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "NetEaseMusicCrawler.spec" del /q "NetEaseMusicCrawler.spec"

echo [2/2] Building onedir package...
echo.

pyinstaller --noconfirm --windowed --onedir ^
    --name "NetEaseMusicCrawler" ^
    --hidden-import PySide6.QtWebEngineWidgets ^
    --hidden-import PySide6.QtWebEngineCore ^
    --hidden-import PySide6.QtWebChannel ^
    --hidden-import PySide6.QtNetwork ^
    --hidden-import PySide6.QtPrintSupport ^
    --hidden-import Crypto.Cipher.AES ^
    --hidden-import Crypto.Util.Padding ^
    --collect-submodules PySide6.QtWebEngineWidgets ^
    --collect-submodules PySide6.QtWebEngineCore ^
    app.py

if errorlevel 1 (
    echo.
    echo [X] Build failed, check error above
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Build OK
echo   Output dir: dist\NetEaseMusicCrawler\
echo   Exe file:   dist\NetEaseMusicCrawler\NetEaseMusicCrawler.exe
echo   Data dir (auto-created on first run): dist\NetEaseMusicCrawler\data\
echo ============================================================
echo.
pause
