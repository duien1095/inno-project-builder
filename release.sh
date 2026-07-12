#!/usr/bin/env bash
set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PACKAGE_DIR"

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <new-version>"
  exit 1
fi

VERSION="$1"

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-release.txt
python -m pytest
python -c "from pathlib import Path; from src import __version__; import re; assert __version__ == '$VERSION', f'__version__ in src is {__version__}, expected {VERSION}'"

python -m build

if [[ -f dist/project_init-${VERSION}* ]]; then
  echo "Release build succeeded for version ${VERSION}."
else
  echo "Release build did not produce expected artifact."
  exit 1
fi
