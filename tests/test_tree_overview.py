import tempfile
import unittest
from pathlib import Path

from src.template_engine import build_tree_overview_text, validate_project_folder_path
from src import __version__


class TreeOverviewTests(unittest.TestCase):
    def test_build_tree_overview_marks_newly_created_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_folder = Path(temp_dir)
            folder_paths = ["01_INPUT", "01_INPUT/02_RANH_QHC"]

            # Tạo thư mục thật trên đĩa để exists() trả về True
            created_dirs = [
                project_folder / "01_INPUT",
                project_folder / "01_INPUT/02_RANH_QHC",
            ]
            for d in created_dirs:
                d.mkdir(parents=True, exist_ok=True)

            content = build_tree_overview_text(
                project_folder, "QHC", folder_paths, created_dirs
            )

            self.assertIn("Nơi lưu:", content)
            self.assertIn("Template: QHC", content)
            self.assertIn("01_INPUT [Đã tạo mới]", content)
            self.assertIn("01_INPUT/02_RANH_QHC [Đã tạo mới]", content)

    def test_build_tree_overview_marks_existing_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_folder = Path(temp_dir)
            (project_folder / "01_INPUT").mkdir(parents=True, exist_ok=True)
            folder_paths = ["01_INPUT", "01_INPUT/02_RANH_QHC"]

            content = build_tree_overview_text(
                project_folder, "QHC", folder_paths, []
            )

            self.assertIn("01_INPUT [Đã có sẵn]", content)
            self.assertIn("01_INPUT/02_RANH_QHC [Chưa tạo]", content)

    def test_validate_project_folder_path_allows_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_folder = Path(temp_dir)
            validate_project_folder_path(project_folder)

    def test_validate_project_folder_path_rejects_non_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_folder = Path(temp_dir)
            (project_folder / "existing.txt").write_text("demo", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "không rỗng"):
                validate_project_folder_path(project_folder)

    def test_version_in_ui(self) -> None:
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+(-[A-Za-z0-9.+-]+)?$")


if __name__ == "__main__":
    unittest.main()
