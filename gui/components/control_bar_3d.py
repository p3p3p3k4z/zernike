"""
gui/components/control_bar_3d.py
================================
Barra de controles interactivos para manipular en tiempo real la camara (elevacion, azimut) 
y el mapa de colores (colormap) del lienzo de visualización 3D del Error Residual.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton
)
from PySide6.QtCore import Signal, Qt


class ControlBar3D(QWidget):
    """
    Toolbar horizontal con controles para ajustar la perspectiva 3D y el Colormap.
    Emite señales al cambiar angulos o mapas de color.
    """
    cambio_camara = Signal(int, int)
    cambio_colormap = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # 1. Selector de Colormap
        layout.addWidget(QLabel("Mapa de Colores:"))
        self.combo_cmap = QComboBox()
        self.combo_cmap.addItems([
            "viridis", "plasma", "coolwarm", "inferno", "cividis", "jet", "magma", "twilight"
        ])
        self.combo_cmap.setToolTip("Selecciona el mapa de colores para la superficie 3D.")
        self.combo_cmap.currentTextChanged.connect(self._al_cambiar_colormap)
        layout.addWidget(self.combo_cmap)

        # Separador visual
        layout.addSpacing(15)

        # 2. Elevacion (°)
        layout.addWidget(QLabel("Elevación (°):"))
        self.spin_elev = QSpinBox()
        self.spin_elev.setRange(-90, 90)
        self.spin_elev.setValue(30)
        self.spin_elev.setSingleStep(5)
        self.spin_elev.setToolTip("Ángulo vertical de inclinación de la cámara (-90° a 90°).")
        self.spin_elev.valueChanged.connect(self._al_cambiar_camara)
        layout.addWidget(self.spin_elev)

        # 3. Azimut (°)
        layout.addWidget(QLabel("Azimut (°):"))
        self.spin_azim = QSpinBox()
        self.spin_azim.setRange(0, 360)
        self.spin_azim.setValue(45)
        self.spin_azim.setSingleStep(5)
        self.spin_azim.setToolTip("Ángulo horizontal de rotación de la cámara (0° a 360°).")
        self.spin_azim.valueChanged.connect(self._al_cambiar_camara)
        layout.addWidget(self.spin_azim)

        # Separador visual
        layout.addSpacing(10)

        # 4. Boton Restablecer
        btn_reset = QPushButton("Restablecer Vista")
        btn_reset.setObjectName("btn_preset")
        btn_reset.setToolTip("Restaura la orientación inicial de la cámara (Elev: 30°, Azim: 45°).")
        btn_reset.clicked.connect(self.restablecer_vista)
        layout.addWidget(btn_reset)

        layout.addStretch()

    def _al_cambiar_camara(self):
        self.cambio_camara.emit(self.spin_elev.value(), self.spin_azim.value())

    def _al_cambiar_colormap(self, cmap_name: str):
        self.cambio_colormap.emit(cmap_name)

    def restablecer_vista(self):
        """Vuelve los valores de elevacion y azimut a la configuracion por defecto."""
        self.spin_elev.blockSignals(True)
        self.spin_azim.blockSignals(True)
        self.spin_elev.setValue(30)
        self.spin_azim.setValue(45)
        self.spin_elev.blockSignals(False)
        self.spin_azim.blockSignals(False)
        self.cambio_camara.emit(30, 45)
