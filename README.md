# PROJECT INIT

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

## Ghi chú
- Ứng dụng đọc template từ thư mục templates/
- Nếu cần thêm template mới, chỉ cần tạo thêm thư mục mới trong templates/

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
