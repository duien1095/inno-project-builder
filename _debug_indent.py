import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open('src/ui/app.py', 'r', encoding='utf-8').readlines()
# Sửa dòng 422: bỏ 4 spaces
lines[421] = lines[421][4:]  # dòng 422 (index 421) - bỏ 4 spaces đầu
lines[422] = lines[422][4:]  # dòng 423 (index 422)
lines[423] = lines[423][4:]  # dòng 424
# ... tiếp tục đến dòng 438
for i in range(424, 438):
    lines[i] = lines[i][4:]
# Ghi lại
with open('src/ui/app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Đã sửa indent xong!")
print(f"Tổng số dòng: {len(lines)}")
