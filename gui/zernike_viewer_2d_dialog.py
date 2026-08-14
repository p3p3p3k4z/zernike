"""
gui/zernike_viewer_2d_dialog.py
===============================
Modulo interactivo para visualizar en 2D (mapa de calor y lineas de nivel)
cada uno de los 21 Polinomios de Zernike (ISO 10110-5, Grado k=5) de forma individual.
Comparte la misma arquitectura, catalogo de informacion y controles de navegacion del Visor 3D.
"""

import numpy as np
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
)
from PySide6.QtCore import Qt, QTimer

from gui.canvas import MplCanvasWidget
from gui.components.control_bar_2d import ControlBar2D
from gui.zernike_viewer_dialog import INFORMACION_ZERNIKE
from lib.zernike import polinomios_zernike
from lib.visualizacion import mapa_zernike_2d


class ZernikeViewer2DDialog(QDialog):
    """Cuadro de dialogo modular para explorar en 2D cualquiera de los 21 Polinomios de Zernike."""
    def __init__(self, resultado_zernike=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visor 2D de Polinomios de Zernike (ISO 10110-5 / 21 Polinomios)")
        self.resize(950, 720)

        if parent is not None and hasattr(parent, 'styleSheet'):
            self.setStyleSheet(parent.styleSheet())

        self.resultado_zernike = resultado_zernike
        self.polinomios = polinomios_zernike()
        self.r_actual = 1
        self._bloqueando_combo = False

        self._generar_malla_circulo_unitaria()
        self._construir_ui()

    def showEvent(self, event):
        """Renderiza el primer grafico 2D una vez que la ventana es visible y dimensionada."""
        super().showEvent(event)
        QTimer.singleShot(50, self._actualizar_grafico_2d)

    def _generar_malla_circulo_unitaria(self, num_puntos=60):
        x = np.linspace(-1.0, 1.0, num_puntos)
        y = np.linspace(-1.0, 1.0, num_puntos)
        xx, yy = np.meshgrid(x, y)
        mask = (xx**2 + yy**2) <= 1.0
        self.X_grid = xx[mask]
        self.Y_grid = yy[mask]

    def _construir_ui(self):
        from PySide6.QtWidgets import QStyle

        layout_base = QVBoxLayout(self)
        layout_base.setContentsMargins(8, 8, 8, 8)
        layout_base.setSpacing(8)

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

        layout_base.addLayout(layout_nav)

        self.control_bar = ControlBar2D(self)
        self.control_bar.cambio_modo.connect(lambda m: self._actualizar_grafico_2d())
        self.control_bar.cambio_franjas.connect(lambda f: self._actualizar_grafico_2d())
        self.control_bar.cambio_colormap.connect(lambda c: self._actualizar_grafico_2d())
        self.control_bar.cambio_modo_render.connect(lambda m: self._actualizar_grafico_2d())
        self.control_bar.cambio_grid.connect(lambda g: self._actualizar_grafico_2d())
        layout_base.addWidget(self.control_bar)

        self.canvas = MplCanvasWidget(self)
        layout_base.addWidget(self.canvas, stretch=1)

        self.lbl_info = QLabel()
        self.lbl_info.setAlignment(Qt.AlignCenter)
        self.lbl_info.setStyleSheet("font-size: 12px; padding: 4px 8px;")
        layout_base.addWidget(self.lbl_info)

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
        self._actualizar_grafico_2d()

    def _cambio_combo_polinomio(self, index):
        if self._bloqueando_combo:
            return
        r = self.combo_polinomio.itemData(index)
        if r is not None:
            self.r_actual = r
            self._actualizar_estado_botones()
            self._actualizar_grafico_2d()

    def _anterior_polinomio(self):
        if self.r_actual > 1:
            self._ir_a_polinomio(self.r_actual - 1)

    def _siguiente_polinomio(self):
        if self.r_actual < 21:
            self._ir_a_polinomio(self.r_actual + 1)

    def _actualizar_grafico_2d(self):
        info = INFORMACION_ZERNIKE[self.r_actual]
        func_poly = self.polinomios[self.r_actual - 1]
        Z_poly = func_poly(self.X_grid, self.Y_grid)

        modo_render = self.control_bar.combo_modo.currentData() or "interferograma"
        n_franjas = self.control_bar.spin_franjas.value()
        cmap_name = self.control_bar.combo_cmap.currentText()
        show_contours = self.control_bar.chk_contours.isChecked()
        show_grid = self.control_bar.chk_grid.isChecked()

        tag_modo = f"Interferograma N={n_franjas:.1f}λ" if modo_render == "interferograma" else "Elevacion de Fase"
        titulo_fig = f"Polinomio r={self.r_actual:02d}: {info['nombre']} [{tag_modo}]"
        fig = mapa_zernike_2d(
            self.X_grid, self.Y_grid, Z_poly,
            title=titulo_fig,
            cmap=cmap_name,
            modo_render=modo_render,
            n_franjas=n_franjas,
            show_contours=show_contours,
            show_grid=show_grid
        )

        self.canvas.set_figure(fig)

        coef_texto = ""
        if self.resultado_zernike is not None and hasattr(self.resultado_zernike, 'A'):
            A_val = self.resultado_zernike.A[self.r_actual - 1]
            coef_texto = f"   |   A_{self.r_actual} = {A_val:.6f}"

        self.lbl_info.setText(
            f"r={self.r_actual}  (n={info['n']}, m={info['m']})   "
            f"Z(x,y) = {info['formula']}{coef_texto}"
        )

        self.btn_anterior.setEnabled(self.r_actual > 1)
        self.btn_siguiente.setEnabled(self.r_actual < 21)
