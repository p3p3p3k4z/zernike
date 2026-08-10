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
    # Estabilidad de escalado y renderizado para gestores de ventanas
    if sys.platform.startswith("linux"):
        # Configuracion Wayland (Sway/Hyprland) / XCB (i3wm/X11)
        if "WAYLAND_DISPLAY" in os.environ:
            os.environ.setdefault("QT_QPA_PLATFORM", "wayland;xcb")
        elif "DISPLAY" in os.environ:
            os.environ.setdefault("QT_QPA_PLATFORM", "xcb;wayland")

    # Registro de AppUserModelID en Windows para asociación de icono en la barra de tareas (Win 10/11)
    elif sys.platform.startswith("win"):
        try:
            import ctypes
            myappid = "zernike.optics.metrology.gui.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setDesktopFileName("zernike-gui")
    window = ZernikeZemaxMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
