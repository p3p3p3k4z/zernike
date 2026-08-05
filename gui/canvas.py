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
        """Limpia los ejes de la figura."""
        self.figure.clear()
        self.canvas.draw()

    def set_figure(self, fig):
        """
        Reemplaza limpiamente la figura en el lienzo.
        Elimina el canvas anterior de Qt para prevenir superposiciones visuales y congelamientos.
        """
        import matplotlib.pyplot as plt

        # Desvincular de pyplot para evitar interferencias
        plt.close(fig)

        if hasattr(self, 'canvas') and self.canvas is not None:
            self.layout().removeWidget(self.canvas)
            self.canvas.setParent(None)
            self.canvas.deleteLater()

        if hasattr(self, 'figure') and self.figure is not None and self.figure != fig:
            plt.close(self.figure)

        self.figure = fig
        self.canvas = FigureCanvas(self.figure)
        self.layout().addWidget(self.canvas)
        self.toolbar.canvas = self.canvas
        self.toolbar.update()

        for ax in self.figure.axes:
            if hasattr(ax, 'mouse_init'):
                ax.mouse_init()

        self.canvas.draw()




