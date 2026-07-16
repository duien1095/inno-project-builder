import sys
print(f"Python: {sys.executable}")
try:
    from reportlab.lib.units import mm
    print(f"reportlab OK: mm={mm}")
except ImportError as e:
    print(f"reportlab ERROR: {e}")
