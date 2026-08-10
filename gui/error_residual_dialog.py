"""
gui/error_residual_dialog.py
============================
Componente modular que encapsula la ventana flotante no modal para 
la visualización tridimensional del Mapa de Error Residual (Z_exp - Z_fit).
"""

from PySide6.QtCore import Qt
from gui.components.base_3d_dialog import Base3DPlotDialog
from lib.visualizacion import mapa_fase_3d


class ErrorResidual3DDialog(Base3DPlotDialog):
    """
    Ventana flotante modular para visualizar el Error Residual 3D
    heredando de Base3DPlotDialog para compartir todos los controles manuales 3D y tema.
    """
    def __init__(self, X, Y, W_exp, W_fit, parent=None):
        self.X = X
        self.Y = Y
        self.W_exp = W_exp
        self.W_fit = W_fit
        self.Z_diff = W_exp - W_fit

        super().__init__(
            titulo="Mapa de Error Residual 3D (Z_exp - Z_fit)",
            width=900,
            height=680,
            parent=parent
        )

        # El primer dibujo se difiere a showEvent para garantizar que
        # el canvas tenga sus dimensiones reales antes de renderizar.

    def showEvent(self, event):
        """Renderiza el grafico 3D una vez que la ventana es visible y dimensionada."""
        super().showEvent(event)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, self._actualizar_grafico_3d)


    def _actualizar_grafico_3d(self):
        cmap_name, elev, azim, z_scale, wireframe, show_grid = self._obtener_parametros_render()

        fig = mapa_fase_3d(
            self.X, self.Y, self.Z_diff,
            title='Error Residual 3D (Z_exp - Z_fit)',
            cmap=cmap_name,
            z_scale=z_scale,
            wireframe=wireframe,
            show_grid=show_grid
        )

        if hasattr(fig, 'axes') and len(fig.axes) > 0 and hasattr(fig.axes[0], 'view_init'):
            fig.axes[0].view_init(elev=elev, azim=azim)

        self.canvas.set_figure(fig)


def mostrar_ventana_3d_error_residual(X, Y, W_exp, W_fit, parent=None):
    """Instancia y muestra la ventana flotante no modal del Error Residual 3D con controles."""
    dialog = ErrorResidual3DDialog(X, Y, W_exp, W_fit, parent=parent)
    dialog.setWindowModality(Qt.NonModal)
    dialog.show()
    return dialog
