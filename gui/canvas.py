"""
gui/canvas.py
=============
Modulo de Qt que envuelve un lienzo de Matplotlib (FigureCanvasQTAgg)
con una barra de herramientas de navegacion (zoom, rotacion, guardar grafica).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvasWidget(QWidget):
    """
    Widget reutilizable para incrustar figuras de Matplotlib (2D y 3D) en PySide6.
    """
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        super().__init__(parent)

        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def clear(self):
        """Limpia los ejes de la figura y actualiza de forma asíncrona."""
        self.figure.clear()
        self.canvas.draw_idle()

    def set_figure(self, fig):
        """
        Reemplaza la figura en el lienzo de forma segura sin destruir QWidgets.
        Mantiene el lienzo PySide6 persistente para prevenir violaciones de segmento (SegFault)
        al cambiar de ventana o espacio de trabajo en Linux/Wayland.
        """
        if fig is None:
            return

        import matplotlib.pyplot as plt

        # Si es la misma figura, simplemente redibujar
        if self.figure == fig:
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

        # Re-inicializar controles 3D si la figura contiene ejes 3D
        for ax in self.figure.axes:
            if hasattr(ax, 'mouse_init'):
                ax.mouse_init()

        # Redibujar asíncronamente en el hilo principal de Qt
        self.canvas.draw_idle()




