import json, tempfile, os, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

tmp = tempfile.TemporaryDirectory()
tmpdir = Path(tmp.name)
cwd = Path.cwd()
os.chdir(str(tmpdir))

print(f"CWD: {Path.cwd()}")

# Tạo file template_pdf.json
json_path = tmpdir / "template_pdf.json"
data = {
    "document_name": "TEST",
    "version": "1.0",
    "overview": {"input": "Nơi lưu dữ liệu gốc"},
    "sections": [
        {
            "name": "01.INPUT",
            "items": [
                {"folder": "01.PHAP_LY", "description": "Văn bản pháp lý"},
                {"folder": "02.RANH_GIOI", "description": "Hồ sơ ranh giới"},
            ]
        }
    ]
}
json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"PDF JSON exists: {json_path.exists()}")

# Test generate_pdf_template
sys.path.insert(0, str(tmpdir.parent.parent))
# Thêm src vào path
src_dir = Path(cwd) / "src"
sys.path.insert(0, str(src_dir.parent))

from src.template_engine import generate_pdf_template

project = tmpdir / "DU_AN"
project.mkdir(parents=True, exist_ok=True)

result = generate_pdf_template(project, "QHC")
print(f"Result: {result}")
if result:
    print(f"File exists: {result.exists()}")
    print(f"File size: {result.stat().st_size}")
else:
    # Thử gọi trực tiếp generate_pdf_from_template
    print("-> Trying direct call...")
    from src.pdf_generator import generate_pdf_from_template
    out = project / "HuongDanLuuTru.pdf"
    try:
        r = generate_pdf_from_template(json_path, out, "TEST")
        print(f"Direct result: {r}")
        print(f"Direct exists: {r.exists()}")
    except Exception as e:
        print(f"Direct error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

os.chdir(str(cwd))
tmp.cleanup()
