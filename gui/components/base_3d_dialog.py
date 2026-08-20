"""
gui/components/base_3d_dialog.py
================================
Clase base modular para cuadros de dialogo de visualización tridimensional (3D).
Garantiza una interfaz uniforme con ControlBar3D, MplCanvasWidget y propagacion de temas (Claro y Nord Oscuro).
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout
from PySide6.QtCore import Qt

from gui.canvas import MplCanvasWidget
from gui.components.control_bar_3d import ControlBar3D


class Base3DPlotDialog(QDialog):
    """
    Clase base para dialogos 3D reutilizables.
    """
    def __init__(self, titulo="Visualizador 3D", width=950, height=700, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.resize(width, height)

        if parent is not None and hasattr(parent, 'styleSheet'):
            self.setStyleSheet(parent.styleSheet())

        self._construir_base_ui()

    def _construir_base_ui(self):
        self.layout_base = QVBoxLayout(self)
        self.layout_base.setContentsMargins(8, 8, 8, 8)
        self.layout_base.setSpacing(8)

        # 1. ControlBar3D Ampliado
        self.control_bar = ControlBar3D(self)
        self.control_bar.cambio_camara.connect(self._al_cambiar_camara)
        self.control_bar.cambio_colormap.connect(self._al_cambiar_colormap)
        self.control_bar.cambio_escala_z.connect(self._al_cambiar_escala_z)
        self.control_bar.cambio_modo_render.connect(self._al_cambiar_modo_render)
        self.control_bar.cambio_grid.connect(self._al_cambiar_grid)
        self.control_bar.cambio_suavizado.connect(lambda n, s: self._actualizar_grafico_3d())
        # Conectar los nuevos controles de modo de vista y curvas de nivel.
        self.control_bar.cambio_modo_vista.connect(lambda _modo_3d: self._actualizar_grafico_3d())
        self.control_bar.cambio_contornos.connect(lambda _activo, _n: self._actualizar_grafico_3d())
        self.layout_base.addWidget(self.control_bar)

        # 2. MplCanvasWidget Persistente
        self.canvas = MplCanvasWidget(self)
        self.layout_base.addWidget(self.canvas, stretch=1)

    def _obtener_parametros_render(self):
        """Retorna una tupla con (cmap, elev, azim, z_scale, wireframe, show_grid)."""
        cmap_name = self.control_bar.combo_cmap.currentText()
        elev = self.control_bar.spin_elev.value()
        azim = self.control_bar.spin_azim.value()
        z_scale = self.control_bar.spin_escala_z.value()
        wireframe = self.control_bar.chk_wireframe.isChecked()
        show_grid = self.control_bar.chk_grid.isChecked()

        try:
            if hasattr(self, 'canvas') and hasattr(self.canvas, 'figure') and self.canvas.figure is not None:
                if len(self.canvas.figure.axes) > 0:
                    ax_prev = self.canvas.figure.axes[0]
                    if hasattr(ax_prev, 'elev') and ax_prev.elev is not None:
                        elev = int(ax_prev.elev)
                        azim = int(ax_prev.azim)
                        self.control_bar.spin_elev.blockSignals(True)
                        self.control_bar.spin_azim.blockSignals(True)
                        self.control_bar.spin_elev.setValue(elev)
                        self.control_bar.spin_azim.setValue(azim)
                        self.control_bar.spin_elev.blockSignals(False)
                        self.control_bar.spin_azim.blockSignals(False)
        except Exception:
            pass

        return cmap_name, elev, azim, z_scale, wireframe, show_grid

    def _obtener_parametros_suavizado(self):
        """Retorna una tupla con (n_grid, sigma)."""
        n_grid = self.control_bar.spin_n_grid.value()
        sigma = self.control_bar.spin_sigma.value()
        return n_grid, sigma

    def _obtener_modo_vista(self) -> bool:
        """Retorna True si la vista activa es 3D (superficie), False si es 2D (mapa de calor)."""
        return not self.control_bar.btn_modo_vista.isChecked()

    def _obtener_parametros_contornos(self) -> tuple:
        """Retorna una tupla (show_contours, n_contour_levels) con los ajustes de curvas de nivel."""
        return (
            self.control_bar.chk_contornos.isChecked(),
            self.control_bar.spin_n_contornos.value(),
        )

    def _al_cambiar_camara(self, elev: int, azim: int):
        if hasattr(self.canvas.figure, 'axes') and len(self.canvas.figure.axes) > 0:
            ax = self.canvas.figure.axes[0]
            if hasattr(ax, 'view_init'):
                ax.view_init(elev=elev, azim=azim)
                self.canvas.canvas.draw_idle()

    def _al_cambiar_colormap(self, cmap_name: str):
        self._actualizar_grafico_3d()

    def _al_cambiar_escala_z(self, val: float):
        self._actualizar_grafico_3d()

    def _al_cambiar_modo_render(self, wireframe: bool):
        self._actualizar_grafico_3d()

    def _al_cambiar_grid(self, show_grid: bool):
        self._actualizar_grafico_3d()

    def _actualizar_grafico_3d(self):
        """Metodo abstracto a implementar en las clases derivadas."""
        pass
