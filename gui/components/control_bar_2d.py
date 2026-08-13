"""
gui/components/control_bar_2d.py
================================
Barra de controles interactivos para manipular en tiempo real el modo de renderizado (Franjas de interferencia vs Elevación de Fase),
sensibilidad de franjas Nλ, mapa de colores, contornos y cuadrícula 2D.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QDoubleSpinBox, QCheckBox, QPushButton
)
from PySide6.QtCore import Signal


class ControlBar2D(QWidget):
    """
    Toolbar horizontal con controles para ajustar el modo de visualización 2D (Franjas de interferencia / Fase),
    número de franjas, paleta cromática, contornos y cuadrícula.
    """
    cambio_modo = Signal(str)
    cambio_franjas = Signal(float)
    cambio_colormap = Signal(str)
    cambio_modo_render = Signal(bool)
    cambio_grid = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # 1. Selector de Modo de Representación
        layout.addWidget(QLabel("Modo:"))
        self.combo_modo = QComboBox()
        self.combo_modo.addItem("Franjas de Interferencia (Interferograma)", "interferograma")
        self.combo_modo.addItem("Mapa de Fase Continuo (Elevación)", "fase")
        self.combo_modo.setToolTip("Alterna entre el patrón de franjas de interferencia sintéticas I(x,y) y el mapa continuo de fase Z(x,y).")
        self.combo_modo.currentIndexChanged.connect(self._al_cambiar_modo)
        layout.addWidget(self.combo_modo)

        # 2. Control de Sensibilidad / Número de Franjas (Nλ)
        self.lbl_franjas = QLabel("Franjas (Nλ):")
        layout.addWidget(self.lbl_franjas)

        self.spin_franjas = QDoubleSpinBox()
        self.spin_franjas.setRange(0.5, 10.0)
        self.spin_franjas.setSingleStep(0.5)
        self.spin_franjas.setValue(2.0)
        self.spin_franjas.setSuffix(" λ")
        self.spin_franjas.setToolTip("Ajusta la densidad de franjas de interferencia para modular la fase del polinomio.")
        self.spin_franjas.valueChanged.connect(lambda val: self.cambio_franjas.emit(val))
        layout.addWidget(self.spin_franjas)

        layout.addSpacing(6)

        # 3. Selector de Colormap
        layout.addWidget(QLabel("Color:"))
        self.combo_cmap = QComboBox()
        self.combo_cmap.addItems([
            "gray", "coolwarm", "seismic", "viridis", "twilight", "inferno", "plasma", "magma", "rainbow", "Spectral", "jet", "cividis"
        ])
        self.combo_cmap.setToolTip("Selecciona la paleta de colores para el gráfico 2D.")
        self.combo_cmap.currentTextChanged.connect(self._al_cambiar_colormap)
        layout.addWidget(self.combo_cmap)

        layout.addSpacing(6)

        # 4. Opciones Visuales (Líneas de Nivel y Grid)
        self.chk_contours = QCheckBox("Contornos")
        self.chk_contours.setChecked(False)
        self.chk_contours.setToolTip("Muestra u oculta las líneas de nivel superpuestas sobre el mapa 2D.")
        self.chk_contours.toggled.connect(lambda state: self.cambio_modo_render.emit(state))
        layout.addWidget(self.chk_contours)

        self.chk_grid = QCheckBox("Cuadrícula")
        self.chk_grid.setChecked(True)
        self.chk_grid.setToolTip("Muestra u oculta la cuadrícula de los ejes 2D.")
        self.chk_grid.toggled.connect(lambda state: self.cambio_grid.emit(state))
        layout.addWidget(self.chk_grid)

        layout.addSpacing(6)

        # 5. Botón Restablecer
        btn_reset = QPushButton("Restablecer")
        btn_reset.setObjectName("btn_preset")
        btn_reset.setToolTip("Restaura las opciones visuales y el patrón de franjas por defecto.")
        btn_reset.clicked.connect(self.restablecer_vista)
        layout.addWidget(btn_reset)

        layout.addStretch()

    def _al_cambiar_modo(self, index: int):
        modo_key = self.combo_modo.itemData(index)
        es_interferograma = (modo_key == "interferograma")
        self.spin_franjas.setEnabled(es_interferograma)
        self.lbl_franjas.setEnabled(es_interferograma)
        self.cambio_modo.emit(modo_key)

    def _al_cambiar_colormap(self, cmap_name: str):
        self.cambio_colormap.emit(cmap_name)

    def restablecer_vista(self):
        """Vuelve los valores de modo, franjas, colormap, contornos y cuadrícula a la configuración por defecto."""
        self.combo_modo.blockSignals(True)
        self.spin_franjas.blockSignals(True)
        self.combo_cmap.blockSignals(True)
        self.chk_contours.blockSignals(True)
        self.chk_grid.blockSignals(True)

        self.combo_modo.setCurrentIndex(0)  # interferograma
        self.spin_franjas.setValue(2.0)
        self.spin_franjas.setEnabled(True)
        self.lbl_franjas.setEnabled(True)
        self.combo_cmap.setCurrentText("gray")
        self.chk_contours.setChecked(False)
        self.chk_grid.setChecked(True)

        self.combo_modo.blockSignals(False)
        self.spin_franjas.blockSignals(False)
        self.combo_cmap.blockSignals(False)
        self.chk_contours.blockSignals(False)
        self.chk_grid.blockSignals(False)

        self.cambio_modo.emit("interferograma")
        self.cambio_franjas.emit(2.0)
        self.cambio_colormap.emit("gray")
        self.cambio_modo_render.emit(False)
        self.cambio_grid.emit(True)
