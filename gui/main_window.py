"""
gui/main_window.py
==================
Controlador principal de la interfaz grafica para el analisis y caracterizacion de 
superficies opticas con Polinomios de Zernike (ISO 10110-5).

Orquesta los componentes modulares (ParameterInputPanel, SummaryTablesWidget, 
MplCanvasWidget, dialogs y styles).
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QFileDialog,
    QMessageBox, QStatusBar, QSplitter, QProgressBar, QLabel, QToolBar
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QAction, QIcon

from gui.canvas import MplCanvasWidget
from gui.styles import obtener_estilo_tema
from gui.dialogs import mostrar_manual_usuario, mostrar_acerca_de, mostrar_ventana_3d_error_residual
from gui.zernike_viewer_dialog import ZernikeViewer3DDialog
from gui.engine_comparison_dialog import EngineComparisonDialog
from gui.interferogram_dialog import InterferogramProcessorDialog



from gui.components import ParameterInputPanel, SummaryTablesWidget, AppMenuBar, ControlBar3D

from gui.worker import ZernikeWorker

from lib.zernike import polinomios_zernike, ajuste_completo
from lib.matriz import (
    generar_malla_ccd, centrar_coordenadas, filtrar_pupila,
    parsear_ecuacion_z, generar_datos_circulo, normalizar_vector
)
from lib.io import exportar_resultados_csv, exportar_zemax, exportar_codev, cargar_datos_csv
from lib.visualizacion import (
    mapa_fase_3d, graficar_flujo_zernike, graficar_pupila,
    graficar_distribucion_ccd, graficar_interferograma_sintetico
)



class ZernikeZemaxMainWindow(QMainWindow):
    """
    Ventana principal de escritorio (Controlador).
    Orquesta el panel de parametros, las tablas de aberraciones y los lienzos de Matplotlib.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zernike — Polinomios Ortogonales de Superficies Ópticas (ISO 10110-5)")
        self.resize(1340, 860)
        self.setMinimumSize(1024, 700)

        # Cargar icono de la aplicación
        ruta_base = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        ruta_icono_png = os.path.join(ruta_base, "assets", "icon.png")
        ruta_icono_ico = os.path.join(ruta_base, "assets", "icon.ico")
        if os.path.exists(ruta_icono_png):
            self.setWindowIcon(QIcon(ruta_icono_png))
        elif os.path.exists(ruta_icono_ico):
            self.setWindowIcon(QIcon(ruta_icono_ico))

        # Variables de estado del modelo
        self.ultimo_resultado = None
        self.ultimas_coordenadas = None
        self.animacion_flotante = None  # Referencia para evitar GC de FuncAnimation
        self.tema_actual = "claro"
        self.motor_actual = 0  # 0: Python, 1: Fortran
        self.worker = None


        # Construir Interfaz primero
        self._crear_interfaz_principal()
        self._crear_menu_bar()


        
        # Barra de Estado (Heuristica 1: Visibilidad del Estado del Sistema)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.lbl_estado_icon = QLabel("Listo")
        self.status_bar.addPermanentWidget(self.lbl_estado_icon)

        # Aplicar Tema Inicial
        self._aplicar_estilo_tema("claro")
        self.status_bar.showMessage("Sistema listo. Configura los parámetros y haz clic en 'Ejecutar Ajuste' (Ctrl+E).")

    # =========================================================================
    # PROPIEDADES DE COMPATIBILIDAD CON COMPONENTES MODULARES
    # =========================================================================
    @property
    def combo_modo(self):
        return self.panel_parametros.combo_modo

    @property
    def input_ecuacion(self):
        return self.panel_parametros.input_ecuacion

    @property
    def input_N(self):
        return self.panel_parametros.input_N

    @property
    def input_M(self):
        return self.panel_parametros.input_M

    @property
    def input_diametro(self):
        return self.panel_parametros.input_diametro

    @property
    def input_csv_path(self):
        return self.panel_parametros.input_csv_path

    @property
    def chk_exp_csv(self):
        return self.panel_parametros.chk_exp_csv

    @property
    def chk_exp_zemax(self):
        return self.panel_parametros.chk_exp_zemax

    @property
    def chk_exp_codev(self):
        return self.panel_parametros.chk_exp_codev

    @property
    def btn_ejecutar(self):
        return self.panel_parametros.btn_ejecutar

    @property
    def tabla_coef(self):
        return self.summary_tables.tabla_coef

    @property
    def tabla_aberraciones(self):
        return self.summary_tables.tabla_aberraciones

    @property
    def card_rms(self):
        return self.summary_tables.card_rms

    # =========================================================================
    # ESTILOS Y TEMAS
    # =========================================================================
    def _aplicar_estilo_tema(self, tema="claro"):
        """Aplica el estilo visual CSS centralizado en gui.styles."""
        self.tema_actual = tema
        css = obtener_estilo_tema(tema)
        self.setStyleSheet(css)
        self.summary_tables.aplicar_tema(tema)

        if hasattr(self, '_dialog_visor_3d') and self._dialog_visor_3d is not None and self._dialog_visor_3d.isVisible():
            self._dialog_visor_3d.setStyleSheet(css)
            self._dialog_visor_3d._actualizar_grafico_3d()

        if hasattr(self, '_dialog_3d') and self._dialog_3d is not None and self._dialog_3d.isVisible():
            self._dialog_3d.setStyleSheet(css)
            self._dialog_3d._actualizar_grafico_3d()

        if hasattr(self, '_dialog_interferograma') and self._dialog_interferograma is not None and self._dialog_interferograma.isVisible():
            self._dialog_interferograma.setStyleSheet(css)
            self._dialog_interferograma._procesar_interferograma()

        if hasattr(self, '_dialog_comparacion') and self._dialog_comparacion is not None and self._dialog_comparacion.isVisible():
            self._dialog_comparacion.setStyleSheet(css)
            self._dialog_comparacion._ejecutar_comparacion()

        if hasattr(self, '_redibujar_3d_main'):
            self._redibujar_3d_main()



    # =========================================================================
    # MENUS DE LA APLICACION (POO Componente AppMenuBar)
    # =========================================================================
    def _crear_menu_bar(self):
        """Instancia la barra de menu principal modular POO."""
        self.menu_bar = AppMenuBar(self, controller=self)
        self.setMenuBar(self.menu_bar)




    def _abrir_manual(self):
        """Despliega el manual de usuario modal."""
        mostrar_manual_usuario(self)

    def _abrir_acerca_de(self):
        """Despliega el cuadro de informacion modal."""
        mostrar_acerca_de(self)

    # =========================================================================
    # CONSTRUCCION DE LA INTERFAZ CENTRAL MODULAR
    # =========================================================================
    def _crear_interfaz_principal(self):
        """Ensambla los componentes modulares ParameterInputPanel y SummaryTablesWidget."""
        widget_central = QWidget()
        layout_central = QHBoxLayout(widget_central)
        layout_central.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Horizontal)

        # Panel Izquierdo Modular: Control de Parametros
        self.panel_parametros = ParameterInputPanel(self)
        self.panel_parametros.ejecutar_solicitado.connect(self._ejecutar_ajuste)
        self.panel_parametros.imagen_interferograma_seleccionada.connect(self._al_seleccionar_imagen_interferograma)
        self.panel_parametros.btn_abrir_procesador_img.clicked.connect(self._lanzar_procesador_interferogramas)
        self.panel_parametros.combo_modo.currentIndexChanged.connect(self._al_cambiar_modo_entrada)
        splitter.addWidget(self.panel_parametros)




        # Panel Derecho Modular: Pestanas de Resultados y Lienzos
        panel_derecho = self._crear_panel_pestanas()
        splitter.addWidget(panel_derecho)

        # Proporcion inicial: 32% lateral, 68% visualizacion
        splitter.setSizes([380, 920])

        layout_central.addWidget(splitter)
        self.setCentralWidget(widget_central)

    def _crear_panel_pestanas(self) -> QWidget:
        """Crea el contenedor con las 4 pestañas principales de visualización."""
        self.tabs = QTabWidget()

        # Tab 1 Modular: Resumen & Aberraciones
        self.summary_tables = SummaryTablesWidget(self)
        self.summary_tables.notificacion_copia.connect(lambda msg: self.status_bar.showMessage(msg, 3500))
        self.tabs.addTab(self.summary_tables, "Resumen & Aberraciones")

        # Tab 2: Malla CCD & Pupila (2D Canvas)
        self.canvas_ccd = MplCanvasWidget(self)
        self.tabs.addTab(self.canvas_ccd, "Malla CCD & Pupila")

        # Tab 3: Error Residual 3D (3D Canvas con Toolbar de control)
        container_3d = QWidget()
        layout_3d = QVBoxLayout(container_3d)
        layout_3d.setContentsMargins(0, 0, 0, 0)

        self.control_bar_3d = ControlBar3D(self)
        self.control_bar_3d.cambio_camara.connect(self._al_cambiar_camara_3d)
        self.control_bar_3d.cambio_colormap.connect(self._al_cambiar_colormap_3d)
        self.control_bar_3d.cambio_escala_z.connect(lambda val: self._redibujar_3d_main())
        self.control_bar_3d.cambio_modo_render.connect(lambda mode: self._redibujar_3d_main())
        self.control_bar_3d.cambio_grid.connect(lambda grid: self._redibujar_3d_main())
        self.control_bar_3d.cambio_suavizado.connect(lambda n, s: self._redibujar_3d_main())
        layout_3d.addWidget(self.control_bar_3d)

        self.canvas_3d = MplCanvasWidget(self)
        layout_3d.addWidget(self.canvas_3d)

        self.tabs.addTab(container_3d, "Error Residual 3D")

        # Tab 4: Interferograma Sintético (2D Canvas)
        self.canvas_sintetico = MplCanvasWidget(self)
        self.tabs.addTab(self.canvas_sintetico, "Interferograma Sintético")

        self.tabs.currentChanged.connect(self._al_cambiar_pestana_principal)

        return self.tabs

    def _al_cambiar_pestana_principal(self, index: int):
        """
        Programa el redibujo de la pestana activa de forma diferida con QTimer.singleShot(0).
        El diferimiento garantiza que el layout de QTabWidget haya terminado de asignar
        las dimensiones finales del contenedor antes de que Matplotlib renderice.
        Un retardo adicional de 50 ms se aplica a la pestana 3D para estabilizar
        la proyeccion de la camara antes del primer dibujo.
        """
        from PySide6.QtCore import QTimer

        if index == 1 and hasattr(self, 'canvas_ccd'):
            QTimer.singleShot(0, self.canvas_ccd._redibujar_con_rescalado)

        elif index == 2 and hasattr(self, 'canvas_3d'):
            QTimer.singleShot(50, self._redibujar_3d_main)

        elif index == 3 and hasattr(self, 'canvas_sintetico'):
            QTimer.singleShot(0, self.canvas_sintetico._redibujar_con_rescalado)






    # =========================================================================
    # EJECUCION & MOTOR MATEMATICO DE ZERNIKE (ASINCRONO CON QTHREAD)
    # =========================================================================
    def _ejecutar_ajuste(self):
        """Valida las entradas y ejecuta el motor de calculo Zernike en segundo plano."""
        modo = self.panel_parametros.combo_modo.currentIndex()
        eq_str = self.panel_parametros.input_ecuacion.text().strip()
        
        if modo == 0 and eq_str:
            from gui.components.preset_manager import PresetStorage
            PresetStorage().agregar_historial(eq_str)

        
        if modo == 2:
            try:
                N = int(self.panel_parametros.input_pts_sintetico.text())
                M = N
            except ValueError:
                N, M = 500, 500
        else:
            try:
                N = int(self.panel_parametros.input_N.text())
                M = int(self.panel_parametros.input_M.text())
            except ValueError:
                N, M = 100, 100


        try:
            diametro = float(self.panel_parametros.input_diametro.text())
        except ValueError:
            diametro = 100.0

        filepath = self.panel_parametros.input_csv_path.text().strip()
        img_filepath = self.panel_parametros.input_img_path.text().strip()
        motor = self.motor_actual

        datos_directos = None
        if modo == 3:
            datos_directos = getattr(self, 'datos_interferograma_cargados', None)
            if datos_directos is None and img_filepath:
                from lib.interferometria import (
                    cargar_y_normalizar_imagen, recortar_y_limpiar_interferograma,
                    demodular_fase_fft2d, desenvolver_fase_2d, extraer_puntos_pupila_circular
                )
                img_mat = cargar_y_normalizar_imagen(img_filepath)
                img_mat, _ = recortar_y_limpiar_interferograma(img_mat, umbral_fondo=0.06)
                fase_wrap, _, _ = demodular_fase_fft2d(img_mat)
                fase_unwrapped = desenvolver_fase_2d(fase_wrap)

                X_val, Y_val, Z_val, _ = extraer_puntos_pupila_circular(fase_unwrapped, img_mat, radio_pct=0.96)
                datos_directos = (X_val, Y_val, Z_val)





        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        self.lbl_estado_icon.setText("Calculando...")
        self.panel_parametros.btn_ejecutar.setEnabled(False)
        self.status_bar.showMessage(f"Iniciando cálculo con motor ({'Fortran' if motor == 1 else 'Python'})...")

        self.worker = ZernikeWorker(modo, eq_str, N, M, diametro, filepath, motor, datos_directos, self)

        self.worker.progreso_actualizado.connect(self._al_progreso_worker)
        self.worker.calculo_finalizado.connect(self._al_finalizar_worker)
        self.worker.calculo_error.connect(self._al_error_worker)
        self.worker.start()

    def _seleccionar_motor_calculo(self, motor: int):
        """Cambia el motor numerico activo (0: Python NumPy, 1: Fortran Nativo)."""
        self.motor_actual = motor
        nombre_motor = "Fortran Nativo (Gram-Schmidt, k=4)" if motor == 1 else "Python (NumPy, k=5, ISO 10110-5)"
        self.status_bar.showMessage(f"Motor de cálculo activo cambiado a: {nombre_motor}", 4000)


    def _al_progreso_worker(self, val: int, msg: str):
        self.progress_bar.setValue(val)
        self.status_bar.showMessage(msg)

    def _al_error_worker(self, error_msg: str):
        self.progress_bar.setVisible(False)
        self.lbl_estado_icon.setText("Error")
        self.status_bar.showMessage("Error en el ajuste. Revisa los datos de entrada.")
        self.panel_parametros._validar_inputs()
        QMessageBox.critical(
            self,
            "Error en el Ajuste de Zernike",
            f"No se pudo completar la simulación:\n\n{error_msg}"
        )

    def _al_finalizar_worker(self, resultados, W_in, X_in, Y_in, X_raw_all, Y_raw_all, mask_all, R_pup):
        self.ultimo_resultado = resultados
        self.ultimas_coordenadas = (X_in, Y_in, W_in)
        self.ultimas_coordenadas_raw = (X_raw_all, Y_raw_all, mask_all, R_pup)

        self.summary_tables.actualizar_datos(resultados, W_in)
        self._actualizar_grafica_ccd(X_raw_all, Y_raw_all, mask_all, R_pup)
        self._actualizar_grafica_3d(X_in, Y_in, W_in, resultados.W_fit)
        self._actualizar_grafica_sintetico()

        self._procesar_exportaciones(resultados, X_in, Y_in, W_in)


        self.progress_bar.setValue(100)
        self.lbl_estado_icon.setText("Completado")
        self.status_bar.showMessage("Ajuste de Zernike finalizado exitosamente. Vistas actualizadas.")
        self.progress_bar.setVisible(False)
        self.panel_parametros.btn_ejecutar.setEnabled(True)

    def _al_cambiar_camara_3d(self, elev: int, azim: int):
        """Actualiza dinámicamente la inclinación y orientación de la cámara 3D."""
        if hasattr(self.canvas_3d.figure, 'axes') and len(self.canvas_3d.figure.axes) > 0:
            ax = self.canvas_3d.figure.axes[0]
            if hasattr(ax, 'view_init'):
                ax.view_init(elev=elev, azim=azim)
                self.canvas_3d.canvas.draw_idle()

    def _al_cambiar_colormap_3d(self, cmap_name: str):
        """Redibuja la superficie 3D al cambiar el colormap."""
        self._redibujar_3d_main()

    def _redibujar_3d_main(self):
        """Metodo de conveniencia para redibujar la vista 3D de la pestaña principal."""
        if self.ultimas_coordenadas is not None and self.ultimo_resultado is not None:
            X_in, Y_in, W_in = self.ultimas_coordenadas
            self._actualizar_grafica_3d(X_in, Y_in, W_in, self.ultimo_resultado.W_fit)


    def _actualizar_grafica_3d(self, X, Y, W_exp, W_fit, cmap_override=None):
        """Renderiza el mapa tridimensional del error residual respetando la orientacion y parametros manuales de control."""
        Z_diff = W_exp - W_fit
        cmap_name = cmap_override if cmap_override is not None else self.control_bar_3d.combo_cmap.currentText()

        elev = self.control_bar_3d.spin_elev.value()
        azim = self.control_bar_3d.spin_azim.value()
        z_scale = self.control_bar_3d.spin_escala_z.value()
        wireframe = self.control_bar_3d.chk_wireframe.isChecked()
        show_grid = self.control_bar_3d.chk_grid.isChecked()
        n_grid = self.control_bar_3d.spin_n_grid.value()
        sigma = self.control_bar_3d.spin_sigma.value()

        try:
            if hasattr(self, 'canvas_3d') and hasattr(self.canvas_3d, 'figure') and self.canvas_3d.figure is not None:
                if len(self.canvas_3d.figure.axes) > 0:
                    ax_prev = self.canvas_3d.figure.axes[0]
                    if hasattr(ax_prev, 'elev') and ax_prev.elev is not None:
                        elev = int(ax_prev.elev)
                        azim = int(ax_prev.azim)
                        self.control_bar_3d.spin_elev.blockSignals(True)
                        self.control_bar_3d.spin_azim.blockSignals(True)
                        self.control_bar_3d.spin_elev.setValue(elev)
                        self.control_bar_3d.spin_azim.setValue(azim)
                        self.control_bar_3d.spin_elev.blockSignals(False)
                        self.control_bar_3d.spin_azim.blockSignals(False)
        except Exception:
            pass

        fig = mapa_fase_3d(
            X, Y, Z_diff,
            title='Error Residual 3D (Z_exp - Z_fit)',
            cmap=cmap_name,
            z_scale=z_scale,
            wireframe=wireframe,
            show_grid=show_grid,
            n_grid=n_grid,
            sigma=sigma
        )

        if hasattr(fig, 'axes') and len(fig.axes) > 0 and hasattr(fig.axes[0], 'view_init'):
            fig.axes[0].view_init(elev=elev, azim=azim)

        self.canvas_3d.set_figure(fig)





    def lanzar_animacion_flujo_zernike(self):
        """
        Muestra EXCLUSIVAMENTE la animación de barra de colores y dependencias recursivas (graficar_flujo_zernike).
        No abre ninguna otra ventana ni representación adicional.
        """
        if self.ultimo_resultado is None:
            QMessageBox.information(
                self,
                "Sin Ajuste Calculado",
                "Primero debes realizar un ajuste con 'Ejecutar Ajuste de Zernike' para generar los datos de la animación."
            )
            return

        if hasattr(self, '_fig_flujo') and self._fig_flujo is not None and plt.fignum_exists(self._fig_flujo.number):
            plt.close(self._fig_flujo)

        plt.ion()
        fig, anim = graficar_flujo_zernike(self.ultimo_resultado, intervalo_ms=180, repetir=False)
        self._fig_flujo = fig
        self.animacion_flotante = anim
        plt.show(block=False)
        self.status_bar.showMessage("Animación de barra de colores recursiva desplegada en ventana flotante independiente.")

    def lanzar_flujo_completo_zernike(self):
        """
        Lanza el flujo completo de ventanas flotantes (Distribución CCD 4 Cuadrantes, Pupila 2D y Animación Recursiva).
        """
        if self.ultimo_resultado is None or not hasattr(self, 'ultimas_coordenadas_raw'):
            QMessageBox.information(
                self,
                "Sin Ajuste Calculado",
                "Primero debes realizar un ajuste con 'Ejecutar Ajuste de Zernike' antes de visualizar el flujo completo."
            )
            return

        plt.close('all')
        self._mostrar_grafica_distribucion_ccd_flotante()
        self._mostrar_grafica_pupila_flotante()
        self.lanzar_animacion_flujo_zernike()
        self.status_bar.showMessage("Flujo completo de ventanas flotantes (CCD, Pupila y Animación Recursiva) desplegado.")



    def _mostrar_animacion_flujo(self):
        """Alias de compatibilidad hacia lanzar_animacion_flujo_zernike."""
        self.lanzar_animacion_flujo_zernike()

    def _actualizar_grafica_sintetico(self):
        """Renderiza el mapa 2D del interferograma sintético en la Pestaña 4."""
        if self.ultimo_resultado is None or not hasattr(self, 'canvas_sintetico'):
            return

        fig = graficar_interferograma_sintetico(
            A_coefs=self.ultimo_resultado.A,
            is_dark=False,  # Siempre claro según requerimiento
            N=256,
            franjas_carrier=12
        )
        self.canvas_sintetico.set_figure(fig)


    def _mostrar_interferograma_sintetico(self):
        """Muestra el interferograma sintético en una ventana flotante independiente."""
        if self.ultimo_resultado is None:
            QMessageBox.information(
                self,
                "Sin Ajuste Disponible",
                "Primero debes realizar un ajuste de Zernike para sintetizar el interferograma óptico."
            )
            return

        from PySide6.QtWidgets import QDialog
        
        fig = graficar_interferograma_sintetico(
            A_coefs=self.ultimo_resultado.A,
            is_dark=False,  # Siempre claro según requerimiento
            N=256,
            franjas_carrier=12
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Interferograma Sintético")
        dialog.resize(700, 600)
        
        layout = QVBoxLayout(dialog)
        canvas = MplCanvasWidget(dialog)
        canvas.set_figure(fig)
        layout.addWidget(canvas)
        
        # Forzar tema claro para la grafica y ventana
        css = obtener_estilo_tema('claro')
        dialog.setStyleSheet(css)

        dialog.show()
        
        # Evitar recoleccion de basura
        if not hasattr(self, '_dialogs_sinteticos'):
            self._dialogs_sinteticos = []
        self._dialogs_sinteticos.append(dialog)
        
        self.status_bar.showMessage("Visualizando el interferograma sintético en ventana flotante.", 3000)

    def _mostrar_espectro_aberraciones_flotante(self):
        """Muestra la gráfica de la Distribución de Aberraciones por Coeficiente de Zernike (21 Colores Golosina) en una ventana flotante independiente."""
        if self.ultimo_resultado is None:
            QMessageBox.information(
                self,
                "Sin Ajuste Disponible",
                "Primero debes realizar un ajuste de Zernike para visualizar el espectro de aberraciones."
            )
            return

        from PySide6.QtWidgets import QDialog, QVBoxLayout
        from gui.canvas import MplCanvasWidget
        from gui.styles import obtener_estilo_tema
        from lib.visualizacion import graficar_espectro_aberraciones

        es_oscuro = (self.tema_actual == 'oscuro')
        fig = graficar_espectro_aberraciones(
            self.ultimo_resultado.A,
            is_dark=es_oscuro,
            title="Distribución de Aberraciones por Coeficiente de Zernike (ISO 10110-5)",
            annotate_values=True
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Distribución de Aberraciones de Zernike (Espectro A1..A21)")
        dialog.resize(850, 480)

        layout = QVBoxLayout(dialog)
        canvas = MplCanvasWidget(dialog)
        canvas.set_figure(fig)
        layout.addWidget(canvas)

        css = obtener_estilo_tema(self.tema_actual)
        dialog.setStyleSheet(css)
        dialog.show()

        if not hasattr(self, '_dialogs_espectro'):
            self._dialogs_espectro = []
        self._dialogs_espectro.append(dialog)

        self.status_bar.showMessage("Visualizando la distribución de aberraciones en ventana flotante.", 3000)

    def _ir_a_pestana_interferograma_sintetico(self):
        """Conmuta directamente a la Pestaña 4 (Interferograma Sintético)."""
        self.tabs.setCurrentIndex(3)


    def _mostrar_grafica_distribucion_ccd_flotante(self):
        """Abre exclusivamente graficar_distribucion_ccd(X_c, Y_c) en una ventana flotante única."""
        if not hasattr(self, 'ultimas_coordenadas_raw') or self.ultimas_coordenadas_raw is None:
            QMessageBox.information(
                self,
                "Sin Ajuste Calculado",
                "Primero debes hacer clic en 'EJECUTAR AJUSTE DE ZERNIKE' para procesar la malla CCD."
            )
            return

        if hasattr(self, '_fig_distribucion') and self._fig_distribucion is not None and plt.fignum_exists(self._fig_distribucion.number):
            plt.close(self._fig_distribucion)

        X_all, Y_all, mask_all, R = self.ultimas_coordenadas_raw
        plt.ion()
        self._fig_distribucion = graficar_distribucion_ccd(X_all, Y_all)
        plt.show(block=False)
        self.status_bar.showMessage("Gráfica de Distribución CCD (4 Cuadrantes) abierta en ventana flotante.")

    def _mostrar_grafica_pupila_flotante(self):
        """Abre la grafica 2D del filtrado por pupila en una ventana flotante dedicada única."""
        if not hasattr(self, 'ultimas_coordenadas_raw') or self.ultimas_coordenadas_raw is None:
            QMessageBox.information(
                self,
                "Sin Ajuste Calculado",
                "Primero debes hacer clic en 'EJECUTAR AJUSTE DE ZERNIKE' para procesar la pupila."
            )
            return

        if hasattr(self, '_fig_pupila') and self._fig_pupila is not None and plt.fignum_exists(self._fig_pupila.number):
            plt.close(self._fig_pupila)

        X_all, Y_all, mask_all, R = self.ultimas_coordenadas_raw
        plt.ion()
        self._fig_pupila = graficar_pupila(X_all, Y_all, mask_all, R)
        plt.show(block=False)
        self.status_bar.showMessage("Gráfica 2D de Pupila Óptica abierta en ventana flotante.")

    def _mostrar_grafica_3d_flotante(self):
        """Abre la grafica tridimensional del error residual en un cuadro flotante modular con controles 3D."""
        if self.ultimo_resultado is None or self.ultimas_coordenadas is None:
            QMessageBox.information(
                self,
                "Sin Ajuste Calculado",
                "Primero debes hacer clic en 'EJECUTAR AJUSTE DE ZERNIKE' para calcular el error residual."
            )
            return

        if hasattr(self, '_dialog_3d') and self._dialog_3d is not None and self._dialog_3d.isVisible():
            self._dialog_3d.close()

        X_in, Y_in, W_in = self.ultimas_coordenadas
        W_fit = self.ultimo_resultado.W_fit
        self._dialog_3d = mostrar_ventana_3d_error_residual(X_in, Y_in, W_in, W_fit, parent=self)
        self.status_bar.showMessage("Gráfico 3D de Error Residual con panel de controles desplegado en ventana flotante.")

    def _mostrar_vista_modo_zemax(self):
        """Abre la ventana interactiva flotante idéntica a Zemax OpticStudio con Quick Fit y matriz de coeficientes."""
        from gui.zemax_view_dialog import ZemaxViewDialog
        if hasattr(self, '_dialog_zemax_view') and self._dialog_zemax_view is not None and self._dialog_zemax_view.isVisible():
            self._dialog_zemax_view.close()

        self._dialog_zemax_view = ZemaxViewDialog(resultado_zernike=self.ultimo_resultado, parent=self)
        self._dialog_zemax_view.show()
        self.status_bar.showMessage("Vista Estilo Zemax OpticStudio (Quick Fit & Coeficientes) desplegada.")

    def _mostrar_visor_polinomios_2d(self):
        """Abre el visor 2D interactivo para explorar de forma individual los 21 Polinomios de Zernike."""
        from gui.zernike_viewer_2d_dialog import ZernikeViewer2DDialog
        if hasattr(self, '_dialog_visor_2d') and self._dialog_visor_2d is not None and self._dialog_visor_2d.isVisible():
            self._dialog_visor_2d.close()

        self._dialog_visor_2d = ZernikeViewer2DDialog(resultado_zernike=self.ultimo_resultado, parent=self)
        self._dialog_visor_2d.show()
        self.status_bar.showMessage("Visor 2D de Polinomios de Zernike desplegado.")

    def _mostrar_visor_polinomios_3d(self):
        """Abre el visor 3D interactivo para explorar de forma individual los 21 Polinomios de Zernike."""
        if hasattr(self, '_dialog_visor_3d') and self._dialog_visor_3d is not None and self._dialog_visor_3d.isVisible():
            self._dialog_visor_3d.close()

        self._dialog_visor_3d = ZernikeViewer3DDialog(resultado_zernike=self.ultimo_resultado, parent=self)
        self._dialog_visor_3d.show()
        self.status_bar.showMessage("Visor 3D de Polinomios de Zernike desplegado.")

    def _comparar_motores_calculo(self):
        """Abre el cuadro de dialogo comparativo entre el motor de Python (NumPy) y Fortran Nativo."""
        if self.ultimas_coordenadas is None:
            QMessageBox.information(
                self,
                "Sin Datos para Comparación",
                "Primero debes hacer clic en 'EJECUTAR AJUSTE DE ZERNIKE' para cargar o calcular las coordenadas."
            )
            return

        if hasattr(self, '_dialog_comparacion') and self._dialog_comparacion is not None and self._dialog_comparacion.isVisible():
            self._dialog_comparacion.close()

        X_in, Y_in, W_in = self.ultimas_coordenadas
        self._dialog_comparacion = EngineComparisonDialog(X_in, Y_in, W_in, parent=self)
        self._dialog_comparacion.show()
        self.status_bar.showMessage("Comparador de Motores (Python vs. Fortran) desplegado.")

    def _al_seleccionar_imagen_interferograma(self, filepath: str):
        """Muestra inmediatamente la previsualización del interferograma en Tab 2 (Malla CCD & Pupila)."""
        if not filepath or not os.path.exists(filepath):
            return

        from lib.interferometria import cargar_y_normalizar_imagen, recortar_y_limpiar_interferograma
        from lib.visualizacion import graficar_interferograma_original

        try:
            img_mat = cargar_y_normalizar_imagen(filepath)
            img_limpia, _ = recortar_y_limpiar_interferograma(img_mat, umbral_fondo=0.06)
            is_dark = (self.tema_actual == 'oscuro')
            fig = graficar_interferograma_original(img_limpia, is_dark=is_dark)

            self.canvas_ccd.set_figure(fig)
            self.tabs.setCurrentIndex(1)  # Pestaña Malla CCD & Pupila
            self.status_bar.showMessage(f"Previsualización inmediata cargada: {os.path.basename(filepath)}", 5000)
        except Exception as e:
            self.status_bar.showMessage(f"No se pudo previsualizar la imagen: {str(e)}", 4000)

    def _al_cambiar_modo_entrada(self, index: int):
        """Limpia datos acumulados en memoria al conmutar entre modos de entrada."""
        self.datos_interferograma_cargados = None
        if index != 3:
            self.panel_parametros.input_img_path.clear()
        self.status_bar.showMessage("Modo de entrada cambiado. Datos anteriores de interferograma reseteados.", 3000)


    def _lanzar_procesador_interferogramas(self):

        """Abre la ventana interactiva de demodulación de interferogramas en imagen."""
        if hasattr(self, '_dialog_interferograma') and self._dialog_interferograma is not None and self._dialog_interferograma.isVisible():
            self._dialog_interferograma.close()

        self._dialog_interferograma = InterferogramProcessorDialog(parent=self)
        self._dialog_interferograma.puntos_extraidos_signal.connect(self._procesar_puntos_interferograma_importados)
        self._dialog_interferograma.show()
        self.status_bar.showMessage("Procesador de Interferogramas (Takeda 2D / Esqueleto) desplegado.")

    def _procesar_puntos_interferograma_importados(self, X_in, Y_in, W_in):
        """Recibe los puntos (X,Y,Z) extraídos del procesador y los prepara para la ejecución desde la ventana principal."""
        self.datos_interferograma_cargados = (X_in, Y_in, W_in)
        self.panel_parametros.combo_modo.setCurrentIndex(3)  # Imagen de Interferograma
        self.status_bar.showMessage(
            f"Se cargaron {len(X_in)} puntos del interferograma. Haz clic en 'EJECUTAR AJUSTE DE ZERNIKE (Ctrl+E)' para iniciar.",
            6000
        )
        QMessageBox.information(
            self,
            "Puntos Listos",
            f"Se han cargado {len(X_in)} puntos en el panel principal.\n\n"
            "Haz clic en el botón 'EJECUTAR AJUSTE DE ZERNIKE (Ctrl+E)' en la ventana principal para realizar la simulación."
        )

    def _actualizar_grafica_ccd(self, X_all, Y_all, mascara, R):
        """Usa graficar_pupila() o renderiza la imagen importada de interferograma en la pestaña CCD & Pupila."""
        modo = self.panel_parametros.combo_modo.currentIndex()
        img_filepath = self.panel_parametros.input_img_path.text().strip()

        if modo == 3 and img_filepath and os.path.exists(img_filepath):
            from lib.interferometria import cargar_y_normalizar_imagen, recortar_y_limpiar_interferograma
            from lib.visualizacion import graficar_interferograma_original
            is_dark = (self.tema_actual == 'oscuro')
            img_mat = cargar_y_normalizar_imagen(img_filepath)
            img_mat, _ = recortar_y_limpiar_interferograma(img_mat, umbral_fondo=0.06)
            fig = graficar_interferograma_original(img_mat, is_dark=is_dark)
        else:
            fig = graficar_pupila(X_all, Y_all, mascara, R)

        self.canvas_ccd.set_figure(fig)




    def _procesar_exportaciones(self, resultados, X, Y, W):
        """Ejecuta las exportaciones opcionales marcadas por el usuario."""
        A = resultados.A
        error = W - resultados.W_fit

        if self.panel_parametros.chk_exp_csv.isChecked():
            exportar_resultados_csv(X, Y, W, resultados.W_fit, error, filepath='output/zernike_resultados.csv')
        if self.panel_parametros.chk_exp_zemax.isChecked():
            exportar_zemax(A, filepath='output/zemax_zernike.zrn')
        if self.panel_parametros.chk_exp_codev.isChecked():
            exportar_codev(A, filepath='output/codev_zernike.dat')

    def _exportar_csv_manual(self):
        """Dialogo de exportacion manual a CSV de resultados."""
        if self.ultimo_resultado is None or self.ultimas_coordenadas is None:
            QMessageBox.warning(self, "Sin Ajuste", "Primero debes ejecutar un ajuste de Zernike.")
            return
        filepath, _ = QFileDialog.getSaveFileName(self, "Exportar Resultados a CSV", "output/zernike_resultados.csv", "Archivos CSV (*.csv)")
        if filepath:
            X_in, Y_in, W_in = self.ultimas_coordenadas
            error = W_in - self.ultimo_resultado.W_fit
            from lib.io import exportar_resultados_csv
            exportar_resultados_csv(X_in, Y_in, W_in, self.ultimo_resultado.W_fit, error, filepath=filepath)
            QMessageBox.information(self, "Exportación Exitosa", f"Archivo CSV de resultados guardado en:\n{filepath}")


    def _exportar_zemax_manual(self):
        """Dialogo de exportacion manual a Zemax."""
        if self.ultimo_resultado is None:
            QMessageBox.warning(self, "Sin Ajuste", "Primero debes ejecutar un ajuste de Zernike.")
            return
        filepath, _ = QFileDialog.getSaveFileName(self, "Exportar Coeficientes a Zemax", "output/zemax_zernike.zrn", "Zemax Zernike (*.zrn *.txt)")
        if filepath:
            exportar_zemax(self.ultimo_resultado.A, filepath=filepath)
            QMessageBox.information(self, "Exportación Exitosa", f"Archivo Zemax guardado en:\n{filepath}")

    def _exportar_codev_manual(self):
        """Dialogo de exportacion manual a CODE V."""
        if self.ultimo_resultado is None:
            QMessageBox.warning(self, "Sin Ajuste", "Primero debes ejecutar un ajuste de Zernike.")
            return
        filepath, _ = QFileDialog.getSaveFileName(self, "Exportar Coeficientes a CODE V", "output/codev_zernike.dat", "CODE V Data (*.dat *.txt)")
        if filepath:
            exportar_codev(self.ultimo_resultado.A, filepath=filepath)
            QMessageBox.information(self, "Exportación Exitosa", f"Archivo CODE V guardado en:\n{filepath}")

    def _generar_reporte_html_manual(self):
        """Diálogo de exportación manual para el Reporte Metrológico de Calidad Óptica en HTML."""
        if self.ultimo_resultado is None:
            QMessageBox.warning(self, "Sin Ajuste", "Primero debes ejecutar un ajuste de Zernike para generar el reporte metrológico.")
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Reporte Metrológico (HTML)",
            "output/reporte_metrologico_zernike.html",
            "Archivos HTML (*.html)"
        )
        if filepath:
            from lib.reportes import exportar_reporte_html
            ok = exportar_reporte_html(self.ultimo_resultado, filepath, titulo="Reporte Metrológico de Calidad Óptica")
            if ok:
                QMessageBox.information(self, "Reporte HTML Generado", f"Reporte metrológico HTML generado exitosamente en:\n{filepath}")

    def _seleccionar_archivo_csv(self):
        """Delega la seleccion del archivo CSV al panel de parametros."""
        self.panel_parametros._seleccionar_archivo_csv()

    def _restablecer_defaults(self):
        """Restablece los campos del panel de parametros."""
        self.panel_parametros.restablecer_defaults()
        self.status_bar.showMessage("Parámetros restablecidos a la configuración inicial por defecto.")

    def _toggle_tema(self):
        """Alterna el tema visual entre Claro y Oscuro."""
        nuevo_tema = "oscuro" if self.tema_actual == "claro" else "claro"
        self._aplicar_estilo_tema(nuevo_tema)
        self.status_bar.showMessage(f"Tema cambiado a: {nuevo_tema.upper()}")
