"""
gui/components/control_bar_3d.py
================================
Barra de controles interactivos para manipular en tiempo real la camara (elevacion, azimut) 
y el mapa de colores (colormap) del lienzo de visualización 3D del Error Residual.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton
)
from PySide6.QtCore import Signal, Qt


class ControlBar3D(QWidget):
    """
    Toolbar horizontal con controles para ajustar la perspectiva 3D, Colormap,
    escala manual del eje Z, modo de renderizado y cuadricula.
    """
    cambio_camara = Signal(int, int)
    cambio_colormap = Signal(str)
    cambio_escala_z = Signal(float)
    cambio_modo_render = Signal(bool)
    cambio_grid = Signal(bool)

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
            "coolwarm", "seismic", "twilight", "viridis", "inferno", "plasma", "magma", "rainbow", "Spectral", "jet", "cividis"
        ])
        self.combo_cmap.setToolTip("Selecciona el mapa de colores para la superficie 3D.")
        self.combo_cmap.currentTextChanged.connect(self._al_cambiar_colormap)
        layout.addWidget(self.combo_cmap)

        layout.addSpacing(10)

        # 2. Elevacion (grados)
        layout.addWidget(QLabel("Elevacion (deg):"))
        self.spin_elev = QSpinBox()
        self.spin_elev.setRange(-90, 90)
        self.spin_elev.setValue(30)
        self.spin_elev.setSingleStep(5)
        self.spin_elev.setToolTip("Angulo vertical de inclinacion de la camara (-90 a 90 deg).")
        self.spin_elev.valueChanged.connect(self._al_cambiar_camara)
        layout.addWidget(self.spin_elev)

        # 3. Azimut (grados)
        layout.addWidget(QLabel("Azimut (deg):"))
        self.spin_azim = QSpinBox()
        self.spin_azim.setRange(0, 360)
        self.spin_azim.setValue(45)
        self.spin_azim.setSingleStep(5)
        self.spin_azim.setToolTip("Angulo horizontal de rotacion de la camara (0 a 360 deg).")
        self.spin_azim.valueChanged.connect(self._al_cambiar_camara)
        layout.addWidget(self.spin_azim)

        layout.addSpacing(10)

        # 4. Escala Z / Amplitud
        layout.addWidget(QLabel("Escala Z:"))
        self.spin_escala_z = QDoubleSpinBox()
        self.spin_escala_z.setRange(0.1, 10.0)
        self.spin_escala_z.setValue(1.0)
        self.spin_escala_z.setSingleStep(0.2)
        self.spin_escala_z.setToolTip("Multiplicador manual de amplitud para el eje vertical Z (0.1x a 10x).")
        self.spin_escala_z.valueChanged.connect(lambda v: self.cambio_escala_z.emit(v))
        layout.addWidget(self.spin_escala_z)

        # 5. Opciones Visuales (Wireframe y Grid)
        self.chk_wireframe = QCheckBox("Wireframe")
        self.chk_wireframe.setToolTip("Alterna el renderizado a malla de alambre.")
        self.chk_wireframe.toggled.connect(lambda state: self.cambio_modo_render.emit(state))
        layout.addWidget(self.chk_wireframe)

        self.chk_grid = QCheckBox("Cuadricula")
        self.chk_grid.setChecked(True)
        self.chk_grid.setToolTip("Muestra u oculta la cuadricula de los ejes 3D.")
        self.chk_grid.toggled.connect(lambda state: self.cambio_grid.emit(state))
        layout.addWidget(self.chk_grid)

        layout.addSpacing(10)

        # 6. Boton Restablecer
        btn_reset = QPushButton("Restablecer Vista")
        btn_reset.setObjectName("btn_preset")
        btn_reset.setToolTip("Restaura la orientacion inicial de la camara y la escala por defecto.")
        btn_reset.clicked.connect(self.restablecer_vista)
        layout.addWidget(btn_reset)

        layout.addStretch()

    def _al_cambiar_camara(self):
        self.cambio_camara.emit(self.spin_elev.value(), self.spin_azim.value())

    def _al_cambiar_colormap(self, cmap_name: str):
        self.cambio_colormap.emit(cmap_name)

    def restablecer_vista(self):
        """Vuelve los valores de elevacion, azimut y escala a la configuracion por defecto."""
        self.spin_elev.blockSignals(True)
        self.spin_azim.blockSignals(True)
        self.spin_escala_z.blockSignals(True)
        self.chk_wireframe.blockSignals(True)
        self.chk_grid.blockSignals(True)

        self.spin_elev.setValue(30)
        self.spin_azim.setValue(45)
        self.spin_escala_z.setValue(1.0)
        self.chk_wireframe.setChecked(False)
        self.chk_grid.setChecked(True)

        self.spin_elev.blockSignals(False)
        self.spin_azim.blockSignals(False)
        self.spin_escala_z.blockSignals(False)
        self.chk_wireframe.blockSignals(False)
        self.chk_grid.blockSignals(False)

        self.cambio_camara.emit(30, 45)
        self.cambio_escala_z.emit(1.0)
        self.cambio_modo_render.emit(False)
        self.cambio_grid.emit(True)

