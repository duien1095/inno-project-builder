"""Giao diện chính của ứng dụng INNO PROJECT BUILDER."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src import __version__
from src.config import (
    COLORS,
    FONTS,
    WINDOW_HEIGHT,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    load_templates_config,
    resolve_template_config_path,
    resolve_template_root,
)
from src.template_engine import (
    build_tree_overview_text,
    create_template_folders,
    validate_project_folder_path,
)


class ProjectInitApp:
    """Ứng dụng tạo cấu trúc dự án cho các đồ án quy hoạch."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.project_folder_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="")
        self.selected_template = ""
        self.selected_template_folders: list[str] = []

        self.template_root = resolve_template_root()
        self.template_config_path = resolve_template_config_path()
        self.templates_data: list[dict[str, Any]] = []
        self.template_buttons_frame: ttk.Frame | None = None
        self.confirm_box: tk.Text | None = None
        self.confirm_button: ttk.Button | None = None
        self.logo_image: tk.PhotoImage | None = None

        self._setup_window()
        self.build_ui()
        self.load_templates()

    # ────────────────────── Cài đặt cửa sổ ──────────────────────

    def _setup_window(self) -> None:
        """Cấu hình cửa sổ chính."""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.root.resizable(True, True)
        self.root.configure(bg=COLORS["bg"])
        self._center_window()

    def _center_window(self) -> None:
        """Canh giữa cửa sổ trên màn hình."""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    # ────────────────────── Logo ──────────────────────

    def _load_logo_image(self) -> tk.PhotoImage | None:
        """Tải logo từ file PNG."""
        root_dir = Path(__file__).resolve().parent.parent.parent
        png_path = root_dir / "assets_logo.png"

        if png_path.exists():
            try:
                return tk.PhotoImage(file=str(png_path))
            except Exception:
                return None
        return None

    # ────────────────────── Xây dựng UI ──────────────────────

    def build_ui(self) -> None:
        """Xây dựng giao diện chính."""
        self.root.configure(bg=COLORS["bg"])

        style = ttk.Style(self.root)
        style.theme_use("clam")

        # ── Định nghĩa style ──
        self._configure_styles(style)

        # ── Layout chính ──
        main_frame = ttk.Frame(self.root, padding=18, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True)

        # Header
        self._build_header(main_frame)

        # Left panel
        left_panel = self._build_left_panel(main_frame)

        # Right panel
        right_panel = self._build_right_panel(main_frame)

        # Grid layout
        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(1, weight=1)

        left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        right_panel.grid(row=1, column=1, sticky="nsew", pady=(0, 10))

    def _configure_styles(self, style: ttk.Style) -> None:
        """Cấu hình ttk styles."""
        style.configure("Main.TFrame", background=COLORS["bg"])
        style.configure("PageHeader.TFrame", background=COLORS["card_bg"])
        style.configure(
            "PageHeader.TLabel",
            background=COLORS["card_bg"],
            foreground=COLORS["primary"],
            font=FONTS["header"],
        )
        style.configure(
            "PageSub.TLabel",
            background=COLORS["card_bg"],
            foreground=COLORS["text_secondary"],
            font=FONTS["subheader"],
        )
        style.configure(
            "Card.TFrame",
            background=COLORS["card_bg"],
            bordercolor="#e5e7eb",
            relief="flat",
        )
        style.configure(
            "Card.TLabel",
            background=COLORS["card_bg"],
            foreground=COLORS["text_primary"],
            font=FONTS["card_title"],
        )
        style.configure(
            "Body.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text_secondary"],
            font=FONTS["body"],
        )
        style.configure(
            "Accent.TButton",
            background=COLORS["primary"],
            foreground=COLORS["card_bg"],
            font=FONTS["button"],
            padding=10,
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLORS["primary_hover"]), ("!disabled", COLORS["primary"])],
            foreground=[("!disabled", COLORS["card_bg"])],
        )
        style.configure(
            "Secondary.TButton",
            background=COLORS["button_bg"],
            foreground=COLORS["button_text"],
            font=FONTS["button_small"],
            padding=10,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#e5e7eb"), ("!disabled", COLORS["button_bg"])],
        )
        style.configure(
            "Info.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text_muted"],
            font=FONTS["body_small"],
        )

    def _build_header(self, parent: ttk.Frame) -> ttk.Frame:
        """Xây dựng phần header."""
        header_frame = ttk.Frame(parent, style="PageHeader.TFrame", padding=(18, 16))
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        brand_frame = ttk.Frame(header_frame, style="PageHeader.TFrame")
        brand_frame.pack(side="left", anchor="center")

        # Logo
        self.logo_image = self._load_logo_image()
        if self.logo_image is not None:
            logo_label = tk.Label(brand_frame, image=self.logo_image, bg=COLORS["card_bg"])
            logo_label.image = self.logo_image
            logo_label.pack(side="left", padx=(0, 12), pady=(0, 2))
        else:
            self._draw_default_logo(brand_frame)

        # Title
        title_box = ttk.Frame(brand_frame, style="PageHeader.TFrame")
        title_box.pack(side="left", anchor="w")
        ttk.Label(title_box, text=WINDOW_TITLE, style="PageHeader.TLabel").pack(anchor="w")
        ttk.Label(
            title_box,
            text=f"Khởi tạo cấu trúc dự án chuẩn — v{__version__}",
            style="PageSub.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        # Status
        status_frame = ttk.Frame(header_frame, style="PageHeader.TFrame")
        status_frame.pack(side="right", anchor="center")
        ttk.Label(status_frame, textvariable=self.status_var, style="PageSub.TLabel").pack(anchor="e")

        return header_frame

    def _draw_default_logo(self, parent: ttk.Frame) -> None:
        """Vẽ logo mặc định khi không tìm thấy file ảnh."""
        logo_canvas = tk.Canvas(
            parent, width=46, height=46, bg=COLORS["card_bg"], highlightthickness=0
        )
        logo_canvas.create_oval(4, 4, 42, 42, fill=COLORS["primary"], outline="")
        logo_canvas.create_text(23, 26, text="D", fill=COLORS["card_bg"], font=("Segoe UI", 18, "bold"))
        logo_canvas.pack(side="left", padx=(0, 12), pady=(0, 2))

    # ────────────────────── Panel trái ──────────────────────

    def _build_left_panel(self, parent: ttk.Frame) -> ttk.Frame:
        """Xây dựng panel bên trái (chọn thư mục + template)."""
        left_panel = ttk.Frame(parent, style="Card.TFrame", padding=18)

        # --- Chọn thư mục ---
        ttk.Label(left_panel, text="Thư mục dự án", style="Card.TLabel").pack(anchor="w")
        ttk.Label(
            left_panel,
            text="Chọn đường dẫn trống để khởi tạo cấu trúc",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(4, 10))

        entry = ttk.Entry(left_panel, textvariable=self.project_folder_var, font=FONTS["entry"])
        entry.pack(fill="x", pady=(0, 14))

        button_row = ttk.Frame(left_panel, style="Card.TFrame")
        button_row.pack(fill="x")
        ttk.Button(
            button_row,
            text="CHỌN THƯ MỤC",
            command=self.select_project_folder,
            style="Accent.TButton",
        ).pack(side="left")
        ttk.Button(
            button_row,
            text="MỞ THƯ MỤC",
            command=self.open_project_folder,
            style="Secondary.TButton",
        ).pack(side="left", padx=(10, 0))

        # --- Chọn template ---
        template_frame = ttk.Frame(left_panel, style="Card.TFrame", padding=(0, 18))
        template_frame.pack(fill="both", expand=True, pady=(14, 0))
        ttk.Label(template_frame, text="CHỌN LOẠI ĐỒ ÁN", style="Card.TLabel").pack(anchor="w")
        ttk.Label(
            template_frame,
            text="Chọn template phù hợp để tạo nhanh cấu trúc dự án.",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(4, 10))

        self.template_buttons_frame = ttk.Frame(template_frame, style="Card.TFrame")
        self.template_buttons_frame.pack(fill="x")

        return left_panel

    # ────────────────────── Panel phải ──────────────────────

    def _build_right_panel(self, parent: ttk.Frame) -> ttk.Frame:
        """Xây dựng panel bên phải (thông tin xác nhận)."""
        right_panel = ttk.Frame(parent, style="Card.TFrame", padding=18)

        ttk.Label(right_panel, text="THÔNG TIN XÁC NHẬN", style="Card.TLabel").pack(anchor="w")
        ttk.Label(
            right_panel,
            text="Xem lại trước khi nhấn KHỞI TẠO.",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(4, 10))

        self.confirm_box = tk.Text(
            right_panel,
            height=22,
            wrap="word",
            font=FONTS["result"],
            bg=COLORS["result_bg"],
            fg=COLORS["text_primary"],
            bd=0,
            relief="flat",
            padx=10,
            pady=10,
        )
        self.confirm_box.pack(fill="both", expand=True)
        self.confirm_box.config(state="disabled")

        self.confirm_button = ttk.Button(
            right_panel,
            text="KHỞI TẠO",
            command=self.on_confirm_create,
            style="Accent.TButton",
        )
        self.confirm_button.pack(anchor="e", pady=(12, 0))
        self.confirm_button.state(["disabled"])

        return right_panel

    # ────────────────────── Template ──────────────────────

    def load_templates(self) -> list[str]:
        """Đọc danh sách template từ file JSON và tạo các nút."""
        self.templates_data = load_templates_config(self.template_config_path)
        templates = [item["template_name"] for item in self.templates_data]

        if not templates:
            self.show_error(
                "Không tìm thấy template nào trong file templates_config.json."
            )

        self._create_template_buttons(templates)
        return templates

    def _create_template_buttons(self, templates: list[str]) -> None:
        """Tạo các nút template động."""
        if self.template_buttons_frame is None:
            return

        # Xoá nút cũ
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
                bg=COLORS["button_bg"],
                fg=COLORS["button_text"],
                bd=1,
                padx=8,
                pady=8,
                font=FONTS["template_button"],
            )
            button.grid(row=row, column=column, padx=6, pady=6, sticky="nsew")

        for col in range(columns):
            self.template_buttons_frame.columnconfigure(col, weight=1)

    # ────────────────────── Sự kiện ──────────────────────

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
        """Chọn loại đồ án và hiển thị thông tin xác nhận."""
        self.selected_template = template_name
        self.selected_template_folders = []

        for item in self.templates_data:
            if item.get("template_name") == template_name:
                self.selected_template_folders = [str(f) for f in item.get("folders", [])]
                break

        project_folder_str = self.project_folder_var.get().strip()
        if not project_folder_str:
            self.show_error("Vui lòng chọn thư mục dự án trước khi chọn template.")
            return

        project_folder = Path(project_folder_str)
        self.status_var.set(f"Đã chọn template: {template_name}")
        self._update_confirmation_panel(project_folder, template_name, self.selected_template_folders)

    def on_confirm_create(self) -> None:
        """Tạo thư mục sau khi người dùng đã xem thông tin."""
        project_folder_str = self.project_folder_var.get().strip()
        if not project_folder_str or not self.selected_template:
            self.show_error("Vui lòng chọn thư mục dự án và template trước khi khởi tạo.")
            return

        if not self.selected_template_folders:
            self.show_error("Không có danh sách thư mục để tạo. Vui lòng chọn lại template.")
            return

        self._initialize_project()

    # ────────────────────── Xử lý chính ──────────────────────

    def _initialize_project(self) -> None:
        """Tạo thư mục dự án theo template đã chọn."""
        try:
            project_folder, folders = self._validate_inputs()
            created_dirs, created_files = create_template_folders(
                project_folder, folders, template_name=self.selected_template
            )
            self._show_result(project_folder, created_dirs, created_files)
        except ValueError as exc:
            self.show_error(str(exc))
        except Exception as exc:
            self.show_error(f"Lỗi tạo thư mục: {exc}")
        else:
            self.show_success("Khởi tạo dự án thành công.")
            if self.confirm_button is not None:
                self.confirm_button.state(["disabled"])

    def _validate_inputs(self) -> tuple[Path, list[str]]:
        """Kiểm tra đầu vào trước khi khởi tạo.

        Returns:
            (project_folder, folders) nếu hợp lệ.

        Raises:
            ValueError: Nếu đầu vào không hợp lệ.
        """
        project_folder_str = self.project_folder_var.get().strip()
        if not project_folder_str:
            raise ValueError("Vui lòng chọn thư mục dự án.")

        project_folder = Path(project_folder_str)

        if not self.selected_template:
            raise ValueError("Vui lòng chọn loại đồ án.")

        validate_project_folder_path(project_folder)

        folders = self.selected_template_folders
        project_folder.mkdir(parents=True, exist_ok=True)

        return project_folder, folders

    def _show_result(
        self,
        project_folder: Path,
        created_dirs: list[Path],
        created_files: list[Path],
    ) -> None:
        """Hiển thị tổng quan cây thư mục trên giao diện."""
        content = build_tree_overview_text(
            project_folder,
            self.selected_template,
            self.selected_template_folders,
            created_dirs,
            created_files,
        )
        if self.confirm_box is None:
            return
        self.confirm_box.config(state="normal")
        self.confirm_box.delete("1.0", "end")
        self.confirm_box.insert("1.0", content)
        self.confirm_box.config(state="disabled")

    def _update_confirmation_panel(
        self,
        project_folder: Path,
        template_name: str,
        folder_paths: list[str],
    ) -> None:
        """Cập nhật thông tin xác nhận trong panel phải."""
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

    # ────────────────────── Thông báo ──────────────────────

    def show_success(self, message: str) -> None:
        """Hiển thị thông báo thành công."""
        self.status_var.set(message)
        messagebox.showinfo("Thành công", message)

    def show_error(self, message: str) -> None:
        """Hiển thị thông báo lỗi."""
        self.status_var.set(message)
        messagebox.showerror("Lỗi", message)
