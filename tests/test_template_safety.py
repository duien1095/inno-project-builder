import tempfile
import unittest
from pathlib import Path

from project_init import (
    is_safe_template_folder_path,
    validate_project_folder_path,
)


class TemplateSafetyTests(unittest.TestCase):
    def test_rejects_local_absolute_path(self) -> None:
        self.assertFalse(is_safe_template_folder_path("D:/Company"))
        self.assertFalse(is_safe_template_folder_path(r"C:\\temp"))

    def test_accepts_unc_path(self) -> None:
        self.assertTrue(is_safe_template_folder_path(r"\\server\\share\\folder"))

    def test_rejects_traversal_path(self) -> None:
        self.assertFalse(is_safe_template_folder_path("..\\secret"))
        self.assertFalse(is_safe_template_folder_path("folder/../secret"))

    def test_validate_project_folder_path_rejects_non_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_folder = Path(temp_dir)
            (project_folder / "existing.txt").write_text("demo", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "không rỗng"):
                validate_project_folder_path(project_folder)


if __name__ == "__main__":
    unittest.main()
