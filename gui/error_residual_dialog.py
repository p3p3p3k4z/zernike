"""
gui/error_residual_dialog.py
============================
Componente modular que encapsula la ventana flotante no modal para 
la visualización tridimensional del Mapa de Error Residual (Z_exp - Z_fit).
"""

from PySide6.QtCore import Qt
from gui.components.base_3d_dialog import Base3DPlotDialog


class ErrorResidual3DDialog(Base3DPlotDialog):
    """
    Ventana flotante modular para visualizar el Error Residual en 3D o 2D
    heredando de Base3DPlotDialog para compartir todos los controles manuales y tema.
    """
    def __init__(self, X, Y, W_exp, W_fit, parent=None, modo_2d=False):
        self.X = X
        self.Y = Y
        self.W_exp = W_exp
        self.W_fit = W_fit
        self.Z_diff = W_exp - W_fit

        titulo = "Mapa de Error Residual 2D (Z_exp - Z_fit)" if modo_2d else "Mapa de Error Residual 3D (Z_exp - Z_fit)"

        super().__init__(
            titulo=titulo,
            width=900,
            height=680,
            parent=parent
        )

        if modo_2d:
            self.control_bar.btn_modo_vista.setChecked(True)

    def actualizar_datos(self, X, Y, W_exp, W_fit):
        """Actualiza dinámicamente los datos de entrada del error residual y refresca la gráfica 2D/3D."""
        self.X = X
        self.Y = Y
        self.W_exp = W_exp
        self.W_fit = W_fit
        self.Z_diff = W_exp - W_fit
        self._actualizar_grafico_3d()

    def showEvent(self, event):
        """Renderiza el grafico 3D una vez que la ventana es visible y dimensionada."""
        super().showEvent(event)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, self._actualizar_grafico_3d)



    def _actualizar_grafico_3d(self):
        cmap_name, elev, azim, z_scale, wireframe, show_grid = self._obtener_parametros_render()
        n_grid, sigma = self._obtener_parametros_suavizado()
        modo_3d = self._obtener_modo_vista()
        show_contours, n_contour_levels = self._obtener_parametros_contornos()

        if modo_3d:
            # Renderizar como superficie tridimensional con curvas de nivel opcionales en el piso.
            from lib.visualizacion import mapa_fase_3d
            fig = mapa_fase_3d(
                self.X, self.Y, self.Z_diff,
                title='Error Residual 3D (Z_exp - Z_fit)',
                cmap=cmap_name,
                z_scale=z_scale,
                wireframe=wireframe,
                show_grid=show_grid,
                n_grid=n_grid,
                sigma=sigma,
                show_contours=show_contours,
                n_contour_levels=n_contour_levels,
            )
            if hasattr(fig, 'axes') and len(fig.axes) > 0 and hasattr(fig.axes[0], 'view_init'):
                fig.axes[0].view_init(elev=elev, azim=azim)
        else:
            # Renderizar como mapa de calor 2D con curvas de nivel superpuestas opcionales.
            from lib.visualizacion import mapa_fase_2d
            fig = mapa_fase_2d(
                self.X, self.Y, self.Z_diff,
                title='Error Residual 2D (Z_exp - Z_fit)',
                cmap=cmap_name,
                n_grid=n_grid,
                sigma=sigma,
                show_contours=show_contours,
                n_contour_levels=n_contour_levels,
            )

        self.canvas.set_figure(fig)



def mostrar_ventana_3d_error_residual(X, Y, W_exp, W_fit, parent=None):
    """Instancia y muestra la ventana flotante no modal del Error Residual 3D con controles."""
    dialog = ErrorResidual3DDialog(X, Y, W_exp, W_fit, parent=parent, modo_2d=False)
    dialog.setWindowModality(Qt.NonModal)
    dialog.show()
    return dialog


def mostrar_ventana_2d_error_residual(X, Y, W_exp, W_fit, parent=None):
    """Instancia y muestra la ventana flotante no modal del Error Residual 2D con controles."""
    dialog = ErrorResidual3DDialog(X, Y, W_exp, W_fit, parent=parent, modo_2d=True)
    dialog.setWindowModality(Qt.NonModal)
    dialog.show()
    return dialog

