@echo off
cd /d "%~dp0"
if "%1"=="" (
    echo Usage: release.bat ^<new-version^>
    exit /b 1
)
set VERSION=%1
python -m pip install --upgrade pip
python -m pip install -r requirements-release.txt
python -m pytest
for /f "delims=" %%A in ('python -c "from project_init import __version__; print(__version__)"') do set CURRENT_VERSION=%%A
if not "%CURRENT_VERSION%"=="%VERSION%" (
    echo __version__ in project_init.py is %CURRENT_VERSION%, expected %VERSION%
    exit /b 1
)
echo Building portable .exe for version %VERSION%...
python -m PyInstaller --noconfirm --onefile --windowed --name project_init_portable --add-data "templates;templates" --add-data "templates_config.json;." --add-data "assets_logo.png;." --hidden-import PIL --hidden-import PIL._tkinter_finder --workpath _build_temp/project_init_portable --distpath dist project_init.py
if exist dist\project_init_portable.exe (
    echo Release build succeeded for version %VERSION%. Portable .exe at dist\project_init_portable.exe
    exit /b 0
)
echo Release build did not produce expected artifact.
exit /b 1