import json
import os
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any

__version__ = "0.1.0"

def build_tree_overview_text(
    project_folder: Path,
    template_name: str,
    folder_paths: list[str],
    created_dirs: list[Path],
    created_files: list[Path] | None = None,
) -> str:
    """Tạo nội dung hiển thị tổng quan cây thư mục theo template."""
    lines: list[str] = [f"Nơi lưu: {project_folder}", f"Template: {template_name}", "", "Tổng quan cây thư mục:"]

    created_dirs_set = {path.resolve() for path in created_dirs}
    if folder_paths:
        for folder_path in sorted(folder_paths):
            target_path = project_folder / folder_path
            try:
                relative_path = target_path.relative_to(project_folder)
            except ValueError:
                relative_path = target_path

            if target_path.resolve() in created_dirs_set:
                status = "Đã tạo mới"
            elif target_path.exists():
                status = "Đã có sẵn"
            else:
                status = "Chưa tạo"

            display_path = str(relative_path).replace("\\", "/")
            lines.append(f"- {display_path} [{status}]")
    else:
        lines.append("- Không có thư mục nào trong template.")

    if created_files:
        lines.append("")
        lines.append("Các file đã tạo:")
        for item in sorted(created_files, key=lambda p: str(p)):
            try:
                relative_path = item.relative_to(project_folder)
            except ValueError:
                relative_path = item
            lines.append(f"- {relative_path}")

    return "\n".join(lines)


def format_created_items(project_folder: Path, template_name: str, created_dirs: list[Path], created_files: list[Path]) -> str:
    """Giữ tương thích với code cũ bằng cách gọi generator tổng quan mới."""
    return build_tree_overview_text(project_folder, template_name, [], created_dirs, created_files)


def is_unsafe_target_path(project_folder: Path) -> bool:
    """Xác định các đường dẫn không an toàn như ổ gốc hoặc thư mục Projects tổng."""
    resolved = project_folder.resolve()
    anchor = resolved.anchor

    # Drive root như D:\, E:\ hoặc UNC root
    if str(resolved).rstrip("\\/") == str(anchor).rstrip("\\/"):
        return True

    name = resolved.name.lower()
    if name in {"projects", "project", "dự án", "projects tổng"}:
        # Chặn khi người dùng chọn thư mục Projects tổng dưới ổ gốc hoặc share root
        parent = resolved.parent
        if str(parent).rstrip("\\/") == str(anchor).rstrip("\\/"):
            return True

    return False


def validate_project_folder_path(project_folder: Path) -> None:
    """Đảm bảo thư mục dự án được chọn là thư mục mới hoặc thư mục rỗng."""
    if project_folder.exists() and not project_folder.is_dir():
        raise ValueError(f"Đường dẫn '{project_folder}' không phải là thư mục.")

    if is_unsafe_target_path(project_folder):
        raise ValueError(
            f"Không được chọn thư mục gốc hoặc thư mục tổng rộng '{project_folder}'. "
            "Vui lòng chọn một thư mục dự án riêng biệt.")

    if project_folder.exists() and any(project_folder.iterdir()):
        raise ValueError(
            f"Thư mục '{project_folder}' đã tồn tại và không rỗng. "
            "Vui lòng chọn thư mục mới hoặc xóa nội dung hiện tại trước khi khởi tạo."
        )


def is_safe_template_folder_path(folder_path: str) -> bool:
    """Kiểm tra folder path từ template không sử dụng local absolute path hoặc traversal.

    UNC path (\\server\share) được cho phép nếu nằm trong phạm vi dự án.
    """
    normalized = Path(folder_path)
    if normalized.is_absolute():
        # Cho phép UNC path, chặn local absolute như D:\...
        if normalized.drive and not normalized.drive.startswith("\\\\"):
            return False

    if any(part == ".." for part in normalized.parts):
        return False

    if folder_path.startswith("/") or (folder_path.startswith("\\") and not folder_path.startswith("\\\\")):
        return False

    return True


class ProjectInitApp:
    """Ứng dụng tạo cấu trúc dự án cho các đồ án quy hoạch."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.project_folder_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="")
        self.result_text = tk.StringVar(value="")
        self.selected_template = ""
        self.selected_template_folders: list[str] = []
        self.template_root = self.resolve_template_root()
        self.template_config_path = self.resolve_template_config_path()
        self.templates_data: list[dict[str, Any]] = []
        self.template_buttons_frame: ttk.Frame | None = None
        self.result_box: tk.Text | None = None
        self.logo_image: tk.PhotoImage | None = None

        self.root.title("INNO PROJECT BUILDER")
        self.root.geometry("920x700")
        self.root.minsize(780, 620)
        self.root.resizable(True, True)
        self.root.configure(bg="#f5f5f7")
        self.center_window()

        self.build_ui()
        self.load_templates()

    def center_window(self) -> None:
        """Canh giữa cửa sổ trên màn hình."""
        self.root.update_idletasks()
        width = 920
        height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def load_logo_image(self) -> tk.PhotoImage | None:
        """Tải logo từ file PNG chuẩn hoặc dùng icon mặc định nếu không tìm thấy."""
        root_dir = Path(__file__).resolve().parent
        png_path = root_dir / "assets_logo.png"

        if png_path.exists():
            try:
                return tk.PhotoImage(file=str(png_path))
            except Exception:
                return None

        return None

    def build_ui(self) -> None:
        """Xây dựng giao diện chính."""
        self.root.configure(bg="#f5f5f7")

        style = ttk.Style(self.root)

        main_frame = ttk.Frame(self.root, padding=18, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True)

        style.theme_use("clam")
        style.theme_use("clam")
        style.configure("Main.TFrame", background="#f5f5f7")
        style.configure("PageHeader.TFrame", background="#ffffff")
        style.configure("PageHeader.TLabel", background="#ffffff", foreground="#d71b24", font=("Segoe UI", 20, "bold"))
        style.configure("PageSub.TLabel", background="#ffffff", foreground="#4b5563", font=("Segoe UI", 10))
        style.configure("Card.TFrame", background="#ffffff", bordercolor="#e5e7eb", relief="flat")
        style.configure("Card.TLabel", background="#ffffff", foreground="#1f2937", font=("Segoe UI", 11, "bold"))
        style.configure("Body.TLabel", background="#f5f5f7", foreground="#4b5563", font=("Segoe UI", 10))
        style.configure("Accent.TButton", background="#d71b24", foreground="#ffffff", font=("Segoe UI", 11, "bold"), padding=10)
        style.map("Accent.TButton", background=[("active", "#b0161d"), ("!disabled", "#d71b24")], foreground=[("!disabled", "#ffffff")])
        style.configure("Secondary.TButton", background="#f3f4f6", foreground="#111827", font=("Segoe UI", 10, "bold"), padding=10)
        style.map("Secondary.TButton", background=[("active", "#e5e7eb"), ("!disabled", "#f3f4f6")])
        style.configure("Info.TLabel", background="#f5f5f7", foreground="#6b7280", font=("Segoe UI", 9))

        header_frame = ttk.Frame(main_frame, style="PageHeader.TFrame", padding=(18, 16))
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        brand_frame = ttk.Frame(header_frame, style="PageHeader.TFrame")
        brand_frame.pack(side="left", anchor="center")

        self.logo_image = self.load_logo_image()
        if self.logo_image is not None:
            logo_label = tk.Label(brand_frame, image=self.logo_image, bg="#ffffff")
            logo_label.image = self.logo_image
            logo_label.pack(side="left", padx=(0, 12), pady=(0, 2))
        else:
            logo_canvas = tk.Canvas(brand_frame, width=46, height=46, bg="#ffffff", highlightthickness=0)
            logo_canvas.create_oval(4, 4, 42, 42, fill="#d71b24", outline="")
            logo_canvas.create_text(23, 26, text="D", fill="#ffffff", font=("Segoe UI", 18, "bold"))
            logo_canvas.pack(side="left", padx=(0, 12), pady=(0, 2))

        title_box = ttk.Frame(brand_frame, style="PageHeader.TFrame")
        title_box.pack(side="left", anchor="w")
        ttk.Label(title_box, text="INNO PROJECT BUILDER", style="PageHeader.TLabel").pack(anchor="w")
        ttk.Label(title_box, text=f"Khởi tạo cấu trúc dự án chuẩn — v{__version__}", style="PageSub.TLabel").pack(anchor="w", pady=(2, 0))

        status_frame = ttk.Frame(header_frame, style="PageHeader.TFrame")
        status_frame.pack(side="right", anchor="center")
        ttk.Label(status_frame, textvariable=self.status_var, style="PageSub.TLabel").pack(anchor="e")

        left_panel = ttk.Frame(main_frame, style="Card.TFrame", padding=18)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        ttk.Label(left_panel, text="Thư mục dự án", style="Card.TLabel").pack(anchor="w")
        ttk.Label(left_panel, text="Chọn đường dẫn trống để khởi tạo cấu trúc", style="Body.TLabel").pack(anchor="w", pady=(4, 10))

        entry = ttk.Entry(left_panel, textvariable=self.project_folder_var, font=("Segoe UI", 11))
        entry.pack(fill="x", pady=(0, 14))

        button_row = ttk.Frame(left_panel, style="Card.TFrame")
        button_row.pack(fill="x")
        ttk.Button(button_row, text="CHỌN THƯ MỤC", command=self.select_project_folder, style="Accent.TButton").pack(side="left")
        ttk.Button(button_row, text="MỞ THƯ MỤC", command=self.open_project_folder, style="Secondary.TButton").pack(side="left", padx=(10, 0))

        template_frame = ttk.Frame(left_panel, style="Card.TFrame", padding=18)
        template_frame.pack(fill="both", expand=True, pady=(14, 0))
        ttk.Label(template_frame, text="CHỌN LOẠI ĐỒ ÁN", style="Card.TLabel").pack(anchor="w")
        ttk.Label(template_frame, text="Chọn template phù hợp để tạo nhanh cấu trúc dự án.", style="Body.TLabel").pack(anchor="w", pady=(4, 10))

        self.template_buttons_frame = ttk.Frame(template_frame, style="Card.TFrame")
        self.template_buttons_frame.pack(fill="x")

        result_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=18)
        result_frame.grid(row=1, column=1, sticky="nsew", pady=(0, 10))
        ttk.Label(result_frame, text="THÔNG TIN XÁC NHẬN", style="Card.TLabel").pack(anchor="w")
        ttk.Label(result_frame, text="Xem lại trước khi nhấn KHỞI TẠO.", style="Body.TLabel").pack(anchor="w", pady=(4, 10))

        self.confirm_box = tk.Text(result_frame, height=22, wrap="word", font=("Segoe UI", 10), bg="#f8fafc", fg="#1f2937", bd=0, relief="flat", padx=10, pady=10)
        self.confirm_box.pack(fill="both", expand=True)
        self.confirm_box.config(state="disabled")

        self.confirm_button = ttk.Button(result_frame, text="KHỞI TẠO", command=self.on_confirm_create, style="Accent.TButton")
        self.confirm_button.pack(anchor="e", pady=(12, 0))
        self.confirm_button.state(["disabled"])

        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(1, weight=1)

    def resolve_template_root(self) -> Path:
        """Tìm thư mục template theo thứ tự ưu tiên."""
        env_path = os.environ.get("PROJECT_INIT_TEMPLATE_ROOT", "").strip()
        candidates: list[Path] = []

        if env_path:
            candidates.append(Path(env_path).expanduser())

        candidates.extend(
            [
                Path(r"D:\00_COMPANY_STANDARD\TEMPLATE"),
                Path(__file__).resolve().parent / "templates",
                Path.cwd() / "templates",
            ]
        )

        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate

        return Path(r"D:\00_COMPANY_STANDARD\TEMPLATE")

    def resolve_template_config_path(self) -> Path:
        """Tìm file cấu hình template JSON nếu có."""
        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        candidates = [
            base_dir / "templates_config.json",
            base_dir / "templates.json",
            base_dir / "templates" / "templates.json",
            Path.cwd() / "templates_config.json",
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate
        return base_dir / "templates_config.json"

    def load_templates(self) -> list[str]:
        """Đọc danh sách template từ file JSON và tạo các nút template tương ứng."""
        templates: list[str] = []
        config_data: dict[str, Any] = {"templates": []}

        if self.template_config_path.exists() and self.template_config_path.is_file():
            try:
                with self.template_config_path.open("r", encoding="utf-8") as handle:
                    config_data = json.load(handle)
            except Exception:
                self.show_error("Không đọc được file templates_config.json. Vui lòng kiểm tra định dạng JSON.")
                config_data = {"templates": []}
        else:
            self.show_error("Không tìm thấy file templates_config.json.")

        self.templates_data = [
            {
                "template_name": item.get("template_name", ""),
                "folders": item.get("folders", []),
            }
            for item in config_data.get("templates", [])
            if isinstance(item, dict)
        ]
        templates = [item["template_name"] for item in self.templates_data if item.get("template_name")]

        if not templates:
            self.show_error("Không tìm thấy template nào trong file templates_config.json.")

        self.create_template_buttons(templates)
        return templates

    def create_template_buttons(self, templates: list[str]) -> None:
        """Tạo các nút template động theo thư mục thực tế."""
        if self.template_buttons_frame is None:
            return

        for widget in self.template_buttons_frame.winfo_children():
            widget.destroy()

        if not templates:
            ttk.Label(
                self.template_buttons_frame,
                text="Không có template nào được tìm thấy.",
                foreground="gray",
            ).pack(anchor="center", pady=20)
            return

        columns = 3
        for index, template_name in enumerate(templates):
            row = index // columns
            column = index % columns
            button = tk.Button(
                self.template_buttons_frame,
                text=template_name,
                command=lambda name=template_name: self.select_template(name),
                width=28,
                wraplength=220,
                justify="center",
                anchor="center",
                relief="raised",
                bg="#f3f4f6",
                fg="#111827",
                bd=1,
                padx=8,
                pady=8,
                font=("Segoe UI", 10, "normal"),
            )
            button.grid(row=row, column=column, padx=6, pady=6, sticky="nsew")

        for column in range(columns):
            self.template_buttons_frame.columnconfigure(column, weight=1)

    def select_project_folder(self) -> None:
        """Cho phép người dùng chọn thư mục dự án."""
        folder = filedialog.askdirectory(title="Chọn thư mục dự án", mustexist=False)
        if folder:
            self.project_folder_var.set(folder)
            self.status_var.set(f"Đã chọn thư mục dự án: {folder}")

    def open_project_folder(self) -> None:
        """Mở thư mục dự án bằng File Explorer."""
        project_folder = Path(self.project_folder_var.get().strip())
        if not project_folder.exists():
            self.show_error("Vui lòng chọn thư mục dự án trước.")
            return
        os.startfile(str(project_folder))

    def select_template(self, template_name: str) -> None:
        """Chọn loại đồ án và hiển thị thông tin xác nhận ngay trên app."""
        self.selected_template = template_name
        self.selected_template_folders = []

        for item in self.templates_data:
            if item.get("template_name") == template_name:
                self.selected_template_folders = [str(folder) for folder in item.get("folders", [])]
                break

        project_folder_str = self.project_folder_var.get().strip()
        if not project_folder_str:
            self.show_error("Vui lòng chọn thư mục dự án trước khi chọn template.")
            return

        project_folder = Path(project_folder_str)
        self.status_var.set(f"Đã chọn template: {template_name}")
        self.update_confirmation_panel(project_folder, template_name, self.selected_template_folders)

    def validate_inputs(self) -> tuple[Path, list[str]]:
        """Kiểm tra đầu vào trước khi khởi tạo."""
        project_folder_str = self.project_folder_var.get().strip()
        if not project_folder_str:
            raise ValueError("Vui lòng chọn thư mục dự án.")

        project_folder = Path(project_folder_str)

        if not self.selected_template:
            raise ValueError("Vui lòng chọn loại đồ án.")

        validate_project_folder_path(project_folder)

        if self.templates_data:
            template_folders = [
                item.get("folders", [])
                for item in self.templates_data
                if item.get("template_name") == self.selected_template
            ]
            if not template_folders:
                raise ValueError("Không tìm thấy template.")
            folders = [str(folder) for folder in self.selected_template_folders]
        else:
            template_dir = self.template_root / self.selected_template
            if not template_dir.exists() or not template_dir.is_dir():
                raise ValueError("Không tìm thấy template.")
            folders = [self.selected_template]

        project_folder.mkdir(parents=True, exist_ok=True)

        return project_folder, folders

    def initialize_project(self) -> None:
        """Tạo thư mục dự án theo template đã chọn."""
        try:
            project_folder, folders = self.validate_inputs()
            created_dirs: list[Path] = []
            self.create_template_folders(project_folder, folders, created_dirs)
            self.show_result(project_folder, created_dirs, [])
        except ValueError as exc:
            self.show_error(str(exc))
        except Exception as exc:  # pragma: no cover - xử lý lỗi chung
            self.show_error(f"Lỗi tạo thư mục: {exc}")
        else:
            self.show_success("Khởi tạo dự án thành công.")
            if self.confirm_button is not None:
                self.confirm_button.state(["disabled"])

    def open_created_project_folder(self, project_folder: Path) -> None:
        """Mở thư mục dự án vừa tạo bằng File Explorer."""
        if not project_folder.exists():
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(str(project_folder))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(project_folder)])
            else:
                subprocess.Popen(["xdg-open", str(project_folder)])
        except Exception:
            self.status_var.set(f"Đã tạo xong, nhưng không mở được thư mục: {project_folder}")

    def create_template_folders(self, project_folder: Path, folder_paths: list[str], created_dirs: list[Path]) -> None:
        """Tạo các thư mục theo danh sách trong template."""
        for folder_path in folder_paths:
            if not is_safe_template_folder_path(folder_path):
                raise ValueError(f"Template chứa đường dẫn không hợp lệ: '{folder_path}'.")

            target_path = project_folder / folder_path
            target_path = target_path.resolve()
            if project_folder.resolve() not in target_path.parents and project_folder.resolve() != target_path:
                raise ValueError(f"Template chứa đường dẫn ra ngoài thư mục dự án: '{folder_path}'.")

            if not target_path.exists():
                target_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(target_path)

    def show_result(self, project_folder: Path, created_dirs: list[Path], created_files: list[Path]) -> None:
        """Hiển thị tổng quan cây thư mục và kết quả tạo trên giao diện."""
        content = build_tree_overview_text(
            project_folder,
            self.selected_template,
            self.selected_template_folders,
            created_dirs,
            created_files,
        )
        self.update_result_box(content)

    def update_result_box(self, content: str) -> None:
        """Cập nhật nội dung khung kết quả."""
        if self.result_box is None:
            return
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", content)
        self.result_box.config(state="disabled")

    def update_confirmation_panel(self, project_folder: Path, template_name: str, folder_paths: list[str]) -> None:
        """Cập nhật thông tin xác nhận ngay trong giao diện chính."""
        if self.confirm_box is None or self.confirm_button is None:
            return

        summary_lines = [
            f"Đường dẫn: {project_folder}",
            f"Tên dự án: {project_folder.name or project_folder.drive}",
            f"Template: {template_name}",
            f"Tổng số thư mục sẽ tạo: {len(folder_paths)}",
            "",
            "Danh sách thư mục:",
        ]
        summary_lines.extend(f"- {folder_path}" for folder_path in folder_paths)
        content = "\n".join(summary_lines)

        self.confirm_box.config(state="normal")
        self.confirm_box.delete("1.0", "end")
        self.confirm_box.insert("1.0", content)
        self.confirm_box.config(state="disabled")

        self.confirm_button.state(["!disabled"])

    def on_confirm_create(self) -> None:
        """Tạo thư mục sau khi người dùng đã xem thông tin ngay trên app."""
        project_folder_str = self.project_folder_var.get().strip()
        if not project_folder_str or not self.selected_template:
            self.show_error("Vui lòng chọn thư mục dự án và template trước khi khởi tạo.")
            return

        if not self.selected_template_folders:
            self.show_error("Không có danh sách thư mục để tạo. Vui lòng chọn lại template.")
            return

        self.initialize_project()

    def show_success(self, message: str) -> None:
        """Hiển thị thông báo thành công."""
        self.status_var.set(message)
        messagebox.showinfo("Thành công", message)

    def show_error(self, message: str) -> None:
        """Hiển thị thông báo lỗi."""
        self.status_var.set(message)
        messagebox.showerror("Lỗi", message)


def main() -> None:
    """Khởi động ứng dụng."""
    root = tk.Tk()
    app = ProjectInitApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
