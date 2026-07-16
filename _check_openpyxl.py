import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")
try:
    import openpyxl
    print(f"openpyxl OK: {openpyxl.__version__}")
except ImportError as e:
    print(f"openpyxl ERROR: {e}")
