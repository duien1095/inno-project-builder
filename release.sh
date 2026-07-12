a#!/usr/bin/env bash
set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PACKAGE_DIR"

LOCAL_ONLY=false
VERSION=""

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 [--local-only] <new-version>"
  echo ""
  echo "Options:"
  echo "  <version>       Build and create GitHub release (requires gh CLI)"
  echo "  --local-only    Only build .exe, skip GitHub release"
  exit 1
fi

if [[ "$1" == "--local-only" ]]; then
  LOCAL_ONLY=true
  VERSION="$2"
else
  VERSION="$1"
fi

if [[ -z "$VERSION" ]]; then
  echo "Error: Missing version argument"
  exit 1
fi

# Install deps
python -m pip install --upgrade pip
python -m pip install -r requirements-release.txt

# Run tests
python -m pytest
echo "Tests passed."

# Check version
python -c "from src import __version__; assert __version__ == '$VERSION', f'__version__ in src is {__version__}, expected {VERSION}'"
echo "Version check passed: v${VERSION}"

# Build portable .exe
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

if [[ ! -f dist/project_init_portable.exe ]]; then
  echo "ERROR: Build did not produce dist/project_init_portable.exe"
  exit 1
fi

echo ""
echo "=== Build successful: dist/project_init_portable.exe ==="
echo ""

if [[ "$LOCAL_ONLY" == true ]]; then
  echo "Local build only. Skipping GitHub release."
  exit 0
fi

# Create GitHub release
echo "Creating GitHub release v${VERSION}..."
gh release create "v${VERSION}" \
  --title "v${VERSION}" \
  --notes-file CHANGELOG.md \
  dist/project_init_portable.exe

echo ""
echo "GitHub release v${VERSION} created successfully!"
echo ""
echo "Users can now download from:"
echo "  https://github.com/duien1095/inno-project-builder/releases/latest"
echo ""
echo "GitHub Pages will auto-update at:"
echo "  https://duien1095.github.io/inno-project-builder/"