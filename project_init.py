"""
INNO PROJECT BUILDER - Khởi tạo cấu trúc dự án chuẩn.

*** File này giữ để tương thích ngược ***
Code đã được tái cấu trúc vào thư mục src/.

Các module mới:
  - src/main.py         : Entry point chính
  - src/config.py       : Cấu hình, đường dẫn
  - src/template_engine.py : Xử lý template, kiểm tra an toàn
  - src/ui/app.py       : Giao diện Tkinter
"""

# Re-export các thành phần từ module mới để giữ tương thích
from src import __version__  # noqa: F401
from src.template_engine import (  # noqa: F401
    build_tree_overview_text,
    create_template_folders,
    format_created_items,
    is_safe_template_folder_path,
    is_unsafe_target_path,
    validate_project_folder_path,
)
from src.ui.app import ProjectInitApp  # noqa: F401

def main() -> None:
    """Khởi động ứng dụng (tương thích ngược)."""
    from src.main import main as new_main
    new_main()
if __name__ == "__main__":
    main()

