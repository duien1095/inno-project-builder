# Cline Tasks - Đã hoàn thành (phiên 2026-07-12)

## 1. Phân tích codebase
- Đọc `project_init.py` — app Tkinter quản lý template dự án quy hoạch
- Đọc `pyproject.toml` — project name `project_init`, version `0.1.0`
- Đọc `release.bat` / `release.sh` — script release cũ dùng `python -m build` (wheel/sdist)
- Đọc `requirements-release.txt` — chỉ có `pytest` và `build`
- Đọc `run_project_init.bat` — launcher cho người dùng
- Phân tích thư mục `_build_temp/` — phát hiện dấu vết PyInstaller từ lần build trước

## 2. Build bản chuẩn Python (wheel + sdist)
- Cài `build`, `pyproject_hooks` qua pip
- Chạy `python -m build` → tạo `dist/project_init-0.1.0-py3-none-any.whl` và `dist/project_init-0.1.0.tar.gz`

## 3. Build bản portable (PyInstaller)
- Cài `pyinstaller` (v6.21.0) qua pip
- **Build onedir**: `dist/_portable/project_init/project_init.exe` (thư mục kèm `_internal/`)
- **Build onefile**: `dist/project_init_portable.exe` (file .exe duy nhất, ~20-30MB)

## 4. Dọn dẹp & chuẩn hóa output
- Xóa `dist_portable/` (thư mục cũ chứa bản build cũ)
- Xóa wheel/sdist/onedir khỏi `dist/`, chỉ giữ `project_init_portable.exe`
- Xóa `_portable/` subdirectory

## 5. Cập nhật README.md
- Thêm phần **"Cơ chế Build"** hướng dẫn build portable với PyInstaller
- Sửa đường dẫn tải portable từ `dist_portable/` → `dist/`
- Rút gọn chỉ còn portable release, bỏ wheel/sdist/onedir docs

## 6. Cập nhật release scripts
- **`release.bat`**: Chuyển từ `python -m build` → PyInstaller `--onefile --windowed`
- **`release.sh`**: Tương tự, dùng separator `:` cho `--add-data` (Linux/Mac)

## 7. Cập nhật `.gitignore`
- Thêm `_build_temp/` (thư mục tạm của PyInstaller)
- Xóa `dist_portable/` (không còn tồn tại)

## 8. GitHub Actions CI/CD + Semantic Release
- **Tạo `.github/workflows/release.yml`**:
  - Trigger: push vào `main`
  - Checkout → setup Python 3.12 → cài dependencies
  - Chạy `pytest`
  - `python-semantic-release` phân tích commit messages, tự động bump version
  - Nếu có release → build `.exe` với PyInstaller
  - Upload `.exe` lên GitHub Release với tag version
- **`pyproject.toml`**: Thêm `[tool.semantic_release]`
  - `version_variables = ["project_init.py:__version__"]` — tự bump version trong source
  - `changelog_file = "CHANGELOG.md"` — tự tạo changelog
  - `upload_to_pypi = false` — chỉ GitHub Release, không PyPI
- **`requirements-release.txt`**: Thêm `python-semantic-release`, `pyinstaller`, `Pillow`

## 9. Commit & Push
- Commit `d11fde9`: "ci: add GitHub Actions workflow with semantic-release for portable .exe releases"
- Push lên `origin/main` thành công

## Quy ước commit cho semantic-release
| Prefix | Version bump |
|--------|-------------|
| `feat:` | minor |
| `fix:` | patch |
| `BREAKING CHANGE:` | major |