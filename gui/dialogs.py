from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt

from gui.canvas import MplCanvasWidget
from gui.components.control_bar_3d import ControlBar3D
from lib.visualizacion import mapa_fase_3d


class ErrorResidual3DDialog(QDialog):
    """
    Ventana flotante modular para visualizar el Error Residual 3D
    reutilizando ControlBar3D y MplCanvasWidget.
    """
    def __init__(self, X, Y, W_exp, W_fit, parent=None):
        super().__init__(parent)
        self.X = X
        self.Y = Y
        self.W_exp = W_exp
        self.W_fit = W_fit
        self.Z_diff = W_exp - W_fit

        self.setWindowTitle("Mapa de Error Residual 3D (Z_exp - Z_fit)")
        self.resize(900, 680)

        if parent is not None and hasattr(parent, 'styleSheet'):
            self.setStyleSheet(parent.styleSheet())

        self._construir_ui()
        self._actualizar_grafico_3d()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # 1. Reutilizar ControlBar3D
        self.control_bar = ControlBar3D(self)
        self.control_bar.cambio_camara.connect(self._al_cambiar_camara)
        self.control_bar.cambio_colormap.connect(self._al_cambiar_colormap)
        layout.addWidget(self.control_bar)

        # 2. Reutilizar MplCanvasWidget
        self.canvas = MplCanvasWidget(self)
        layout.addWidget(self.canvas)


    def _actualizar_grafico_3d(self, cmap_override=None):
        cmap_name = cmap_override if cmap_override is not None else self.control_bar.combo_cmap.currentText()

        elev = self.control_bar.spin_elev.value()
        azim = self.control_bar.spin_azim.value()
        try:
            if hasattr(self, 'canvas') and hasattr(self.canvas, 'figure') and self.canvas.figure is not None:
                if len(self.canvas.figure.axes) > 0:
                    ax_prev = self.canvas.figure.axes[0]
                    if hasattr(ax_prev, 'elev') and ax_prev.elev is not None:
                        elev = int(ax_prev.elev)
                        azim = int(ax_prev.azim)
                        self.control_bar.spin_elev.blockSignals(True)
                        self.control_bar.spin_azim.blockSignals(True)
                        self.control_bar.spin_elev.setValue(elev)
                        self.control_bar.spin_azim.setValue(azim)
                        self.control_bar.spin_elev.blockSignals(False)
                        self.control_bar.spin_azim.blockSignals(False)
        except Exception:
            pass

        fig = mapa_fase_3d(self.X, self.Y, self.Z_diff, title='Error Residual 3D (Z_exp - Z_fit)', cmap=cmap_name)
        if hasattr(fig, 'axes') and len(fig.axes) > 0 and hasattr(fig.axes[0], 'view_init'):
            fig.axes[0].view_init(elev=elev, azim=azim)

        self.canvas.set_figure(fig)



    def _al_cambiar_camara(self, elev: int, azim: int):
        if hasattr(self.canvas.figure, 'axes') and len(self.canvas.figure.axes) > 0:
            ax = self.canvas.figure.axes[0]
            if hasattr(ax, 'view_init'):
                ax.view_init(elev=elev, azim=azim)
                self.canvas.canvas.draw_idle()

    def _al_cambiar_colormap(self, cmap_name: str):
        self._actualizar_grafico_3d(cmap_override=cmap_name)


def mostrar_ventana_3d_error_residual(X, Y, W_exp, W_fit, parent=None):
    """Instancia y muestra la ventana flotante no modal del Error Residual 3D con controles."""
    dialog = ErrorResidual3DDialog(X, Y, W_exp, W_fit, parent=parent)
    dialog.setWindowModality(Qt.NonModal)
    dialog.show()
    return dialog


def mostrar_manual_usuario(parent=None):
    """Despliega la ventana modal con el manual de usuario y referencia matematica con tema dinamico."""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Manual de Usuario y Referencia Matemática — Zernike")
    dialog.resize(760, 560)

    if parent is not None and hasattr(parent, 'styleSheet'):
        dialog.setStyleSheet(parent.styleSheet())
    
    es_oscuro = getattr(parent, 'tema_actual', 'claro') == 'oscuro'

    # Paleta de colores dinamica segun el tema
    if es_oscuro:
        h2_color = "#88C0D0"      # Nord8 Ice Blue
        h3_color = "#81A1C1"      # Nord9 Glacier Blue
        pre_bg = "#2E3440"        # Nord0 Dark Background
        pre_border = "#4C566A"    # Nord3 Border
        pre_color = "#ECEFF4"     # Nord6 Text
        code_color = "#88C0D0"   # Nord8
        hr_color = "#4C566A"
        body_color = "#D8DEE9"    # Nord4
    else:
        h2_color = "#1E3A8A"
        h3_color = "#1E40AF"
        pre_bg = "#F1F5F9"
        pre_border = "#CBD5E1"
        pre_color = "#0F172A"
        code_color = "#1E3A8A"
        hr_color = "#CBD5E1"
        body_color = "#0F172A"

    layout = QVBoxLayout(dialog)
    text_edit = QTextEdit()
    text_edit.setReadOnly(True)
    text_edit.setHtml(f"""
        <div style='color: {body_color}; font-family: sans-serif; font-size: 13px;'>
            <h2 style='color: {h2_color};'>Zernike — Polinomios Ortogonales de Superficies Ópticas</h2>
            <p>Esta aplicación permite ajustar y descomponer superficies ópticas y frentes de onda utilizando la base 
            ortogonal de <b>Polinomios de Zernike</b> bajo la norma internacional <b>ISO 10110-5 / ANSI Z80.28</b>, 
            implementando el algoritmo de Gram-Schmidt discreto con verificación cruzada (Malacara, 1990 — <i>Optical Shop Testing</i>).</p>
            
            <hr style='border: none; border-top: 1px solid {hr_color};'>

            <h3 style='color: {h3_color};'>1. Flujo Matemático del Algoritmo</h3>
            <p>El sistema realiza la siguiente transformación de bases de manera strictly ortogonal:</p>
            <pre style='background-color: {pre_bg}; color: {pre_color}; padding: 10px; border: 1px solid {pre_border}; border-radius: 6px;'>
Datos (X, Y, W) ──▶ normalizar_vector() / filtrar_pupila()
       │
       ▼
    Matriz U ──▶ evaluar_polinomios() [Base de Zernike evaluada]
       │
       ▼ Gram-Schmidt
    V, D, F  ──▶ construir_base_ortogonal() [Base ortogonalizada]
       │
       ▼
   Vectores B, C, A ──▶ calcular_A() [Coeficientes ISO 10110-5]
       │
       ▼
   W_fit ──▶ Superficie Reconstruida = Σ (A_r * U_r) = Σ (B_r * V_r)
            </pre>

            <h3 style='color: {h3_color};'>2. Modos de Simulación Disponibles</h3>
            <ul>
                <li><b>1. CCD Sensor (Malla NxM):</b> Simula una cuadrícula rectangular simétrica de píxeles centrada al origen óptico (0,0) y recortada por una pupila circular de diámetro configurable. Evalúa ecuaciones polinómicas o trigonométricas (ej. <code style='color: {code_color};'>sin(x) + cos(y)</code>).</li>
                <li><b>2. Archivo CSV Experimental:</b> Importa datos reales de interferogramas o profilometría conteniendo las columnas <code style='color: {code_color};'>X, Y, Z</code>.</li>
                <li><b>3. Círculo Unitario Sintético:</b> Muestreo uniforme de N=100 puntos dentro del círculo de radio R=1.</li>
            </ul>

            <h3 style='color: {h3_color};'>3. Descomposición de Aberraciones Ópticas Primarias (Seidel)</h3>
            <ul>
                <li><b>Pistón (A1):</b> Desplazamiento medio o fase constante.</li>
                <li><b>Tilt X / Tilt Y (A2, A3):</b> Inclinación o efecto prisma en los ejes X e Y.</li>
                <li><b>Desenfoque / Defocus (A5):</b> Error de curvatura o potencia focal esférica.</li>
                <li><b>Astigmatismo (A4, A6):</b> Deformación cilíndrica a 45° y 0°.</li>
                <li><b>Coma X / Coma Y (A8, A9):</b> Asimetría transversal del frente de onda (efecto cometa).</li>
                <li><b>Aberración Esférica de 3er Orden (A13):</b> Defecto simétrico radial de alto orden.</li>
            </ul>

            <h3 style='color: {h3_color};'>4. Formatos Estándar de Exportación</h3>
            <ul>
                <li><b>Zemax OpticStudio (.zrn):</b> Archivo de texto estándar formateado con radio de pupila, longitud de onda y coeficientes $A_1 \\dots A_{21}$.</li>
                <li><b>CODE V (.dat):</b> Archivo de datos de superficie para CODE V con cabeceras <code style='color: {code_color};'>NRAD</code> y <code style='color: {code_color};'>ZFR</code>.</li>
                <li><b>CSV (.csv):</b> Archivo plano con coordenadas X, Y, Z real, Z ajustado y error residual.</li>
            </ul>

            <h3 style='color: {h3_color};'>5. Atajos de Teclado Útiles</h3>
            <ul>
                <li><code style='color: {code_color};'>Ctrl + E</code>: Ejecutar Ajuste de Zernike.</li>
                <li><code style='color: {code_color};'>Ctrl + O</code>: Abrir / Cargar archivo CSV.</li>
                <li><code style='color: {code_color};'>Ctrl + F</code>: Ver Animación de Polinomios de Zernike.</li>
                <li><code style='color: {code_color};'>Ctrl + R</code>: Restablecer parámetros iniciales.</li>
                <li><code style='color: {code_color};'>Ctrl + S</code>: Exportar a Zemax OpticStudio.</li>
                <li><code style='color: {code_color};'>Ctrl + T</code>: Alternar Tema Claro / Oscuro.</li>
                <li><code style='color: {code_color};'>F1</code>: Desplegar este manual de usuario.</li>
            </ul>
        </div>
    """)
    layout.addWidget(text_edit)

    btn_close = QPushButton("Cerrar Manual")
    btn_close.clicked.connect(dialog.accept)
    layout.addWidget(btn_close)

    dialog.exec()


def mostrar_acerca_de(parent=None):
    """Despliega el cuadro acerca de la aplicacion Zernike con soporte del tema actual."""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("Acerca de Zernike")
    if parent is not None and hasattr(parent, 'styleSheet'):
        msg_box.setStyleSheet(parent.styleSheet())
        
    es_oscuro = getattr(parent, 'tema_actual', 'claro') == 'oscuro'
    h3_color = "#88C0D0" if es_oscuro else "#1E3A8A"

    msg_box.setText(
        f"<h3 style='color: {h3_color};'>Zernike v1.0</h3>"
        "<p>Librería y software para ajuste y caracterización de superficies ópticas "
        "mediante <b>Polinomios Ortogonales de Zernike (ISO 10110-5 / ANSI Z80.28)</b>.</p>"
        "<p>Implementación del algoritmo de Gram-Schmidt discreto (Malacara, 1990).</p>"
        "<p><b>Desarrollado con PySide6 & Matplotlib.</b></p>"
    )
    msg_box.exec()

