"""Test cho chức năng sinh file PDF từ template_pdf.json (phiên bản 1 trang A4)."""

import json
import tempfile
import unittest
from pathlib import Path

from src.template_engine import (
    PDF_OUTPUT_FILENAME,
    PDF_TEMPLATE_FILENAME,
    PDF_TEMPLATE_NAMES,
    generate_pdf_template,
    create_template_folders,
)


SAMPLE_JSON = {
    "document_name": "HUONG_DAN_LUU_TRU",
    "version": "1.0",
    "overview": {
        "input": "Nơi lưu dữ liệu gốc nhận từ bên ngoài",
        "process": "Nơi lưu hồ sơ đang thực hiện",
        "output": "Nơi lưu sản phẩm đã hoàn thiện",
    },
    "sections": [
        {
            "name": "01.INPUT",
            "items": [
                {"folder": "01.PHAP_LY", "description": "Văn bản pháp lý"},
                {"folder": "02.RANH_GIOI", "description": "Hồ sơ ranh giới"},
            ],
        },
        {
            "name": "02.PROCESS",
            "items": [
                {"folder": "01.HO_SO", "description": "Hồ sơ tổng hợp"},
            ],
        },
    ],
}


class PdfTemplateTests(unittest.TestCase):
    """Kiểm tra generate_pdf_template và tích hợp với create_template_folders."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.origin_dir = Path.cwd()
        self.template_dir = Path(self.temp_dir.name)

        # Tạo file template_pdf.json
        json_path = self.template_dir / PDF_TEMPLATE_FILENAME
        json_path.write_text(
            json.dumps(SAMPLE_JSON, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        import os
        os.chdir(str(self.template_dir))

    def tearDown(self) -> None:
        import os
        os.chdir(str(self.origin_dir))
        self.temp_dir.cleanup()

    def test_generate_pdf_qhc(self) -> None:
        """Sinh file PDF cho QHC."""
        project_folder = self.template_dir / "DU_AN_QHC"
        project_folder.mkdir(parents=True, exist_ok=True)

        result = generate_pdf_template(project_folder, "QHC")

        self.assertIsNotNone(result)
        self.assertTrue(result.exists())
        self.assertEqual(result.name, PDF_OUTPUT_FILENAME)
        self.assertGreater(result.stat().st_size, 1000)

    def test_generate_pdf_qhpk(self) -> None:
        """Sinh file PDF cho QHPK."""
        project_folder = self.template_dir / "DU_AN_QHPK"
        project_folder.mkdir(parents=True, exist_ok=True)

        result = generate_pdf_template(project_folder, "QHPK")

        self.assertIsNotNone(result)
        self.assertTrue(result.exists())

    def test_generate_pdf_qhct(self) -> None:
        """Sinh file PDF cho QHCT."""
        project_folder = self.template_dir / "DU_AN_QHCT"
        project_folder.mkdir(parents=True, exist_ok=True)

        result = generate_pdf_template(project_folder, "QHCT")

        self.assertIsNotNone(result)
        self.assertTrue(result.exists())

    def test_not_generate_for_concept(self) -> None:
        """Không sinh PDF cho CONCEPT."""
        for concept_name in ["CONCEPT_QHPK", "CONCEPT_QHCT"]:
            project_folder = self.template_dir / f"DU_AN_{concept_name}"
            project_folder.mkdir(parents=True, exist_ok=True)

            result = generate_pdf_template(project_folder, concept_name)
            self.assertIsNone(result)

    def test_created_files_list(self) -> None:
        """Kiểm tra created_files có chứa PDF."""
        project_folder = self.template_dir / "DU_AN_FILES"
        project_folder.mkdir(parents=True, exist_ok=True)

        created_files: list[Path] = []
        generate_pdf_template(project_folder, "QHC", created_files=created_files)

        self.assertEqual(len(created_files), 1)
        self.assertEqual(created_files[0].name, PDF_OUTPUT_FILENAME)

    def test_pdf_in_template_folder(self) -> None:
        """PDF lưu trong 00.TEMPLATE nếu có trong folder_paths."""
        project_folder = self.template_dir / "DU_AN_TEMPLATE"
        project_folder.mkdir(parents=True, exist_ok=True)
        (project_folder / "00.TEMPLATE").mkdir(parents=True, exist_ok=True)

        result = generate_pdf_template(
            project_folder, "QHC",
            folder_paths=["00.TEMPLATE", "01.INPUT"],
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.parent.name, "00.TEMPLATE")

    def test_pdf_in_root_if_no_template_folder(self) -> None:
        """PDF lưu ở gốc nếu không có TEMPLATE."""
        project_folder = self.template_dir / "DU_AN_ROOT"
        project_folder.mkdir(parents=True, exist_ok=True)

        result = generate_pdf_template(
            project_folder, "QHC",
            folder_paths=["01.INPUT"],
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.parent, project_folder)

    def test_pdf_is_valid(self) -> None:
        """Kiểm tra header PDF hợp lệ."""
        project_folder = self.template_dir / "DU_AN_VALID"
        project_folder.mkdir(parents=True, exist_ok=True)

        generate_pdf_template(project_folder, "QHC")

        pdf_path = project_folder / PDF_OUTPUT_FILENAME
        with open(pdf_path, "rb") as f:
            header = f.read(5)
        self.assertEqual(header, b"%PDF-")

    def test_pdf_one_page(self) -> None:
        """Đảm bảo PDF chỉ có 1 trang."""
        project_folder = self.template_dir / "DU_AN_ONEPAGE"
        project_folder.mkdir(parents=True, exist_ok=True)

        generate_pdf_template(project_folder, "QHC")

        pdf_path = project_folder / PDF_OUTPUT_FILENAME
        with open(pdf_path, "rb") as f:
            content = f.read()

        page_count = content.count(b"/Type /Page") - content.count(b"/Type /Pages")
        self.assertEqual(page_count, 1, "PDF phai nam gon trong 1 trang A4")

    def test_integration_create_template_folders_qhc(self) -> None:
        """Tích hợp: create_template_folders tạo thư mục + PDF + Excel."""
        project_folder = self.template_dir / "DU_AN_INTEGRATION"

        created_dirs, created_files = create_template_folders(
            project_folder,
            ["01.INPUT", "02.PROCESS"],
            template_name="QHC",
        )

        self.assertEqual(len(created_dirs), 2)
        self.assertTrue((project_folder / "01.INPUT").exists())
        self.assertTrue((project_folder / "02.PROCESS").exists())

        pdf_files = [f for f in created_files if f.name == PDF_OUTPUT_FILENAME]
        self.assertEqual(len(pdf_files), 1)
        self.assertTrue((project_folder / PDF_OUTPUT_FILENAME).exists())

    def test_integration_with_template_subdir(self) -> None:
        """Tích hợp: có 00.TEMPLATE thì PDF vào đó."""
        project_folder = self.template_dir / "DU_AN_TEMPLATE_INT"

        created_dirs, created_files = create_template_folders(
            project_folder,
            ["00.TEMPLATE", "01.INPUT", "02.PROCESS"],
            template_name="QHC",
        )

        self.assertEqual(len(created_dirs), 3)
        pdf_files = [f for f in created_files if f.name == PDF_OUTPUT_FILENAME]
        self.assertEqual(len(pdf_files), 1)
        self.assertTrue((project_folder / "00.TEMPLATE" / PDF_OUTPUT_FILENAME).exists())

    def test_integration_concept_skips_pdf(self) -> None:
        """Tích hợp: CONCEPT không tạo PDF."""
        project_folder = self.template_dir / "DU_AN_CONCEPT"

        created_dirs, created_files = create_template_folders(
            project_folder,
            ["01.INPUT", "02.PROCESS"],
            template_name="CONCEPT_QHPK",
        )

        self.assertEqual(len(created_dirs), 2)
        pdf_files = [f for f in created_files if f.name == PDF_OUTPUT_FILENAME]
        self.assertEqual(len(pdf_files), 0)
        self.assertFalse((project_folder / PDF_OUTPUT_FILENAME).exists())


if __name__ == "__main__":
    unittest.main()
