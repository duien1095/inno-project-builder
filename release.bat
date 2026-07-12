@echo off
cd /d "%~dp0"
if "%1"=="" (
    echo Usage: release.bat ^<new-version^>
    exit /b 1
)
set VERSION=%1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-release.txt
python -m pytest
for /f "delims=" %%A in ('python -c "from project_init import __version__; print(__version__)"') do set CURRENT_VERSION=%%A
if not "%CURRENT_VERSION%"=="%VERSION%" (
    echo __version__ in project_init.py is %CURRENT_VERSION%, expected %VERSION%
    exit /b 1
)
python -m build
if exist dist\project_init-%VERSION%-* (
    echo Release build succeeded for version %VERSION%.
    exit /b 0
)
echo Release build did not produce expected artifact.
exit /b 1
