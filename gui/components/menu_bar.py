"""
gui/components/menu_bar.py
==========================
Componente modular POO que encapsula la barra de menu superior de la aplicacion (QMenuBar).
Organiza los menus Archivo, Herramientas, Ver y Ayuda con acciones independientes.
"""

from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction, QKeySequence, QActionGroup



class AppMenuBar(QMenuBar):
    """
    Barra de menu principal orientada a objetos (POO).
    Emite senales o ejecuta los metodos delegate pasados desde la ventana principal.
    """
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self._construir_menus()

    def _construir_menus(self):
        """Construye las acciones y menus desplegables."""
        if self.controller is None:
            return

        # --- Menu Archivo ---
        menu_archivo = self.addMenu("&Archivo")
        
        act_cargar = QAction("Cargar datos CSV...", self)
        act_cargar.setShortcut(QKeySequence("Ctrl+O"))
        act_cargar.setStatusTip("Carga un archivo CSV con datos experimentales (X, Y, Z)")
        act_cargar.triggered.connect(self.controller._seleccionar_archivo_csv)
        menu_archivo.addAction(act_cargar)

        act_exp_csv = QAction("Exportar Resultados a CSV (.csv)", self)
        act_exp_csv.setShortcut(QKeySequence("Ctrl+S"))
        act_exp_csv.setStatusTip("Exporta las coordenadas X, Y, Z esperadas, ajustadas y error residual a un archivo CSV")
        act_exp_csv.triggered.connect(self.controller._exportar_csv_manual)
        menu_archivo.addAction(act_exp_csv)

        act_exp_zemax = QAction("Exportar a Zemax OpticStudio (.zrn)", self)
        act_exp_zemax.setStatusTip("Exporta los coeficientes ajustados al formato estándar de Zemax")
        act_exp_zemax.triggered.connect(self.controller._exportar_zemax_manual)
        menu_archivo.addAction(act_exp_zemax)


        act_exp_codev = QAction("Exportar a CODE V (.dat)", self)
        act_exp_codev.setStatusTip("Exporta los coeficientes ajustados al formato estándar de CODE V")
        act_exp_codev.triggered.connect(self.controller._exportar_codev_manual)
        menu_archivo.addAction(act_exp_codev)

        menu_archivo.addSeparator()
        act_salir = QAction("Salir", self)
        act_salir.setShortcut(QKeySequence("Ctrl+Q"))
        act_salir.triggered.connect(self.controller.close)
        menu_archivo.addAction(act_salir)

        # --- Menu Herramientas ---
        menu_herramientas = self.addMenu("&Herramientas")
        
        act_ejecutar = QAction("Ejecutar Ajuste de Zernike", self)
        act_ejecutar.setShortcut(QKeySequence("Ctrl+E"))
        act_ejecutar.setStatusTip("Lanza el proceso de cálculo de Gram-Schmidt y Zernike")
        act_ejecutar.triggered.connect(self.controller._ejecutar_ajuste)
        menu_herramientas.addAction(act_ejecutar)

        menu_herramientas.addSeparator()

        act_interferograma = QAction("Analizar Imagen de Interferograma (FFT 2D / Takeda)", self)
        act_interferograma.setStatusTip("Extrae automáticamente el mapa de fase (X, Y, Z) a partir de una imagen de interferograma")
        act_interferograma.triggered.connect(self.controller._lanzar_procesador_interferogramas)
        menu_herramientas.addAction(act_interferograma)

        act_comparar_motores = QAction("Comparar Motores (Python vs. Fortran)", self)
        act_comparar_motores.setStatusTip("Compara matemáticamente y de forma gráfica los resultados de los motores Python y Fortran")
        act_comparar_motores.triggered.connect(self.controller._comparar_motores_calculo)
        menu_herramientas.addAction(act_comparar_motores)

        act_visor_zernike_2d = QAction("Visor 2D de Polinomios de Zernike (21 Polinomios)", self)
        act_visor_zernike_2d.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        act_visor_zernike_2d.setStatusTip("Explora de forma individual cada uno de los 21 Polinomios de Zernike en 2D (Mapa de calor y contornos)")
        act_visor_zernike_2d.triggered.connect(self.controller._mostrar_visor_polinomios_2d)
        menu_herramientas.addAction(act_visor_zernike_2d)

        act_visor_zernike = QAction("Visor 3D de Polinomios de Zernike (21 Polinomios)", self)
        act_visor_zernike.setShortcut(QKeySequence("Ctrl+Z"))
        act_visor_zernike.setStatusTip("Explora de forma individual cada uno de los 21 Polinomios de Zernike en 3D")
        act_visor_zernike.triggered.connect(self.controller._mostrar_visor_polinomios_3d)
        menu_herramientas.addAction(act_visor_zernike)

        menu_herramientas.addSeparator()

        # Submenu de Seleccion de Motor de Calculo
        menu_motor = QMenu("Motor de Cálculo Matemático", self)
        group_motor = QActionGroup(self)
        group_motor.setExclusive(True)

        self.act_motor_py = QAction("Python (NumPy / ISO 10110-5, k=5, L=21)", self, checkable=True)
        self.act_motor_py.setChecked(True)
        self.act_motor_py.setStatusTip("Usa el motor de Python (NumPy, k=5, 21 polinomios, sin limite de puntos)")
        self.act_motor_py.triggered.connect(lambda: self.controller._seleccionar_motor_calculo(0))
        group_motor.addAction(self.act_motor_py)
        menu_motor.addAction(self.act_motor_py)

        self.act_motor_ft = QAction("Fortran Nativo (Gram-Schmidt, k=4, L=15 - Max 50,000 pts)", self, checkable=True)
        self.act_motor_ft.setStatusTip("Usa el motor ejecutor en Fortran nativo (Gram-Schmidt, k=4, 15 polinomios)")
        self.act_motor_ft.triggered.connect(lambda: self.controller._seleccionar_motor_calculo(1))
        group_motor.addAction(self.act_motor_ft)
        menu_motor.addAction(self.act_motor_ft)

        menu_herramientas.addMenu(menu_motor)
        
        menu_herramientas.addSeparator()

        act_reset = QAction("Restablecer Parámetros por Defecto", self)
        act_reset.setShortcut(QKeySequence("Ctrl+R"))
        act_reset.setStatusTip("Restablece todos los campos a sus valores iniciales")
        act_reset.triggered.connect(self.controller._restablecer_defaults)
        menu_herramientas.addAction(act_reset)

        # --- Menu Ver ---
        menu_ver = self.addMenu("&Ver")

        # Submenu Gráficas Flotantes
        menu_graficas = menu_ver.addMenu("Gráficas Flotantes de Análisis")

        act_dist_ccd = QAction("Distribución CCD en 4 Cuadrantes", self)
        act_dist_ccd.setStatusTip("Muestra el plano cartesiano de distribución de puntos en 4 cuadrantes")
        act_dist_ccd.triggered.connect(self.controller._mostrar_grafica_distribucion_ccd_flotante)
        menu_graficas.addAction(act_dist_ccd)

        act_pupila_flotante = QAction("Filtrado por Pupila Óptica", self)
        act_pupila_flotante.setStatusTip("Muestra la gráfica del filtrado circular por pupila óptica")
        act_pupila_flotante.triggered.connect(self.controller._mostrar_grafica_pupila_flotante)
        menu_graficas.addAction(act_pupila_flotante)

        act_3d_flotante = QAction("Mapa de Error Residual 3D", self)
        act_3d_flotante.setStatusTip("Muestra el gráfico tridimensional del error residual")
        act_3d_flotante.triggered.connect(self.controller._mostrar_grafica_3d_flotante)
        menu_graficas.addAction(act_3d_flotante)

        act_sintetico = QAction("Sintetizar Interferograma Óptico desde Zernike", self)
        act_sintetico.setStatusTip("Genera el patrón de interferencia sintético 2D a partir del frente de onda ajustado")
        act_sintetico.triggered.connect(self.controller._mostrar_interferograma_sintetico)
        menu_graficas.addAction(act_sintetico)

        menu_ver.addSeparator()

        # Submenu Flujos y Animaciones
        menu_flujos = menu_ver.addMenu("Flujos y Animaciones")

        act_recursivo = QAction("Animación Recursiva de Zernike", self)
        act_recursivo.setShortcut(QKeySequence("Ctrl+F"))
        act_recursivo.setStatusTip("Muestra exclusivamente la animación de capas de colores y dependencias recursivas (graficar_flujo_zernike)")
        act_recursivo.triggered.connect(self.controller.lanzar_animacion_flujo_zernike)
        menu_flujos.addAction(act_recursivo)

        act_flujo = QAction("Flujo Completo del Algoritmo", self)
        act_flujo.setStatusTip("Abre la secuencia completa de ventanas y representaciones gráficas del algoritmo")
        act_flujo.triggered.connect(self.controller.lanzar_flujo_completo_zernike)
        menu_flujos.addAction(act_flujo)

        menu_ver.addSeparator()

        act_tema = QAction("Alternar Tema Claro / Oscuro", self)
        act_tema.setShortcut(QKeySequence("Ctrl+T"))
        act_tema.triggered.connect(self.controller._toggle_tema)
        menu_ver.addAction(act_tema)


        # --- Menu Ayuda ---
        menu_ayuda = self.addMenu("Ayud&a")
        
        act_manual = QAction("Manual de Usuario y Guía de Zernike (F1)", self)
        act_manual.setShortcut(QKeySequence("F1"))
        act_manual.triggered.connect(self.controller._abrir_manual)
        menu_ayuda.addAction(act_manual)

        act_acerca = QAction("Acerca de Zernike", self)
        act_acerca.triggered.connect(self.controller._abrir_acerca_de)
        menu_ayuda.addAction(act_acerca)
