"""
gui/components/control_bar_3d.py
================================
Barra de controles interactivos para manipular en tiempo real la camara (elevacion, azimut) 
y el mapa de colores (colormap) del lienzo de visualización 3D del Error Residual.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton
)
from PySide6.QtCore import Signal, Qt


class ControlBar3D(QWidget):
    """
    Toolbar modular en 2 filas con controles para ajustar la perspectiva 3D/2D, Colormap,
    escala manual de Z, modo de renderizado, cuadrícula, resolución de grilla, suavizado e isolíneas.
    """
    cambio_camara = Signal(int, int)
    cambio_colormap = Signal(str)
    cambio_escala_z = Signal(float)
    cambio_modo_render = Signal(bool)
    cambio_grid = Signal(bool)
    cambio_suavizado = Signal(int, float)
    cambio_modo_vista = Signal(bool)   # True = 3D, False = 2D
    cambio_contornos  = Signal(bool, int)  # (activo, n_niveles)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(6, 4, 6, 4)
        layout_principal.setSpacing(4)

        layout_fila1 = QHBoxLayout()
        layout_fila1.setContentsMargins(0, 0, 0, 0)
        layout_fila1.setSpacing(8)

        layout_fila2 = QHBoxLayout()
        layout_fila2.setContentsMargins(0, 0, 0, 0)
        layout_fila2.setSpacing(8)

        # --- FILA 1: Perspectiva, Cámara y Rango ---
        self.btn_modo_vista = QPushButton("Vista 3D")
        self.btn_modo_vista.setCheckable(True)
        self.btn_modo_vista.setChecked(False)
        self.btn_modo_vista.setToolTip("Alterna la visualización entre superficie 3D y mapa de calor 2D.")
        self.btn_modo_vista.toggled.connect(self._al_cambiar_modo_vista)
        layout_fila1.addWidget(self.btn_modo_vista)

        layout_fila1.addSpacing(6)

        layout_fila1.addWidget(QLabel("Mapa de Colores:"))
        self.combo_cmap = QComboBox()
        self.combo_cmap.addItems([
            "viridis", "coolwarm", "seismic", "twilight", "inferno", "plasma", "magma", "rainbow", "Spectral", "jet", "cividis"
        ])
        self.combo_cmap.setToolTip("Selecciona el mapa de colores para la representación gráfica.")
        self.combo_cmap.currentTextChanged.connect(self._al_cambiar_colormap)
        layout_fila1.addWidget(self.combo_cmap)

        layout_fila1.addSpacing(6)

        layout_fila1.addWidget(QLabel("Elevación (deg):"))
        self.spin_elev = QSpinBox()
        self.spin_elev.setRange(-90, 90)
        self.spin_elev.setValue(30)
        self.spin_elev.setSingleStep(5)
        self.spin_elev.setToolTip("Ángulo vertical de inclinación de la cámara (-90 a 90 deg).")
        self.spin_elev.valueChanged.connect(self._al_cambiar_camara)
        layout_fila1.addWidget(self.spin_elev)

        layout_fila1.addWidget(QLabel("Azimut (deg):"))
        self.spin_azim = QSpinBox()
        self.spin_azim.setRange(0, 360)
        self.spin_azim.setValue(45)
        self.spin_azim.setSingleStep(5)
        self.spin_azim.setToolTip("Ángulo horizontal de rotación de la cámara (0 a 360 deg).")
        self.spin_azim.valueChanged.connect(self._al_cambiar_camara)
        layout_fila1.addWidget(self.spin_azim)

        layout_fila1.addSpacing(6)

        layout_fila1.addWidget(QLabel("Escala Z:"))
        self.spin_escala_z = QDoubleSpinBox()
        self.spin_escala_z.setRange(0.1, 10.0)
        self.spin_escala_z.setValue(1.0)
        self.spin_escala_z.setSingleStep(0.2)
        self.spin_escala_z.setToolTip("Multiplicador manual de amplitud para el eje vertical Z (0.1x a 10x).")
        self.spin_escala_z.valueChanged.connect(lambda v: self.cambio_escala_z.emit(v))
        layout_fila1.addWidget(self.spin_escala_z)

        layout_fila1.addStretch()

        # --- FILA 2: Opciones de Malla, Filtros Espaciales e Isolíneas ---
        self.chk_wireframe = QCheckBox("Wireframe")
        self.chk_wireframe.setToolTip("Alterna el renderizado a malla de alambre en vista 3D.")
        self.chk_wireframe.toggled.connect(lambda state: self.cambio_modo_render.emit(state))
        layout_fila2.addWidget(self.chk_wireframe)

        self.chk_grid = QCheckBox("Cuadrícula")
        self.chk_grid.setChecked(True)
        self.chk_grid.setToolTip("Muestra u oculta la cuadrícula de los ejes.")
        self.chk_grid.toggled.connect(lambda state: self.cambio_grid.emit(state))
        layout_fila2.addWidget(self.chk_grid)

        layout_fila2.addSpacing(6)

        layout_fila2.addWidget(QLabel("Grilla:"))
        self.spin_n_grid = QSpinBox()
        self.spin_n_grid.setRange(30, 200)
        self.spin_n_grid.setValue(80)
        self.spin_n_grid.setSingleStep(10)
        self.spin_n_grid.setToolTip("Resolución de la grilla regular de interpolación cúbica (30 a 200 puntos por lado).")
        self.spin_n_grid.valueChanged.connect(self._al_cambiar_suavizado)
        layout_fila2.addWidget(self.spin_n_grid)

        layout_fila2.addSpacing(6)

        layout_fila2.addWidget(QLabel("Suavizado (sigma):"))
        self.spin_sigma = QDoubleSpinBox()
        self.spin_sigma.setRange(0.0, 5.0)
        self.spin_sigma.setValue(0.0)
        self.spin_sigma.setSingleStep(0.5)
        self.spin_sigma.setToolTip("Factor de suavizado gaussiano espacial para atenuar picos de ruido (0.0 = desactivado).")
        self.spin_sigma.valueChanged.connect(self._al_cambiar_suavizado)
        layout_fila2.addWidget(self.spin_sigma)

        layout_fila2.addSpacing(6)

        self.chk_contornos = QCheckBox("Curvas de Nivel")
        self.chk_contornos.setChecked(False)
        self.chk_contornos.setToolTip("Superpone curvas de nivel (isolíneas) sobre la vista activa.")
        self.chk_contornos.toggled.connect(self._al_cambiar_contornos)
        layout_fila2.addWidget(self.chk_contornos)

        layout_fila2.addWidget(QLabel("Niveles:"))
        self.spin_n_contornos = QSpinBox()
        self.spin_n_contornos.setRange(3, 50)
        self.spin_n_contornos.setValue(10)
        self.spin_n_contornos.setSingleStep(1)
        self.spin_n_contornos.setToolTip("Número de curvas de nivel a dibujar (3 a 50).")
        self.spin_n_contornos.valueChanged.connect(self._al_cambiar_contornos)
        layout_fila2.addWidget(self.spin_n_contornos)

        layout_fila2.addSpacing(10)

        btn_reset = QPushButton("Restablecer Vista")
        btn_reset.setObjectName("btn_preset")
        btn_reset.setToolTip("Restaura la orientación inicial de la cámara, escala, suavizado y filtros por defecto.")
        btn_reset.clicked.connect(self.restablecer_vista)
        layout_fila2.addWidget(btn_reset)

        layout_fila2.addStretch()

        layout_principal.addLayout(layout_fila1)
        layout_principal.addLayout(layout_fila2)

    def _al_cambiar_camara(self):
        self.cambio_camara.emit(self.spin_elev.value(), self.spin_azim.value())

    def _al_cambiar_colormap(self, cmap_name: str):
        self.cambio_colormap.emit(cmap_name)

    def _al_cambiar_suavizado(self):
        self.cambio_suavizado.emit(self.spin_n_grid.value(), self.spin_sigma.value())

    def _al_cambiar_modo_vista(self, activado: bool):
        """Actualiza el texto del boton y emite la senal de cambio de modo de vista."""
        self.btn_modo_vista.setText("Vista 2D" if activado else "Vista 3D")
        # Deshabilitar controles de camara que no aplican en la vista 2D plana.
        es_3d = not activado
        self.spin_elev.setEnabled(es_3d)
        self.spin_azim.setEnabled(es_3d)
        self.chk_wireframe.setEnabled(es_3d)
        self.cambio_modo_vista.emit(not activado)

    def _al_cambiar_contornos(self):
        """Emite la senal de curvas de nivel con el estado y numero de niveles actuales."""
        self.cambio_contornos.emit(
            self.chk_contornos.isChecked(),
            self.spin_n_contornos.value(),
        )

    def restablecer_vista(self):
        """Vuelve todos los controles a la configuracion inicial por defecto."""
        controles = [
            self.spin_elev, self.spin_azim, self.spin_escala_z,
            self.spin_n_grid, self.spin_sigma,
            self.chk_wireframe, self.chk_grid,
            self.btn_modo_vista, self.chk_contornos, self.spin_n_contornos,
        ]
        for ctrl in controles:
            ctrl.blockSignals(True)

        self.spin_elev.setValue(30)
        self.spin_azim.setValue(45)
        self.spin_escala_z.setValue(1.0)
        self.spin_n_grid.setValue(80)
        self.spin_sigma.setValue(0.0)
        self.chk_wireframe.setChecked(False)
        self.chk_grid.setChecked(True)
        self.btn_modo_vista.setChecked(False)
        self.btn_modo_vista.setText("Vista 3D")
        self.chk_contornos.setChecked(False)
        self.spin_n_contornos.setValue(10)
        # Restaurar el estado habilitado de los controles de camara.
        for ctrl in [self.spin_elev, self.spin_azim, self.chk_wireframe]:
            ctrl.setEnabled(True)

        for ctrl in controles:
            ctrl.blockSignals(False)

        self.cambio_camara.emit(30, 45)
        self.cambio_escala_z.emit(1.0)
        self.cambio_suavizado.emit(80, 0.0)
        self.cambio_modo_render.emit(False)
        self.cambio_grid.emit(True)
        self.cambio_modo_vista.emit(True)  # True = modo 3D activo
        self.cambio_contornos.emit(False, 10)

