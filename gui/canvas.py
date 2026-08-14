"""
gui/canvas.py
=============
Modulo de Qt que envuelve un lienzo de Matplotlib (SafeFigureCanvas)
con una barra de herramientas de navegacion (zoom, rotacion, guardar grafica).
Protegido contra violaciones de segmento (SegFault) en gestores de ventanas de mosaico (i3wm, Sway, bspwm).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import QSize, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class SafeFigureCanvas(FigureCanvas):
    """
    Lienzo de Matplotlib protegido contra fallos de memoria C++ (SegFault)
    producidos al ocultar, mover o redimensionar ventanas en i3wm / X11 / Wayland.
    """
    def resizeEvent(self, event):
        if self.width() <= 1 or self.height() <= 1:
            return
        try:
            super().resizeEvent(event)
        except Exception:
            pass

    def paintEvent(self, event):
        if self.width() <= 1 or self.height() <= 1:
            return
        try:
            super().paintEvent(event)
        except Exception:
            pass


class MplCanvasWidget(QWidget):
    """
    Widget reutilizable para incrustar figuras de Matplotlib (2D y 3D) en PySide6.
    """
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        super().__init__(parent)

        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.canvas = SafeFigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self):
        """Retorna un tamaño sugerido estable para evitar variaciones de geometría."""
        return QSize(640, 480)

    def showEvent(self, event):
        """Al mostrar el widget (ej: al cambiar de pestaña), redibujar con rescalado."""
        super().showEvent(event)
        QTimer.singleShot(0, self._redibujar_con_rescalado)

    def clear(self):
        """Limpia los ejes de la figura y actualiza de forma asíncrona."""
        self.figure.clear()
        if self.width() > 1 and self.height() > 1:
            self.canvas.draw_idle()

    def _rescalar_figura_al_canvas(self, fig):
        """
        Ajusta las dimensiones internas de la figura de Matplotlib al tamaño real
        actual del canvas de PySide6.
        """
        w = self.canvas.width()
        h = self.canvas.height()
        dpi = fig.get_dpi()
        if w > 1 and h > 1 and dpi > 0:
            fig.set_size_inches(w / dpi, h / dpi, forward=False)

    def set_figure(self, fig):
        """
        Reemplaza la figura en el lienzo de forma segura sin destruir QWidgets.
        """
        if fig is None:
            return

        if self.figure == fig:
            QTimer.singleShot(0, self._redibujar_si_visible)
            return

        if self.figure is not None and self.figure != fig:
            try:
                plt.close(self.figure)
            except Exception:
                pass

        self.figure = fig
        self.canvas.figure = self.figure
        self.figure.set_canvas(self.canvas)

        if hasattr(self, 'toolbar') and self.toolbar is not None:
            self.toolbar.canvas = self.canvas
            self.toolbar.update()

        QTimer.singleShot(0, self._redibujar_con_rescalado)

    def _redibujar_con_rescalado(self):
        """
        Rescala la figura al tamaño real del canvas y solicita un redibujo.
        """
        if self.width() <= 1 or self.height() <= 1:
            return
        try:
            self._rescalar_figura_al_canvas(self.figure)
            self.canvas.draw_idle()
        except Exception:
            pass

    def _redibujar_si_visible(self):
        """Solicita un redibujo simple si el canvas tiene dimensiones válidas."""
        if self.width() > 1 and self.height() > 1:
            try:
                self.canvas.draw_idle()
            except Exception:
                pass

