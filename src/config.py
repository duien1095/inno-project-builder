"""Cấu hình và hằng số cho ứng dụng."""

import json
import os
import sys
from pathlib import Path
from typing import Any


# ---- Đường dẫn mặc định ----
DEFAULT_TEMPLATE_ROOT = Path(r"D:\00_COMPANY_STANDARD\TEMPLATE")
ENV_TEMPLATE_ROOT_VAR = "PROJECT_INIT_TEMPLATE_ROOT"

# ---- Tên file cấu hình ----
TEMPLATE_CONFIG_FILENAMES = [
    "templates_config.json",
    "templates.json",
]

# ---- Giao diện ----
WINDOW_TITLE = "INNO PROJECT BUILDER"
WINDOW_WIDTH = 920
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 780
WINDOW_MIN_HEIGHT = 620

# ---- Màu sắc ----
COLORS = {
    "bg": "#f5f5f7",
    "card_bg": "#ffffff",
    "primary": "#d71b24",
    "primary_hover": "#b0161d",
    "text_primary": "#1f2937",
    "text_secondary": "#4b5563",
    "text_muted": "#6b7280",
    "text_light": "#9ca3af",
    "button_bg": "#f3f4f6",
    "button_text": "#111827",
    "result_bg": "#f8fafc",
}

# ---- Font ----
FONTS = {
    "header": ("Segoe UI", 20, "bold"),
    "subheader": ("Segoe UI", 10),
    "card_title": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "body_small": ("Segoe UI", 9),
    "entry": ("Segoe UI", 11),
    "button": ("Segoe UI", 11, "bold"),
    "button_small": ("Segoe UI", 10, "bold"),
    "result": ("Segoe UI", 10),
    "template_button": ("Segoe UI", 10, "normal"),
}


def resolve_template_root() -> Path:
    """Tìm thư mục template theo thứ tự ưu tiên."""
    env_path = os.environ.get(ENV_TEMPLATE_ROOT_VAR, "").strip()
    candidates: list[Path] = []

    if env_path:
        candidates.append(Path(env_path).expanduser())

    candidates.extend(
        [
            DEFAULT_TEMPLATE_ROOT,
            Path(__file__).resolve().parent.parent / "templates",
            Path.cwd() / "templates",
        ]
    )

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate

    return DEFAULT_TEMPLATE_ROOT


def resolve_template_config_path() -> Path:
    """Tìm file cấu hình template JSON."""
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    candidates: list[Path] = []

    for filename in TEMPLATE_CONFIG_FILENAMES:
        candidates.extend([
            base_dir / filename,
            base_dir / "templates" / filename,
            Path.cwd() / filename,
        ])

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return base_dir / TEMPLATE_CONFIG_FILENAMES[0]


def load_templates_config(config_path: Path) -> list[dict[str, Any]]:
    """Đọc danh sách template từ file JSON.

    Returns:
        Danh sách dict, mỗi dict có 'template_name' (str) và 'folders' (list[str]).
    """
    if not config_path.exists() or not config_path.is_file():
        return []

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config_data = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return []

    return [
        {
            "template_name": item.get("template_name", ""),
            "folders": [str(f) for f in item.get("folders", [])],
        }
        for item in config_data.get("templates", [])
        if isinstance(item, dict) and item.get("template_name")
    ]
