import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('src/ui/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Tổng số dòng: {len(lines)}")

# In các dòng 415-440
for i in range(414, min(440, len(lines))):
    print(f"{i+1:>4}: {repr(lines[i][:60])}")

# Fix:
# 1. Xoá dòng 418 (self._initialize_project() lơ lửng) - index 417
# 2. Dòng 422 (def _initialize_project) - index 421: sửa 8 spaces -> 4 spaces

# Xoá dòng 418
del lines[417]

# Sau khi xoá, dòng 422 cũ xuống 421. Sửa indent
for i, line in enumerate(lines):
    stripped = line.lstrip()
    if stripped.startswith('def _initialize_project('):
        current_indent = len(line) - len(stripped)
        print(f"Dòng {i+1}: indent hiện tại = {current_indent}, cần 4 spaces")
        if current_indent == 8:
            lines[i] = line[4:]  # bỏ 4 spaces
            print(f"  -> Đã sửa thành indent 4 spaces")
        break

with open('src/ui/app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
print("\nSau khi fix:")
for i in range(414, min(440, len(lines))):
    print(f"{i+1:>4}: {repr(lines[i][:60])}")

# Check syntax
try:
    compile(''.join(lines), 'app.py', 'exec')
    print("\n✅ Syntax OK!")
except SyntaxError as e:
    print(f"\n❌ Syntax error: {e}")

