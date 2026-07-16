#!/usr/bin/env python3
"""Build PDF hướng dẫn lưu trữ từ file JSON — gói gọn trong 1 trang A4.

Usage:
    python build_pdf.py template_pdf.json [output.pdf]
"""

import json
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ═══════════════════════════ Đăng ký font ═══════════════════════════

# Arial có sẵn trên Windows, hỗ trợ tiếng Việt đầy đủ
_FONT_PATHS = [
    ("DejaVuSans", "DejaVuSans-Bold", [
        r"C:\Windows\Fonts\DejaVuSans.ttf",
        r"C:\Windows\Fonts\DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/Library/Fonts/DejaVuSans.ttf",
        "/Library/Fonts/DejaVuSans-Bold.ttf",
    ]),
    ("Arial", "Arial-Bold", [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
    ]),
    ("TimesNewRoman", "TimesNewRoman-Bold", [
        r"C:\Windows\Fonts\times.ttf",
        r"C:\Windows\Fonts\timesbd.ttf",
    ]),
]

_REGISTERED = False
_FONT_NAME = "Helvetica"
_FONT_BOLD_NAME = "Helvetica-Bold"


def _register_fonts():
    global _REGISTERED, _FONT_NAME, _FONT_BOLD_NAME

    if _REGISTERED:
        return

    for font_name, bold_name, paths in _FONT_PATHS:
        reg, reg_b = None, None
        for p in paths:
            path = Path(p)
            if path.exists():
                is_bold = "Bold" in p or "bold" in p or "bd" in p.replace("arialbd", "bd")
                if is_bold:
                    reg_b = str(path)
                else:
                    reg = str(path)
        if reg:
            try:
                pdfmetrics.registerFont(TTFont(font_name, reg))
                if reg_b:
                    pdfmetrics.registerFont(TTFont(bold_name, reg_b))
                else:
                    pdfmetrics.registerFont(TTFont(bold_name, reg))
                pdfmetrics.registerFontFamily(
                    font_name,
                    normal=font_name,
                    bold=bold_name,
                )
                _FONT_NAME = font_name
                _FONT_BOLD_NAME = bold_name
                _REGISTERED = True
                return
            except Exception:
                continue

    # Fallback: dùng Helvetica (không hỗ trợ TV nhưng đỡ crash)
    _FONT_NAME = "Helvetica"
    _FONT_BOLD_NAME = "Helvetica-Bold"
    _REGISTERED = True


# ═══════════════════════════ Màu sắc ═══════════════════════════

NAVY = HexColor("#1F4E78")
LIGHT_BLUE = HexColor("#D9E1F2")
LIGHT_GRAY = HexColor("#F2F2F2")
WHITE = white
GRAY_LINE = HexColor("#CCCCCC")
DARK_GRAY = HexColor("#333333")

# ═══════════════════════════ Styles ═══════════════════════════

_register_fonts()

FN = _FONT_NAME
FB = _FONT_BOLD_NAME


def _make_styles():
    return {
        "DocTitle": ParagraphStyle(
            "DocTitle",
            fontName=FB,
            fontSize=11,
            leading=13,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=2,
            spaceBefore=0,
        ),
        "DocSub": ParagraphStyle(
            "DocSub",
            fontName=FN,
            fontSize=7,
            leading=9,
            textColor=DARK_GRAY,
            alignment=TA_CENTER,
            spaceAfter=2,
            spaceBefore=0,
        ),
        "SectionTitle": ParagraphStyle(
            "SectionTitle",
            fontName=FB,
            fontSize=7.5,
            leading=9,
            textColor=WHITE,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            leftIndent=3,
        ),
        "CellNormal": ParagraphStyle(
            "CellNormal",
            fontName=FN,
            fontSize=6.5,
            leading=7.5,
            textColor=DARK_GRAY,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "CellBold": ParagraphStyle(
            "CellBold",
            fontName=FB,
            fontSize=6.5,
            leading=7.5,
            textColor=DARK_GRAY,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "TableHeader": ParagraphStyle(
            "TableHeader",
            fontName=FB,
            fontSize=6.5,
            leading=7.5,
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "SubHeader": ParagraphStyle(
            "SubHeader",
            fontName=FB,
            fontSize=6.5,
            leading=7.5,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=0,
        ),
    }


S = None  # sẽ gán sau khi _make_styles()


def P(name, text):
    return Paragraph(str(text), S[name])


# ═══════════════════════════ Xây mô tả item ═══════════════════════════

def _build_item_desc(item: dict) -> str:
    """Gộp description, naming_rule, example, subfolders thành 1 chuỗi HTML."""
    parts = []
    desc = item.get("description", "")

    if desc:
        parts.append(desc)

    naming = item.get("naming_rule")
    if naming:
        parts.append(
            f'<font color="#1F4E78"><b>Quy tắc:</b></font> {naming}'
        )

    example = item.get("example")
    if example:
        parts.append(
            f'<font color="#1F4E78"><b>VD:</b></font> {example}'
        )

    subfolders = item.get("subfolders")
    if subfolders:
        subs = " | ".join(subfolders)
        parts.append(
            f'<font color="#1F4E78"><b>Con:</b></font> {subs}'
        )

    return " | ".join(parts)


# ═══════════════════════════ Bảng Tổng quan ═══════════════════════════

OVERVIEW_LABELS = {
    "input": "INPUT — Dữ liệu gốc",
    "process": "PROCESS — Đang xử lý",
    "output": "OUTPUT — Đã hoàn thiện",
    "dl_cap_nhat": "DL_CẬP_NHẬT — Dữ liệu mới",
    "gop_y_hop": "GÓP Ý_HỌP — Biên bản, ý kiến",
}


def _build_overview_table(overview: dict):
    if not overview:
        return None

    data = [
        [P("TableHeader", "NHÓM"), P("TableHeader", "Ý NGHĨA")],
    ]

    for key, desc in overview.items():
        label = OVERVIEW_LABELS.get(key, key)
        data.append([
            P("CellBold", label),
            P("CellNormal", desc),
        ])

    col_widths = [50 * mm, 130 * mm]
    t = Table(data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.4, GRAY_LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), LIGHT_GRAY))
        else:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), WHITE))

    t.setStyle(TableStyle(style_cmds))
    return t


# ═══════════════════════════ Section ═══════════════════════════

def _build_section_table(section: dict):
    name = section.get("name", "")
    items = section.get("items", [])

    if not items:
        return None

    # Thanh tiêu đề
    title_data = [[P("SectionTitle", f"{name}")]]
    title_table = Table(title_data, colWidths=[180 * mm])
    title_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))

    # Header + rows
    header_row = [P("SubHeader", "Thư mục"), P("SubHeader", "Mô tả")]
    col_widths = [42 * mm, 138 * mm]
    data_rows = [header_row]

    for item in items:
        folder = item.get("folder", "")
        desc_html = _build_item_desc(item)
        data_rows.append([
            P("CellBold", folder),
            Paragraph(desc_html, S["CellNormal"]),
        ])

    body_table = Table(data_rows, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, GRAY_LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(data_rows)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), LIGHT_GRAY))
        else:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), WHITE))

    body_table.setStyle(TableStyle(style_cmds))

    # Ghép title + body
    merged = Table([
        [title_table],
        [body_table],
    ], colWidths=[180 * mm])

    merged.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    return merged


# ═══════════════════════════ Header / Footer ═══════════════════════════

def _header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.4)
    canvas.line(15, A4[1] - 15, A4[0] - 15, A4[1] - 15)
    canvas.setFont(FN, 6)
    canvas.setFillColor(HexColor("#888888"))
    canvas.drawCentredString(A4[0] / 2, 10, f"Trang {doc.page}")
    canvas.restoreState()


# ═══════════════════════════ Hàm chính ═══════════════════════════

def build_pdf(json_path: Path, output_path: Path | None = None) -> Path:
    """Đọc file JSON, sinh PDF gói gọn trong 1 trang A4."""
    global S
    _register_fonts()
    S = _make_styles()

    if not json_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    document_name = data.get("document_name", "HƯỚNG DẪN LƯU TRỮ")
    version = data.get("version", "1.0")
    overview = data.get("overview", {})
    sections = data.get("sections", [])

    if output_path is None:
        output_path = Path(f"{document_name}.pdf")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Build story ──
    story = []

    # Tiêu đề cố định
    storyline = "HƯỚNG DẪN LƯU TRỮ DỮ LIỆU"
    story.append(P("DocTitle", storyline))
    story.append(Spacer(1, 1 * mm))

    # Bảng tổng quan
    ov_table = _build_overview_table(overview)
    if ov_table:
        story.append(ov_table)
        story.append(Spacer(1, 2 * mm))

    # Các section
    for sec in sections:
        sec_table = _build_section_table(sec)
        if sec_table:
            story.append(sec_table)
            story.append(Spacer(1, 1.5 * mm))

    # ── Tạo PDF ──
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=14,
        rightMargin=14,
        topMargin=18,
        bottomMargin=16,
        title=document_name,
        author="INNO PROJECT BUILDER",
    )

    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="normal",
    )
    template = PageTemplate(id="main", frames=[frame], onPage=_header_footer)
    doc.addPageTemplates([template])
    doc.build(story)

    return output_path


# ═══════════════════════════ CLI ═══════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    json_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    result = build_pdf(json_path, output_path)
    print(f"✅ PDF đã tạo: {result}")

    # Kiểm tra số trang
    with open(result, "rb") as f:
        content = f.read()

    page_count = content.count(b"/Type /Page") - content.count(b"/Type /Pages")
    print(f"   Kích thước: {result.stat().st_size:,} bytes")
    print(f"   Số trang: {page_count}")

    if page_count == 1:
        print("✅ PDF nằm gọn trong 1 trang A4!")
    else:
        print(f"⚠️  PDF có {page_count} trang. Cần tinh chỉnh thêm.")
