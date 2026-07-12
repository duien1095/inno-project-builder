@echo off
cd /d "%~dp0"
if "%1"=="" (
    echo Usage: release.bat ^<new-version^>
    echo.
    echo Options:
    echo   ^<version^>     Build and create GitHub release (requires gh CLI)
    echo   --local-only   Only build .exe, skip GitHub release
    exit /b 1
)

set VERSION=%1
set LOCAL_ONLY=0
if "%VERSION%"=="--local-only" (
    set VERSION=%2
    set LOCAL_ONLY=1
)

if "%VERSION%"=="" (
    echo Error: Missing version argument
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r requirements-release.txt
python -m pytest
if %ERRORLEVEL% NEQ 0 (
    echo Tests failed. Aborting release.
exit /b 1
)

for /f "delims=" %%A in ('python -c "from src import __version__; print(__version__)"') do set CURRENT_VERSION=%%A
if not "%CURRENT_VERSION%"=="%VERSION%" (
    echo __version__ in src is %CURRENT_VERSION%, expected %VERSION%
    exit /b 1
)

echo Building portable .exe for version %VERSION%...
python -m PyInstaller --noconfirm --onefile --windowed --name project_init_portable --add-data "templates;templates" --add-data "templates_config.json;." --add-data "assets_logo.png;." --hidden-import PIL --hidden-import PIL._tkinter_finder --workpath _build_temp/project_init_portable --distpath dist project_init.py
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller build failed.
    exit /b 1
)

if not exist dist\project_init_portable.exe (
    echo Release build did not produce expected artifact.
    exit /b 1
)

echo.
echo === Build successful: dist\project_init_portable.exe ===
echo.

if "%LOCAL_ONLY%"=="1" (
    echo Local build only. Skipping GitHub release.
    exit /b 0
)

:: Create GitHub release and upload asset
echo Creating GitHub release v%VERSION%...
gh release create v%VERSION% ^
    --title "v%VERSION%" ^
    --notes-file CHANGELOG.md ^
    dist\project_init_portable.exe

if %ERRORLEVEL% EQU 0 (
    echo GitHub release v%VERSION% created successfully!
    echo.
    echo Users can now download from:
    echo   https://github.com/duien1095/inno-project-builder/releases/latest
    echo.
    echo GitHub Pages will auto-update at:
    echo   https://duien1095.github.io/inno-project-builder/
) else (
    echo WARNING: Build succeeded but failed to create GitHub release.
    echo Manual upload: https://github.com/duien1095/inno-project-builder/releases/new
)

exit /b 0
