"""
gui/components/parameter_panel.py
=================================
Componente reutilizable que encapsula los controles de entrada de parametros:
- Seleccion del modo de simulacion (CCD, CSV, Circulo)
- Ecuacion matematica y botones de preset rapido
- Dimensiones del sensor CCD y diametro de pupila
- Carga de archivos CSV
- Opciones de exportacion
- Boton principal de ejecucion
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox,
    QFileDialog
)
from PySide6.QtCore import Qt, Signal

from lib.matriz import parsear_ecuacion_z

_STYLE_ERROR = "border: 2px solid #EF4444; background-color: #FEF2F2; color: #991B1B;"
_STYLE_OK = ""


class ParameterInputPanel(QWidget):
    """
    Panel de control lateral para la configuracion de parametros de la simulacion.
    Emite senales al solicitar ejecuciones o seleccionar archivos.
    """
    ejecutar_solicitado = Signal()
    archivo_csv_seleccionado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()
        self._conectar_validaciones()
        self._validar_inputs()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # --- Grupo 1: Modo de Entrada ---
        grupo_modo = QGroupBox("1. Modo de Simulación Óptica")
        layout_modo = QVBoxLayout()
        
        self.combo_modo = QComboBox()
        self.combo_modo.addItems([
            "1. CCD Sensor (Malla NxM simétrica)",
            "2. Archivo CSV Experimental (X, Y, Z)",
            "3. Círculo Unitario Sintético (N=100)"
        ])
        self.combo_modo.setToolTip("Selecciona la fuente de datos para el ajuste de Zernike.")
        self.combo_modo.currentIndexChanged.connect(self._cambio_modo_entrada)
        layout_modo.addWidget(self.combo_modo)
        grupo_modo.setLayout(layout_modo)
        layout.addWidget(grupo_modo)

        # --- Grupo 2: Parametros del Sensor CCD ---
        self.grupo_ccd = QGroupBox("2. Configuración de Superficie & Sensor")
        layout_ccd = QVBoxLayout()

        layout_ccd.addWidget(QLabel("Ecuación Z(x,y):"))
        self.input_ecuacion = QLineEdit("3*x*y + 2*x")
        self.input_ecuacion.setToolTip("Introduce una función cartesiana o trigonométrica (ej. sin(x) + cos(y)).")
        layout_ccd.addWidget(self.input_ecuacion)

        # Presets de Ecuaciones Rapidas
        lbl_presets = QLabel("Ecuaciones de prueba rapidas:")
        lbl_presets.setStyleSheet("font-size: 11px; color: #64748B;")
        layout_ccd.addWidget(lbl_presets)

        btn_gestor = QPushButton("Gestor de Presets e Historial...")
        btn_gestor.setObjectName("btn_preset")
        btn_gestor.setToolTip("Abre el administrador de presets opticos, historial reciente y ecuaciones guardadas.")
        btn_gestor.clicked.connect(self._abrir_gestor_presets)
        layout_ccd.addWidget(btn_gestor)

        grid_presets = QGridLayout()
        btn_p1 = QPushButton("Astigmatismo (3xy)")
        btn_p1.setObjectName("btn_preset")
        btn_p1.clicked.connect(lambda: self.input_ecuacion.setText("3*x*y + 2*x"))
        
        btn_p2 = QPushButton("Onda (sin(x)+cos(y))")
        btn_p2.setObjectName("btn_preset")
        btn_p2.clicked.connect(lambda: self.input_ecuacion.setText("sin(x) + cos(y)"))

        btn_p3 = QPushButton("Desenfoque (x^2+y^2)")
        btn_p3.setObjectName("btn_preset")
        btn_p3.clicked.connect(lambda: self.input_ecuacion.setText("x^2 + y^2"))

        btn_p4 = QPushButton("3er Orden Complejo")
        btn_p4.setObjectName("btn_preset")
        btn_p4.clicked.connect(lambda: self.input_ecuacion.setText("-y - 1.5*y*y*y + 1.5*x*x*y + x*y*y - 0.33*x*x*x + 2*x*x + 2*y*y + 0.5*x - 1"))

        grid_presets.addWidget(btn_p1, 0, 0)
        grid_presets.addWidget(btn_p2, 0, 1)
        grid_presets.addWidget(btn_p3, 1, 0)
        grid_presets.addWidget(btn_p4, 1, 1)
        layout_ccd.addLayout(grid_presets)


        # Dimensiones de la malla
        grid_dim = QGridLayout()
        grid_dim.addWidget(QLabel("Filas (N):"), 0, 0)
        self.input_N = QLineEdit("100")
        self.input_N.setToolTip("Número de filas de píxeles del sensor (mínimo 5).")
        grid_dim.addWidget(self.input_N, 0, 1)

        grid_dim.addWidget(QLabel("Columnas (M):"), 1, 0)
        self.input_M = QLineEdit("100")
        self.input_M.setToolTip("Número de columnas de píxeles del sensor (mínimo 5).")
        grid_dim.addWidget(self.input_M, 1, 1)

        grid_dim.addWidget(QLabel("Diámetro Pupila (px):"), 2, 0)
        self.input_diametro = QLineEdit("100")
        self.input_diametro.setToolTip("Diámetro en píxeles de la apertura circular de la pupila.")
        grid_dim.addWidget(self.input_diametro, 2, 1)

        layout_ccd.addLayout(grid_dim)
        self.grupo_ccd.setLayout(layout_ccd)
        layout.addWidget(self.grupo_ccd)

        # --- Grupo 3: Carga CSV ---
        self.grupo_csv = QGroupBox("2. Archivo de Entrada CSV")
        layout_csv = QHBoxLayout()
        self.input_csv_path = QLineEdit()
        self.input_csv_path.setPlaceholderText("Ruta del archivo .csv")
        btn_examinar = QPushButton("Examinar...")
        btn_examinar.setToolTip("Busca un archivo CSV en tu computadora")
        btn_examinar.clicked.connect(self._seleccionar_archivo_csv)
        layout_csv.addWidget(self.input_csv_path)
        layout_csv.addWidget(btn_examinar)
        self.grupo_csv.setLayout(layout_csv)
        self.grupo_csv.setVisible(False)
        layout.addWidget(self.grupo_csv)

        # --- Grupo 4: Exportacion Opcional ---
        grupo_exp = QGroupBox("3. Archivos de Salida (Opcionales)")
        layout_exp = QVBoxLayout()
        self.chk_exp_csv = QCheckBox("Exportar CSV de Resultados (output/zernike_resultados.csv)")
        self.chk_exp_zemax = QCheckBox("Exportar Formato Zemax (output/zemax_zernike.zrn)")
        self.chk_exp_codev = QCheckBox("Exportar Formato CODE V (output/codev_zernike.dat)")
        layout_exp.addWidget(self.chk_exp_csv)
        layout_exp.addWidget(self.chk_exp_zemax)
        layout_exp.addWidget(self.chk_exp_codev)
        grupo_exp.setLayout(layout_exp)
        layout.addWidget(grupo_exp)

        # --- Boton Principal de Ejecucion ---
        self.btn_ejecutar = QPushButton("EJECUTAR AJUSTE DE ZERNIKE (Ctrl+E)")
        self.btn_ejecutar.setMinimumHeight(44)
        self.btn_ejecutar.setCursor(Qt.PointingHandCursor)
        self.btn_ejecutar.setToolTip("Inicia la evaluación matemática, ortogonalización de Gram-Schmidt y generación de gráficos.")
        self.btn_ejecutar.clicked.connect(self.ejecutar_solicitado.emit)
        layout.addWidget(self.btn_ejecutar)

        layout.addStretch()

    def _conectar_validaciones(self):
        """Conecta las señales de modificación de texto con la rutina de validación."""
        self.input_ecuacion.textChanged.connect(self._validar_inputs)
        self.input_N.textChanged.connect(self._validar_inputs)
        self.input_M.textChanged.connect(self._validar_inputs)
        self.input_diametro.textChanged.connect(self._validar_inputs)
        self.input_csv_path.textChanged.connect(self._validar_inputs)

    def _validar_inputs(self):
        """Comprueba la validez de los parámetros y aplica resaltado en rojo para errores."""
        modo = self.combo_modo.currentIndex()
        todo_valido = True

        if modo == 0:  # CCD Sensor
            # Validar Ecuación
            eq_str = self.input_ecuacion.text().strip()
            func_z = parsear_ecuacion_z(eq_str) if eq_str else None
            if not eq_str or func_z is None:
                self.input_ecuacion.setStyleSheet(_STYLE_ERROR)
                todo_valido = False
            else:
                self.input_ecuacion.setStyleSheet(_STYLE_OK)

            # Validar N
            try:
                N = int(self.input_N.text())
                if N < 5:
                    raise ValueError()
                self.input_N.setStyleSheet(_STYLE_OK)
            except ValueError:
                self.input_N.setStyleSheet(_STYLE_ERROR)
                todo_valido = False

            # Validar M
            try:
                M = int(self.input_M.text())
                if M < 5:
                    raise ValueError()
                self.input_M.setStyleSheet(_STYLE_OK)
            except ValueError:
                self.input_M.setStyleSheet(_STYLE_ERROR)
                todo_valido = False

            # Validar Diámetro
            try:
                diametro = float(self.input_diametro.text())
                if diametro <= 0:
                    raise ValueError()
                self.input_diametro.setStyleSheet(_STYLE_OK)
            except ValueError:
                self.input_diametro.setStyleSheet(_STYLE_ERROR)
                todo_valido = False

            self.input_csv_path.setStyleSheet(_STYLE_OK)

        elif modo == 1:  # CSV Experimental
            filepath = self.input_csv_path.text().strip()
            if not filepath or not os.path.exists(filepath) or not filepath.lower().endswith(".csv"):
                self.input_csv_path.setStyleSheet(_STYLE_ERROR)
                todo_valido = False
            else:
                self.input_csv_path.setStyleSheet(_STYLE_OK)

            self.input_ecuacion.setStyleSheet(_STYLE_OK)
            self.input_N.setStyleSheet(_STYLE_OK)
            self.input_M.setStyleSheet(_STYLE_OK)
            self.input_diametro.setStyleSheet(_STYLE_OK)

        else:  # Circulo Sintetico
            self.input_ecuacion.setStyleSheet(_STYLE_OK)
            self.input_N.setStyleSheet(_STYLE_OK)
            self.input_M.setStyleSheet(_STYLE_OK)
            self.input_diametro.setStyleSheet(_STYLE_OK)
            self.input_csv_path.setStyleSheet(_STYLE_OK)

        self.btn_ejecutar.setEnabled(todo_valido)

    def _cambio_modo_entrada(self, index):
        """Muestra u oculta los paneles segun el modo de entrada activo."""
        if index == 0:  # CCD Sensor
            self.grupo_ccd.setVisible(True)
            self.grupo_csv.setVisible(False)
        elif index == 1:  # CSV
            self.grupo_ccd.setVisible(False)
            self.grupo_csv.setVisible(True)
        else:  # Circulo
            self.grupo_ccd.setVisible(False)
            self.grupo_csv.setVisible(False)

        self._validar_inputs()

    def _seleccionar_archivo_csv(self):
        """Abre un cuadro de dialogo nativo para seleccionar un archivo CSV."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV de Superficie Óptica", "", "Archivos CSV (*.csv)")
        if filepath:
            self.input_csv_path.setText(filepath)
            self.combo_modo.setCurrentIndex(1)
            self.archivo_csv_seleccionado.emit(filepath)

    def restablecer_defaults(self):
        """Restablece los campos a su estado por defecto."""
        self.combo_modo.setCurrentIndex(0)
        self.input_ecuacion.setText("3*x*y + 2*x")
        self.input_N.setText("100")
        self.input_M.setText("100")
        self.input_diametro.setText("100")
        self.input_csv_path.clear()
        self.chk_exp_csv.setChecked(False)
        self.chk_exp_zemax.setChecked(False)
        self.chk_exp_codev.setChecked(False)
        self._validar_inputs()

    def _abrir_gestor_presets(self):
        """Abre el cuadro de dialogo interactivo del Gestor de Presets e Historial."""
        from gui.components.preset_manager import PresetManagerDialog

        dlg = PresetManagerDialog(ecuacion_actual=self.input_ecuacion.text(), parent=self)
        dlg.ecuacion_seleccionada.connect(self._al_seleccionar_preset)
        dlg.exec()

    def _al_seleccionar_preset(self, ecuacion: str):
        """Aplica la ecuacion seleccionada en el gestor al campo de texto."""
        self.input_ecuacion.setText(ecuacion)
        self._validar_inputs()


