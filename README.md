# INNO PROJECT BUILDER (Chuẩn hóa thư mục quy hoạch)

![HRDD Logo](./assets/logo.png)

Dự án này cung cấp một ứng dụng desktop Windows để khởi tạo nhanh cấu trúc thư mục cho các dự án quy hoạch.

## Mục tiêu
- Giảm thao tác thủ công khi tạo thư mục dự án
- Dùng template chuẩn để khởi tạo cấu trúc nhanh chóng
- Hỗ trợ người dùng làm việc chuyên nghiệp và nhất quán

## Cấu trúc thư mục
- templates/ : thư mục lưu các template khởi tạo dự án
- Khi khởi tạo, ứng dụng chỉ tạo đúng những thư mục và file có trong template được chọn

## Ứng dụng chính
- project_init.py : giao diện ứng dụng Tkinter
- run_project_init.bat : file chạy nhanh trên Windows

## Cách chạy
1. Mở thư mục tree
2. Nhấn đúp vào run_project_init.bat
3. Chọn thư mục dự án
4. Chọn template và xác nhận

## Hướng dẫn chi tiết sử dụng App

### 1. Yêu cầu hệ thống
- Windows 7 trở lên
- Python 3.7+ (nếu chạy từ source code)

### 2. Cài đặt
**Cách 1: Chạy trực tiếp (đơn giản nhất)**
- Tải file `project_init_portable.exe` từ folder `dist/`
- Không cần cài đặt Python hay các dependencies khác

**Cách 2: Chạy từ source code**
- Cần cài đặt Python
- Chạy lệnh: `python project_init.py`

### 3. Sử dụng ứng dụng
**Bước 1:** Chạy ứng dụng
- Nhấn đúp vào `run_project_init.bat` hoặc `project_init_portable.exe`

**Bước 2:** Chọn thư mục đích
- Nhấn nút "Browse" để chọn nơi tạo dự án mới
- Hoặc ghi trực tiếp đường dẫn vào ô text

**Bước 3:** Chọn template
- Danh sách các template có sẵn:
  - **TOD**: Template chuẩn cho dự án Quy hoạch Tổng thể
  - **QHC**: Template cho dự án Quy hoạch Chi tiết
  - **QHCT**: Template cho dự án Quy hoạch Cảnh Quan Thiên nhiên

**Bước 4:** Xác nhận
- Nhấn nút "Create Project" để tạo dự án
- Chọn "Yes" khi hộp thoại xác nhận

**Bước 5:** Hoàn tất
- Dự án sẽ được tạo tự động với cấu trúc thư mục theo template

### 4. Thêm template mới
- Tạo thư mục mới trong thư mục `templates/`
- Đặt tên theo format: `TEMPLATE_NAME/`
- Template sẽ tự động xuất hiện trong danh sách lựa chọn của ứng dụng

### 5. Kết quả sau khi tạo
- Tất cả thư mục và file từ template được sao chép vào thư mục dự án
- Có thể bắt đầu làm việc ngay

## Cơ chế Build

Ứng dụng được release dưới dạng **một file .exe portable duy nhất**, không cần cài đặt Python hay bất kỳ dependency nào.

### Build portable (one-file .exe)

Sử dụng PyInstaller để đóng gói toàn bộ ứng dụng:

```bash
# Cài PyInstaller
pip install pyinstaller

# Build one-file portable
python -m PyInstaller --noconfirm --onefile --windowed ^
  --name project_init_portable ^
  --add-data "templates;templates" ^
  --add-data "templates_config.json;." ^
  --add-data "assets_logo.png;." ^
  --hidden-import PIL ^
  --hidden-import PIL._tkinter_finder ^
  --workpath _build_temp/project_init_portable ^
  --distpath dist ^
  project_init.py
```

Kết quả: `dist/project_init_portable.exe` — file .exe duy nhất (~20-30MB), copy và chạy trực tiếp trên mọi máy Windows không cần Python.

### Release tự động

Script `release.bat` (Windows) và `release.sh` (Linux/Mac) tự động hóa quy trình release:

```bash
# Windows
release.bat 0.2.0

# Linux/Mac
./release.sh 0.2.0
```

Script sẽ:
1. Cài đặt dependencies
2. Chạy test suite (`pytest`)
3. Kiểm tra version khớp với `__version__` trong `project_init.py`
4. Build portable .exe với PyInstaller

## Ghi chú
- Ứng dụng đọc template từ thư mục templates/
- Nếu cần thêm template mới, chỉ cần tạo thêm thư mục mới trong templates/

## Tác giả
**Kiến Trúc Sư Duyên Đoàn**

---

*Phát triển bởi HRDD - Creativity at Work*

## Rủi ro bảo mật đã ghi nhận nhưng chưa xử lý
1. Lỗ hổng nghiêm trọng nhất: Path Traversal

Hiện tại:

```
target_path = project_folder / folder_path
```

Nếu file JSON template bị sửa thành:

```
{
  "folders": [
    "../../ABC",
    "../../../DATA",
    "D:/Company"
  ]
}
```

thì code sẽ tạo thư mục ngoài project.

Ví dụ:

```
project_folder = D:/Projects/Project_A
folder_path = ../../Finance
```

kết quả:

```
D:/Finance
```

=> Tool có thể tạo thư mục lung tung trên ổ đĩa.

Đây là rủi ro lớn nhất.
