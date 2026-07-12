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
- Tải file `project_init_portable.exe` từ folder `dist_portable/`
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
