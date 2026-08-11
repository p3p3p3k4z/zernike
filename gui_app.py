import sys
import os
import signal

# Configuración explícita del backend QtAgg para evitar conflictos de renderizado en Matplotlib
import matplotlib
matplotlib.use("QtAgg")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication
from gui.main_window import ZernikeZemaxMainWindow


def main():
    # Estabilidad de escalado y renderizado para gestores de ventanas en Linux (i3wm / Wayland / X11)
    if sys.platform.startswith("linux"):
        # Desactivar portal DBus XDG en i3wm/X11 para evitar fallos de segmento si org.freedesktop.portal.Desktop no está activo
        os.environ.setdefault("QT_NO_XDG_DESKTOP_PORTAL", "1")
        os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.services.warning=false")
        
        # Configuración de plataforma con fallback: Wayland (Sway/Hyprland) / XCB (i3wm/X11)
        if "WAYLAND_DISPLAY" in os.environ:
            os.environ.setdefault("QT_QPA_PLATFORM", "wayland;xcb")
        elif "DISPLAY" in os.environ:
            os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

        # Pre-cargar cache de fuentes de Matplotlib para evitar condiciones de carrera en el hilo GUI de Qt
        try:
            import matplotlib.font_manager as fm
            fm.fontManager.get_default_weight()
        except Exception:
            pass

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

    # Permitir que Ctrl+C desde la terminal cierre la ventana limpiamente.
    # Sin el timer de latido, Qt bloquea el GIL durante exec() y Python nunca
    # procesa la senal SIGINT. El timer de 250 ms cede el control periodicamente.
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    latido = QTimer()
    latido.start(250)
    latido.timeout.connect(lambda: None)

    window = ZernikeZemaxMainWindow()

    # Asignar a QApplication el icono de la ventana principal para que la barra de tareas de Windows lo despliegue
    if not window.windowIcon().isNull():
        app.setWindowIcon(window.windowIcon())

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
