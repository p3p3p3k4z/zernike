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
import math
from PySide6.QtWidgets import (

    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox,
    QFileDialog
)
from PySide6.QtCore import Qt, Signal

from lib.matriz import parsear_ecuacion_z

from gui.components.equation_input_widget import EquationInputWidget

_STYLE_ERROR = "border: 2px solid #EF4444; background-color: #FEF2F2; color: #991B1B;"
_STYLE_OK = ""


class ParameterInputPanel(QWidget):
    """
    Panel de control lateral para la configuracion de parametros de la simulacion.
    Emite senales al solicitar ejecuciones o seleccionar archivos.
    """
    ejecutar_solicitado = Signal()
    archivo_csv_seleccionado = Signal(str)
    imagen_interferograma_seleccionada = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()
        self._conectar_validaciones()
        self._validar_inputs()

    @property
    def input_ecuacion(self):
        return self.widget_eq_ccd.input_ecuacion

    @property
    def input_ecuacion_sintetico(self):
        return self.widget_eq_sintetico.input_ecuacion

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
            "3. Círculo Unitario Sintético (N=100)",
            "4. Imagen de Interferograma (PNG, JPG, BMP)"
        ])

        self.combo_modo.setToolTip("Selecciona la fuente de datos para el ajuste de Zernike.")
        self.combo_modo.currentIndexChanged.connect(self._cambio_modo_entrada)
        layout_modo.addWidget(self.combo_modo)
        grupo_modo.setLayout(layout_modo)
        layout.addWidget(grupo_modo)

        # --- Grupo 2: Parametros del Sensor CCD ---
        self.grupo_ccd = QGroupBox("2. Configuración de Superficie & Sensor")
        layout_ccd = QVBoxLayout()

        self.widget_eq_ccd = EquationInputWidget(ecuacion_inicial="3*x*y + 2*x", incluir_presets=True)
        layout_ccd.addWidget(self.widget_eq_ccd)

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

        # Etiqueta informativa dinámica de conteo de píxeles
        self.lbl_info_puntos_ccd = QLabel()
        self.lbl_info_puntos_ccd.setWordWrap(True)
        self.lbl_info_puntos_ccd.setStyleSheet("font-size: 11px; color: #2563EB; font-weight: bold; margin-top: 4px;")
        layout_ccd.addWidget(self.lbl_info_puntos_ccd)

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

        # --- Grupo 3.5: Carga Imagen de Interferograma ---
        self.grupo_interferograma = QGroupBox("2. Imagen de Interferograma")
        layout_img = QVBoxLayout()
        
        layout_path = QHBoxLayout()
        self.input_img_path = QLineEdit()
        self.input_img_path.setPlaceholderText("Ruta de imagen (*.png, *.jpg, *.bmp)")
        btn_examinar_img = QPushButton("Examinar...")
        btn_examinar_img.setToolTip("Busca una imagen de interferograma en tu computadora")
        btn_examinar_img.clicked.connect(self._seleccionar_archivo_imagen)
        layout_path.addWidget(self.input_img_path)
        layout_path.addWidget(btn_examinar_img)
        layout_img.addLayout(layout_path)

        self.btn_abrir_procesador_img = QPushButton("Abrir Procesador (Takeda FFT / Esqueleto)")
        self.btn_abrir_procesador_img.setToolTip("Abre el editor visual para demodular franjas y filtrar espectro 2D")
        self.btn_abrir_procesador_img.setStyleSheet("font-weight: bold; background-color: #2563EB; color: white;")
        layout_img.addWidget(self.btn_abrir_procesador_img)

        self.grupo_interferograma.setLayout(layout_img)
        self.grupo_interferograma.setVisible(False)
        layout.addWidget(self.grupo_interferograma)

        # --- Grupo 3.8: Círculo Unitario Sintético ---
        self.grupo_circulo_sintetico = QGroupBox("2. Círculo Unitario Sintético")
        layout_sint = QVBoxLayout()

        grid_pts = QHBoxLayout()
        grid_pts.addWidget(QLabel("Número de Puntos (N):"))
        self.input_pts_sintetico = QLineEdit("500")
        self.input_pts_sintetico.setToolTip("Cantidad de puntos aleatorios a generar dentro del círculo unitario [-1, 1], ej. 100, 500, 2000, 5000, 10000.")
        grid_pts.addWidget(self.input_pts_sintetico)
        layout_sint.addLayout(grid_pts)

        self.chk_z_aleatorio = QCheckBox("Superficie Z Aleatoria (Combinación Zernike + Ruido)")
        self.chk_z_aleatorio.setChecked(True)
        self.chk_z_aleatorio.setToolTip("Si se activa, genera una superficie óptica sintetizada aleatoriamente variando coeficientes Zernike. Si se desactiva, permite escribir una ecuación Z(x,y) personalizada.")
        self.chk_z_aleatorio.toggled.connect(self._al_alternar_z_aleatorio)
        layout_sint.addWidget(self.chk_z_aleatorio)

        # Campo de Ecuación Z(x,y) personalizada para el círculo utilizando el componente modular
        self.widget_eq_sintetico = EquationInputWidget(ecuacion_inicial="x^2 + y^2", incluir_presets=False)
        self.widget_eq_sintetico.setEnabled(False)
        layout_sint.addWidget(self.widget_eq_sintetico)

        self.chk_semilla_aleatoria = QCheckBox("Semilla Aleatoria (Variar puntos (X,Y) en cada ejecución)")
        self.chk_semilla_aleatoria.setChecked(True)
        self.chk_semilla_aleatoria.setToolTip("Si se activa, genera una nueva muestra espacial de puntos aleatorios en cada ejecución. Si se desactiva, fija la semilla=42.")
        layout_sint.addWidget(self.chk_semilla_aleatoria)

        self.grupo_circulo_sintetico.setLayout(layout_sint)
        self.grupo_circulo_sintetico.setVisible(False)
        layout.addWidget(self.grupo_circulo_sintetico)






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
        self.input_img_path.textChanged.connect(self._validar_inputs)
        self.input_pts_sintetico.textChanged.connect(self._validar_inputs)
        self.input_ecuacion_sintetico.textChanged.connect(self._validar_inputs)

    def _al_alternar_z_aleatorio(self, checked: bool):
        """Habilita o deshabilita la ecuación Z personalizada según si la superficie aleatoria está activa."""
        self.widget_eq_sintetico.setEnabled(not checked)
        self._validar_inputs()


    def _validar_inputs(self):
        """Comprueba la validez de los parámetros y aplica resaltado en rojo para errores."""
        modo = self.combo_modo.currentIndex()
        todo_valido = True

        if modo == 0:  # CCD Sensor
            # Validar Ecuación
            eq = self.input_ecuacion.text().strip()
            if not eq:
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

            # Cálculo y explicación dinámica de píxeles CCD
            try:
                N_val = int(self.input_N.text())
                M_val = int(self.input_M.text())
                d_val = float(self.input_diametro.text())
                total_matriz = N_val * M_val
                # Estimación geométrica exacta de la pupila circular inscrita
                radio_pupila = min(d_val / 2.0, min(N_val, M_val) / 2.0)
                pts_pupila_est = int(math.pi * (radio_pupila ** 2))
                pts_pupila_est = min(pts_pupila_est, total_matriz)
                self.lbl_info_puntos_ccd.setText(
                    f"Matriz Sensor: {N_val}×{M_val} = {total_matriz:,} píxeles\n"
                    f"Puntos útiles (pupila circular): ~{pts_pupila_est:,} pts"
                )
            except ValueError:
                self.lbl_info_puntos_ccd.setText("Matriz Sensor: Ingrese dimensiones válidas (N, M ≥ 5)")



            self.input_csv_path.setStyleSheet(_STYLE_OK)
            self.input_img_path.setStyleSheet(_STYLE_OK)
            self.input_pts_sintetico.setStyleSheet(_STYLE_OK)
            self.input_ecuacion_sintetico.setStyleSheet(_STYLE_OK)

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
            self.input_img_path.setStyleSheet(_STYLE_OK)
            self.input_pts_sintetico.setStyleSheet(_STYLE_OK)
            self.input_ecuacion_sintetico.setStyleSheet(_STYLE_OK)

        elif modo == 3:  # Imagen de Interferograma
            filepath = self.input_img_path.text().strip()
            exts = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
            if not filepath or not os.path.exists(filepath) or not filepath.lower().endswith(exts):
                self.input_img_path.setStyleSheet(_STYLE_ERROR)
                todo_valido = False
            else:
                self.input_img_path.setStyleSheet(_STYLE_OK)

            self.input_ecuacion.setStyleSheet(_STYLE_OK)
            self.input_N.setStyleSheet(_STYLE_OK)
            self.input_M.setStyleSheet(_STYLE_OK)
            self.input_diametro.setStyleSheet(_STYLE_OK)
            self.input_csv_path.setStyleSheet(_STYLE_OK)
            self.input_pts_sintetico.setStyleSheet(_STYLE_OK)
            self.input_ecuacion_sintetico.setStyleSheet(_STYLE_OK)

        else:  # Circulo Sintetico
            try:
                pts = int(self.input_pts_sintetico.text())
                if pts < 5:
                    raise ValueError()
                self.input_pts_sintetico.setStyleSheet(_STYLE_OK)
            except ValueError:
                self.input_pts_sintetico.setStyleSheet(_STYLE_ERROR)
                todo_valido = False

            if not self.chk_z_aleatorio.isChecked():
                eq = self.input_ecuacion_sintetico.text().strip()
                if not eq:
                    self.input_ecuacion_sintetico.setStyleSheet(_STYLE_ERROR)
                    todo_valido = False
                else:
                    self.input_ecuacion_sintetico.setStyleSheet(_STYLE_OK)
            else:
                self.input_ecuacion_sintetico.setStyleSheet(_STYLE_OK)

            self.input_ecuacion.setStyleSheet(_STYLE_OK)
            self.input_N.setStyleSheet(_STYLE_OK)
            self.input_M.setStyleSheet(_STYLE_OK)
            self.input_diametro.setStyleSheet(_STYLE_OK)
            self.input_csv_path.setStyleSheet(_STYLE_OK)
            self.input_img_path.setStyleSheet(_STYLE_OK)

        self.btn_ejecutar.setEnabled(todo_valido)


    def _cambio_modo_entrada(self, index):
        """Muestra u oculta los paneles segun el modo de entrada activo."""
        if index == 0:  # CCD Sensor
            self.grupo_ccd.setVisible(True)
            self.grupo_csv.setVisible(False)
            self.grupo_circulo_sintetico.setVisible(False)
            self.grupo_interferograma.setVisible(False)
        elif index == 1:  # CSV
            self.grupo_ccd.setVisible(False)
            self.grupo_csv.setVisible(True)
            self.grupo_circulo_sintetico.setVisible(False)
            self.grupo_interferograma.setVisible(False)
        elif index == 2:  # Círculo Sintético
            self.grupo_ccd.setVisible(False)
            self.grupo_csv.setVisible(False)
            self.grupo_circulo_sintetico.setVisible(True)
            self.grupo_interferograma.setVisible(False)
        elif index == 3:  # Imagen de Interferograma
            self.grupo_ccd.setVisible(False)
            self.grupo_csv.setVisible(False)
            self.grupo_circulo_sintetico.setVisible(False)
            self.grupo_interferograma.setVisible(True)

        self._validar_inputs()

    def _seleccionar_archivo_csv(self):
        """Abre un cuadro de dialogo nativo para seleccionar un archivo CSV."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV de Superficie Óptica", "", "Archivos CSV (*.csv)")
        if filepath:
            self.input_csv_path.setText(filepath)
            self.combo_modo.setCurrentIndex(1)
            self.archivo_csv_seleccionado.emit(filepath)

    def _seleccionar_archivo_imagen(self):
        """Abre un cuadro de dialogo nativo para seleccionar una imagen de interferograma."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen de Interferograma", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        if filepath:
            self.input_img_path.setText(filepath)
            self.combo_modo.setCurrentIndex(3)
            self._validar_inputs()
            self.imagen_interferograma_seleccionada.emit(filepath)



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
        self.chk_z_aleatorio.setChecked(True)
        self.chk_semilla_aleatoria.setChecked(True)
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





