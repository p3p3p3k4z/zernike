import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication
from gui.main_window import ZernikeZemaxMainWindow


def main():
    app = QApplication(sys.argv)
    window = ZernikeZemaxMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
