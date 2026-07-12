"""Entry point cho ứng dụng INNO PROJECT BUILDER."""

import tkinter as tk

from src.ui.app import ProjectInitApp


def main() -> None:
    """Khởi động ứng dụng."""
    root = tk.Tk()
    app = ProjectInitApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
