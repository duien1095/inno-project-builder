#!/usr/bin/env bash
set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PACKAGE_DIR"

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <new-version>"
  exit 1
fi

VERSION="$1"

python -m pip install --upgrade pip
python -m pip install -r requirements-release.txt
python -m pytest
python -c "from project_init import __version__; assert __version__ == '$VERSION', f'__version__ in project_init.py is {__version__}, expected {VERSION}'"

echo "Building portable .exe for version ${VERSION}..."
python -m PyInstaller --noconfirm --onefile --windowed \
  --name project_init_portable \
  --add-data "templates:templates" \
  --add-data "templates_config.json:." \
  --add-data "assets_logo.png:." \
  --hidden-import PIL \
  --hidden-import PIL._tkinter_finder \
  --workpath _build_temp/project_init_portable \
  --distpath dist \
  project_init.py

if [[ -f dist/project_init_portable.exe ]]; then
  echo "Release build succeeded for version ${VERSION}. Portable .exe at dist/project_init_portable.exe"
else
  echo "Release build did not produce expected artifact."
  exit 1
fi