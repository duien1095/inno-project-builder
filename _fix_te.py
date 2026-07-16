import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('src/template_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    stripped = line.rstrip('\n\r')
    # Tìm dòng "if not target_path.exists():" bị indent 16 spaces
    if stripped.lstrip().startswith('if not target_path.exists()'):
        spaces = len(stripped) - len(stripped.lstrip())
        if spaces != 12:
            print(f"Dòng {i+1}: indent={spaces} -> sửa thành 12")
            lines[i] = '            ' + stripped.lstrip() + '\n'
            # Sửa 2 dòng tiếp theo
            for j in range(1, 3):
                if i+j < len(lines):
                    s = lines[i+j].rstrip('\n\r')
                    sp = len(s) - len(s.lstrip())
                    if sp > 12:
                        lines[i+j] = '                ' + s.lstrip() + '\n'
                        print(f"Dòng {i+j+1}: indent={sp} -> sửa thành 16")
            break

with open('src/template_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
try:
    compile(''.join(lines), 'template_engine.py', 'exec')
    print("✅ Syntax OK!")
except SyntaxError as e:
    print(f"❌ {e}")
