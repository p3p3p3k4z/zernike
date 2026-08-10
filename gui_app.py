import sys
import os

# Configuración explícita del backend QtAgg para evitar conflictos de renderizado en Matplotlib
import matplotlib
matplotlib.use("QtAgg")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from gui.main_window import ZernikeZemaxMainWindow


def main():
    # Estabilidad de escalado y renderizado para servidor de pantalla Linux (Wayland/X11)
    if sys.platform.startswith("linux"):
        os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    window = ZernikeZemaxMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
