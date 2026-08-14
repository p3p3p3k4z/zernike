"""
gui/zernike_viewer_dialog.py
============================
Modulo de cuadro de dialogo interactivo para visualizar en 3D
cada uno de los 21 Polinomios de Zernike (ISO 10110-5, Grado k=5) de forma individual.
Hereda de Base3DPlotDialog para compartir todos los controles manuales 3D y tema.
"""

import numpy as np
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QComboBox, QPushButton
)
from PySide6.QtCore import Qt

from gui.components.base_3d_dialog import Base3DPlotDialog
from lib.zernike import INFORMACION_ZERNIKE_ISO, polinomios_zernike
from lib.visualizacion import mapa_fase_3d

INFORMACION_ZERNIKE = {info["r"]: info for info in INFORMACION_ZERNIKE_ISO}


class ZernikeViewer3DDialog(Base3DPlotDialog):
    """
    Cuadro de dialogo modular para explorar en 3D cualquiera de los 21 Polinomios de Zernike.
    """
    def __init__(self, resultado_zernike=None, parent=None):
        self.resultado_zernike = resultado_zernike
        self.polinomios = polinomios_zernike()
        self.r_actual = 1
        self._bloqueando_combo = False

        self._generar_malla_circulo_unitaria()

        super().__init__(
            titulo="Visor 3D de Polinomios de Zernike (ISO 10110-5 / 21 Polinomios)",
            width=950,
            height=720,
            parent=parent
        )

        self._personalizar_layout()
        # El primer dibujo se difiere a showEvent para garantizar que
        # el canvas tenga sus dimensiones reales antes de renderizar.

    def showEvent(self, event):
        """Renderiza el primer grafico 3D una vez que la ventana es visible y dimensionada."""
        super().showEvent(event)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, self._actualizar_grafico_3d)

    def _generar_malla_circulo_unitaria(self, num_puntos=60):
        x = np.linspace(-1.0, 1.0, num_puntos)
        y = np.linspace(-1.0, 1.0, num_puntos)
        xx, yy = np.meshgrid(x, y)
        mask = (xx**2 + yy**2) <= 1.0
        self.X_grid = xx[mask]
        self.Y_grid = yy[mask]

    def _personalizar_layout(self):
        # Fila de navegacion: Icono Izquierda | ComboBox Polinomios | Icono Derecha
        from PySide6.QtWidgets import QStyle

        layout_nav = QHBoxLayout()

        self.btn_anterior = QPushButton()
        self.btn_anterior.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.btn_anterior.setToolTip("Polinomio Anterior (r - 1)")
        self.btn_anterior.setFixedWidth(42)
        self.btn_anterior.clicked.connect(self._anterior_polinomio)
        layout_nav.addWidget(self.btn_anterior)

        self.combo_polinomio = QComboBox()
        for r in range(1, 22):
            info = INFORMACION_ZERNIKE[r]
            texto = f"r={r:02d}  Z_{info['n']}^{{{info['m']}}}  {info['nombre']}"
            self.combo_polinomio.addItem(texto, r)
        self.combo_polinomio.currentIndexChanged.connect(self._cambio_combo_polinomio)
        layout_nav.addWidget(self.combo_polinomio, stretch=1)

        self.btn_siguiente = QPushButton()
        self.btn_siguiente.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.btn_siguiente.setToolTip("Polinomio Siguiente (r + 1)")
        self.btn_siguiente.setFixedWidth(42)
        self.btn_siguiente.clicked.connect(self._siguiente_polinomio)
        layout_nav.addWidget(self.btn_siguiente)

        self.layout_base.insertLayout(0, layout_nav)

        # Etiqueta de informacion (formula y coeficiente) al pie
        self.lbl_info = QLabel()
        self.lbl_info.setAlignment(Qt.AlignCenter)
        self.lbl_info.setStyleSheet("font-size: 12px; padding: 4px 8px;")
        self.layout_base.addWidget(self.lbl_info)
        self._actualizar_estado_botones()

    def _actualizar_estado_botones(self):
        """Habilita o deshabilita los botones de navegacion segun los limites r=1 y r=21."""
        self.btn_anterior.setEnabled(self.r_actual > 1)
        self.btn_siguiente.setEnabled(self.r_actual < 21)

    def _ir_a_polinomio(self, r: int):
        """Navega al polinomio r (1..21) actualizando el combo y el grafico de forma atomica."""
        self.r_actual = r
        self._bloqueando_combo = True
        self.combo_polinomio.setCurrentIndex(r - 1)
        self._bloqueando_combo = False
        self._actualizar_estado_botones()
        self._actualizar_grafico_3d()

    def _cambio_combo_polinomio(self, index):
        if self._bloqueando_combo:
            return
        r = self.combo_polinomio.itemData(index)
        if r is not None:
            self.r_actual = r
            self._actualizar_estado_botones()
            self._actualizar_grafico_3d()

    def _anterior_polinomio(self):
        if self.r_actual > 1:
            self._ir_a_polinomio(self.r_actual - 1)

    def _siguiente_polinomio(self):
        if self.r_actual < 21:
            self._ir_a_polinomio(self.r_actual + 1)

    def _actualizar_grafico_3d(self):
        info = INFORMACION_ZERNIKE[self.r_actual]
        func_poly = self.polinomios[self.r_actual - 1]
        Z_poly = func_poly(self.X_grid, self.Y_grid)

        cmap_name, elev, azim, z_scale, wireframe, show_grid = self._obtener_parametros_render()
        n_grid, sigma = self._obtener_parametros_suavizado()

        titulo_fig = f"Polinomio r={self.r_actual:02d}: {info['nombre']}"
        fig = mapa_fase_3d(
            self.X_grid, self.Y_grid, Z_poly,
            title=titulo_fig,
            cmap=cmap_name,
            z_scale=z_scale,
            wireframe=wireframe,
            show_grid=show_grid,
            n_grid=n_grid,
            sigma=sigma
        )

        if hasattr(fig, 'axes') and len(fig.axes) > 0 and hasattr(fig.axes[0], 'view_init'):
            fig.axes[0].view_init(elev=elev, azim=azim)

        self.canvas.set_figure(fig)

        # Actualizar etiqueta inferior con formula y coeficiente
        coef_texto = ""
        if self.resultado_zernike is not None and hasattr(self.resultado_zernike, 'A'):
            A_val = self.resultado_zernike.A[self.r_actual - 1]
            coef_texto = f"   |   A_{self.r_actual} = {A_val:.6f}"

        self.lbl_info.setText(
            f"r={self.r_actual}  (n={info['n']}, m={info['m']})   "
            f"Z(x,y) = {info['formula']}{coef_texto}"
        )

        # Activar / desactivar botones de navegacion en los extremos
        self.btn_anterior.setEnabled(self.r_actual > 1)
        self.btn_siguiente.setEnabled(self.r_actual < 21)
