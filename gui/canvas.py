"""
gui/canvas.py
=============
Modulo de Qt que envuelve un lienzo de Matplotlib (SafeFigureCanvas)
con una barra de herramientas de navegacion (zoom, rotacion, guardar grafica).
Protegido contra violaciones de segmento (SegFault) en gestores de ventanas de mosaico (i3wm, Sway, bspwm).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import QSize
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class SafeFigureCanvas(FigureCanvas):
    """
    Lienzo de Matplotlib protegido contra fallos de memoria C++ (SegFault)
    producidos al ocultar, mover o redimensionar ventanas en i3wm / X11 / Wayland.
    """
    def resizeEvent(self, event):
        # En i3wm o gestores de mosaico, al ocultar o cambiar de espacio de trabajo,
        # las dimensiones del widget pueden reducirse a 0x0 o desmapearse en X11.
        if self.width() <= 1 or self.height() <= 1 or not self.isVisible():
            return
        try:
            super().resizeEvent(event)
        except Exception:
            pass

    def paintEvent(self, event):
        # Previene que Matplotlib intente pintar en un buffer de memoria de tamaño 0 o desmapeado
        if self.width() <= 1 or self.height() <= 1 or not self.isVisible():
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
        # Ignorar sizeHints del canvas para evitar que la ventana se me expanda sola al actualizar barras de color
        self.canvas.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
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

    def clear(self):
        """Limpia los ejes de la figura y actualiza de forma asíncrona."""
        self.figure.clear()
        if self.isVisible() and self.width() > 1 and self.height() > 1:
            self.canvas.draw_idle()

    def set_figure(self, fig):
        """
        Reemplaza la figura en el lienzo de forma segura sin destruir QWidgets.
        Mantiene el lienzo PySide6 (SafeFigureCanvas) persistente para prevenir
        violaciones de segmento (SegFault) al cambiar de espacio de trabajo en i3wm / X11.
        """
        if fig is None:
            return

        import matplotlib.pyplot as plt

        # Si es la misma figura, simplemente redibujar
        if self.figure == fig:
            if self.isVisible() and self.width() > 1 and self.height() > 1:
                self.canvas.draw_idle()
            return

        # Cerrar la figura previa en pyplot si aplica
        if self.figure is not None and self.figure != fig:
            plt.close(self.figure)

        # Vincular la nueva figura al lienzo persistente de PySide6
        self.figure = fig
        self.canvas.figure = self.figure
        self.figure.set_canvas(self.canvas)

        # Actualizar la barra de herramientas de navegación
        if hasattr(self, 'toolbar') and self.toolbar is not None:
            self.toolbar.canvas = self.canvas
            self.toolbar.update()

        # Redibujar asíncronamente en el hilo principal de Qt si la ventana es visible
        if self.isVisible() and self.width() > 1 and self.height() > 1:
            self.canvas.draw_idle()




