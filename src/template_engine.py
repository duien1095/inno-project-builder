"""Xử lý template: kiểm tra an toàn, tạo thư mục, xác thực."""

from pathlib import Path

from src.excel_generator import generate_excel_for_project
from src.pdf_generator import generate_pdf_from_template


# Danh sách template được sinh file PDF
PDF_TEMPLATE_NAMES = {"QHC", "QHPK", "QHCT"}
PDF_TEMPLATE_FILENAME = "template_pdf.json"
PDF_OUTPUT_FILENAME = "HuongDanLuuTru.pdf"


def generate_pdf_template(
    project_folder: Path,
    template_name: str,
    folder_paths: list[str] | None = None,
    created_files: list[Path] | None = None,
) -> Path | None:
    """Đọc template_pdf.json và sinh file PDF.

    File PDF được lưu vào thư mục template (nếu tìm thấy trong folder_paths).
    Nếu không tìm thấy thư mục template, lưu vào gốc dự án.

    Chỉ sinh cho QHC, QHPK, QHCT. Bỏ qua CONCEPT_*.

    Args:
        project_folder: Thư mục gốc dự án.
        template_name: Tên template.
        folder_paths: Danh sách folder paths từ config (để tìm thư mục đích).
        created_files: List để ghi nhận file đã tạo.

    Returns:
        Đường dẫn file PDF đã tạo, None nếu không tạo.
    """
    if template_name not in PDF_TEMPLATE_NAMES:
        return None

    if created_files is None:
        created_files = []

    # Tìm file template_pdf.json
    source_candidates = [
        Path.cwd() / PDF_TEMPLATE_FILENAME,
        Path(__file__).resolve().parent.parent / PDF_TEMPLATE_FILENAME,
    ]

    json_path: Path | None = None
    for candidate in source_candidates:
        if candidate.exists() and candidate.is_file():
            json_path = candidate
            break

    if json_path is None:
        return None

    # Tìm thư mục template trong folder_paths
    target_dir = _find_template_folder(project_folder, folder_paths)
    if target_dir is None:
        target_dir = project_folder

    output_path = target_dir / PDF_OUTPUT_FILENAME
    try:
        generate_pdf_from_template(
            json_path=json_path,
            output_path=output_path,
            project_name=project_folder.name,
        )
        if output_path.exists():
            created_files.append(output_path)
            return output_path
    except Exception:
        pass

    return None


def _find_template_folder(project_folder: Path, folder_paths: list[str] | None) -> Path | None:
    """Tìm thư mục chứa 'TEMPLATE' hoặc 'HUONG_DAN' hoặc 'HDSD' trong folder_paths.

    Nếu không tìm thấy, trả về None (sẽ lưu ở gốc dự án).
    """
    if not folder_paths:
        return None

    for folder_path in folder_paths:
        name_upper = folder_path.upper()
        if "TEMPLATE" in name_upper or "HUONG_DAN" in name_upper or "HDSD" in name_upper:
            target = project_folder / folder_path
            if target.exists() and target.is_dir():
                return target

    return None


def is_safe_template_folder_path(folder_path: str) -> bool:
    """Kiểm tra folder path từ template không sử dụng local absolute path hoặc traversal.

    UNC path (\\\\server\\share) được cho phép nếu nằm trong phạm vi dự án.
    """
    normalized = Path(folder_path)

    # Chặn local absolute path (D:\\..., C:\\...)
    if normalized.is_absolute():
        if normalized.drive and not normalized.drive.startswith("\\\\"):
            return False

    # Chặn path traversal (..)
    if any(part == ".." for part in normalized.parts):
        return False

    # Chặn path bắt đầu bằng / hoặc \ (không phải UNC)
    if folder_path.startswith("/") or (folder_path.startswith("\\") and not folder_path.startswith("\\\\")):
        return False

    return True


def is_unsafe_target_path(project_folder: Path) -> bool:
    """Xác định các đường dẫn không an toàn như ổ gốc hoặc thư mục Projects tổng."""
    resolved = project_folder.resolve()
    anchor = resolved.anchor

    # Drive root như D:\\, E:\\ hoặc UNC root
    if str(resolved).rstrip("\\/") == str(anchor).rstrip("\\/"):
        return True

    name = resolved.name.lower()
    if name in {"projects", "project", "dự án", "projects tổng"}:
        # Chặn khi chọn thư mục Projects tổng dưới ổ gốc
        parent = resolved.parent
        if str(parent).rstrip("\\/") == str(anchor).rstrip("\\/"):
            return True

    return False


def validate_project_folder_path(project_folder: Path) -> None:
    """Đảm bảo thư mục dự án được chọn là thư mục mới hoặc thư mục rỗng.

    Raises:
        ValueError: Nếu đường dẫn không hợp lệ.
    """
    if project_folder.exists() and not project_folder.is_dir():
        raise ValueError(f"Đường dẫn '{project_folder}' không phải là thư mục.")

    if is_unsafe_target_path(project_folder):
        raise ValueError(
            f"Không được chọn thư mục gốc hoặc thư mục tổng rộng '{project_folder}'. "
            "Vui lòng chọn một thư mục dự án riêng biệt."
        )

    if project_folder.exists() and any(project_folder.iterdir()):
        raise ValueError(
            f"Thư mục '{project_folder}' đã tồn tại và không rỗng. "
            "Vui lòng chọn thư mục mới hoặc xóa nội dung hiện tại trước khi khởi tạo."
        )


def create_template_folders(
    project_folder: Path,
    folder_paths: list[str],
    template_name: str | None = None,
    created_dirs: list[Path] | None = None,
    created_files: list[Path] | None = None,
) -> tuple[list[Path], list[Path]]:
    """Tạo các thư mục theo danh sách trong template.

    Args:
        project_folder: Thư mục gốc dự án.
        folder_paths: Danh sách đường dẫn tương đối cần tạo.
        template_name: Tên template (để copy template_pdf.json nếu có).
        created_dirs: List để ghi nhận các thư mục đã tạo mới (optional).
        created_files: List để ghi nhận các file đã tạo mới (optional).

    Returns:
        Tuple (created_dirs, created_files).

    Raises:
        ValueError: Nếu có đường dẫn không hợp lệ hoặc vượt ra ngoài dự án.
    """
    if created_dirs is None:
        created_dirs = []
    if created_files is None:
        created_files = []

    project_resolved = project_folder.resolve()

    for folder_path in folder_paths:
        if not is_safe_template_folder_path(folder_path):
            raise ValueError(f"Template chứa đường dẫn không hợp lệ: '{folder_path}'.")

        target_path = (project_folder / folder_path).resolve()

        # Kiểm tra không vượt ra ngoài thư mục dự án
        if project_resolved not in target_path.parents and project_resolved != target_path:
            raise ValueError(
                f"Template chứa đường dẫn ra ngoài thư mục dự án: '{folder_path}'."
            )

        if not target_path.exists():
            target_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(target_path)

    # Sinh file PDF hướng dẫn lưu trữ cho QHC, QHPK, QHCT
    if template_name and template_name in PDF_TEMPLATE_NAMES:
        generate_pdf_template(project_folder, template_name, folder_paths, created_files)

    # Sinh file Excel bảng tính chỉ tiêu vào thư mục INPUT/PROCESS
    if template_name and template_name in PDF_TEMPLATE_NAMES:
        generate_excel_for_project(
            project_folder,
            template_name,
            folder_paths,
            created_files,
        )

    return created_dirs, created_files


def _format_relative_path(path: Path, base: Path) -> str:
    """Chuẩn hóa đường dẫn tương đối về dạng POSIX (forward slash).

    Trên Windows, Path.relative_to() trả về backslash, cần đổi sang /
    để đồng bộ với folder_paths trong template config.
    """
    try:
        rel = path.relative_to(base)
    except ValueError:
        return str(path)
    return rel.as_posix()


def build_tree_overview_text(
    project_folder: Path,
    template_name: str,
    folder_paths: list[str],
    created_dirs: list[Path],
    created_files: list[Path] | None = None,
) -> str:
    """Tạo nội dung hiển thị tổng quan cây thư mục theo template."""
    lines: list[str] = [
        f"Nơi lưu: {project_folder}",
        f"Template: {template_name}",
        "",
        "Tổng quan cây thư mục:",
    ]

    created_dirs_set = {path.resolve() for path in created_dirs if path.exists()}

    if folder_paths:
        for folder_path in sorted(folder_paths):
            target_path = project_folder / folder_path
            relative_path = _format_relative_path(target_path, project_folder)

            if target_path.exists():
                status = "Đã tạo mới" if target_path.resolve() in created_dirs_set else "Đã có sẵn"
            else:
                status = "Chưa tạo"

            lines.append(f"- {relative_path} [{status}]")
    else:
        lines.append("- Không có thư mục nào trong template.")

    if created_files:
        lines.append("")
        lines.append("Các file đã tạo:")
        for item in sorted(created_files, key=lambda p: str(p)):
            relative_path = _format_relative_path(item, project_folder)
            lines.append(f"- {relative_path}")

    return "\n".join(lines)


def format_created_items(
    project_folder: Path,
    template_name: str,
    created_dirs: list[Path],
    created_files: list[Path],
) -> str:
    """Giữ tương thích với code cũ bằng cách gọi generator tổng quan mới."""
    return build_tree_overview_text(
        project_folder, template_name, [], created_dirs, created_files
    )
