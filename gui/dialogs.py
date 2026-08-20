from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QMessageBox
from PySide6.QtCore import Qt

from gui.error_residual_dialog import ErrorResidual3DDialog, mostrar_ventana_3d_error_residual, mostrar_ventana_2d_error_residual
from gui.styles import obtener_paleta_tema

URL_PORTAFOLIO_DESARROLLADOR = "https://marioramirez-dev.vercel.app/"


def mostrar_manual_usuario(parent=None):
    """Despliega la ventana modal con el manual de usuario y referencia matemática con tema dinámico."""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Manual de Usuario y Referencia Matemática — Zernike")
    dialog.resize(800, 600)

    if parent is not None and hasattr(parent, 'styleSheet'):
        dialog.setStyleSheet(parent.styleSheet())
    
    tema = getattr(parent, 'tema_actual', 'claro')
    paleta = obtener_paleta_tema(tema)

    layout = QVBoxLayout(dialog)
    text_edit = QTextBrowser()
    text_edit.setReadOnly(True)
    text_edit.setOpenExternalLinks(True)
    text_edit.setHtml(f"""
        <div style='color: {paleta["body_color"]}; font-family: sans-serif; font-size: 13px;'>
            <h2 style='color: {paleta["h2_color"]};'>Zernike — Polinomios Ortogonales de Superficies Ópticas</h2>
            <p>Esta aplicación permite ajustar y descomponer superficies ópticas y frentes de onda utilizando la base 
            ortogonal de <b>Polinomios de Zernike</b> bajo la norma internacional <b>ISO 10110-5 / ANSI Z80.28</b>, 
            implementando el algoritmo de Gram-Schmidt discreto con verificación cruzada (Malacara, 1990 — <i>Optical Shop Testing</i>).</p>
            
            <hr style='border: none; border-top: 1px solid {paleta["hr_color"]};'>

            <h3 style='color: {paleta["h3_color"]};'>1. Flujo Matemático del Algoritmo</h3>
            <p>El sistema realiza la transformación de bases ortogonales de manera directa:</p>
            <pre style='background-color: {paleta["code_bg"]}; color: {paleta["fg"]}; padding: 10px; border: 1px solid {paleta["border"]}; border-radius: 6px;'>
Datos (X, Y, W) ──▶ normalizar_vector() / filtrar_pupila()
       │
       ▼
    Matriz U ──▶ evaluar_polinomios() [Base de Zernike evaluada en (x,y)]
       │
       ▼ Gram-Schmidt Discreto
    V, D, F  ──▶ construir_base_ortogonal() [Base V_r ortogonalizada]
       │
       ▼
   Vectores B, C, A ──▶ calcular_A() [Coeficientes ISO 10110-5 (A_1 ... A_21)]
       │
       ▼
   W_fit ──▶ Superficie Reconstruida = Σ (A_r * U_r) = Σ (B_r * V_r)
            </pre>

            <h3 style='color: {paleta["h3_color"]};'>2. Modos de Entrada de Datos Integrados</h3>
            <ul>
                <li><b>1. CCD Sensor (Malla NxM):</b> Simula una cuadrícula rectangular simétrica de píxeles centrada al origen óptico (0,0) recortada por una pupila circular. Evalúa expresiones analíticas mediante parser AST seguro (soporta <code>sin, cos, tan, sqrt, exp, log, pi, e</code>).</li>
                <li><b>2. Archivo CSV Experimental:</b> Importa datos reales conteniendo columnas <code>X, Y, Z</code> o <code>X, Y, W</code>.</li>
                <li><b>3. Círculo Unitario Sintético:</b> Muestreo de N puntos dentro de la pupila circular de radio unitario &rho; &le; 1.0.</li>
                <li><b>4. Imagen de Interferograma (Demodulación 2D FFT):</b> Carga imágenes de franjas fotográficas reales para extraer fase continua mediante la Transformada de Fourier 2D de Takeda et al. (1982) y desenvolvimiento de fase (*phase unwrapping*).</li>
            </ul>

            <h3 style='color: {paleta["h3_color"]};'>3. Motores de Cómputo (Dual Engine)</h3>
            <ul>
                <li><b>Python (NumPy / SVD-QR):</b> Motor de cómputo en Python de alta precisión y estabilidad numérica.</li>
                <li><b>Fortran Nativo (Gram-Schmidt CFFI):</b> Motor binario acelerado compilado en Fortran 90/95 para alto rendimiento en matrices masivas.</li>
            </ul>

            <h3 style='color: {paleta["h3_color"]};'>4. Descomposición de Aberraciones Ópticas Primarias (Seidel)</h3>
            <ul>
                <li><b>Pistón (A1):</b> Desplazamiento medio o fase constante.</li>
                <li><b>Tilt X / Tilt Y (A2, A3):</b> Inclinación o efecto prisma en los ejes X e Y.</li>
                <li><b>Desenfoque / Defocus (A5):</b> Error de curvatura o potencia focal esférica.</li>
                <li><b>Astigmatismo a 0° / 45° (A4, A6):</b> Deformación cilíndrica a 0° y 45°.</li>
                <li><b>Coma X / Coma Y (A7, A8):</b> Asimetría transversal del frente de onda (efecto cometa).</li>
                <li><b>Aberración Esférica de 3er Orden (A13):</b> Defecto simétrico radial de alto orden.</li>
            </ul>

            <h3 style='color: {paleta["h3_color"]};'>5. Herramientas Especializadas de Análisis</h3>
            <ul>
                <li><b>Vista Estilo Zemax OpticStudio (Ctrl+Shift+X):</b> Réplica de la interfaz de MetroPro / Zemax con tabla de coeficientes por orden radial, métricas *Quick Fit* (P-V, RMS, Power, Irregularity) y edición inversa interactiva.</li>
                <li><b>Visualizador Polinomios 2D/3D:</b> Inspección individual de cualquiera de los 21 polinomios de la base en 3D o en franjas de interferencia monocromáticas 2D.</li>
                <li><b>Sintetizador de Interferogramas 2D:</b> Reconstrucción óptica directa con portadora espacial e iluminación gaussiana.</li>
                <li><b>Comparador Numérico Cruzado:</b> Prueba cruzada entre Python y Fortran reportando diferencias absolutas y aceleración de tiempo.</li>
            </ul>

            <h3 style='color: {paleta["h3_color"]};'>6. Formatos Estándar de Exportación</h3>
            <ul>
                <li><b>Zemax OpticStudio (.zrn):</b> Archivo estándar de texto con radio de pupila, longitud de onda y coeficientes A_1 ... A_21. Soporta selección de ruta mediante explorador interactivo.</li>
                <li><b>CODE V (.dat):</b> Archivo de datos de superficie para CODE V con cabeceras <code>NRAD</code> y <code>ZFR</code>. Soporta selección de ruta mediante explorador interactivo.</li>
                <li><b>CSV (.csv):</b> Archivo plano con coordenadas X, Y, Z real, Z ajustado y error residual.</li>
            </ul>

            <h3 style='color: {paleta["h3_color"]};'>7. Atajos de Teclado Útiles</h3>
            <ul>
                <li><code style='color: {paleta["code_color"]};'>Ctrl + E</code>: Ejecutar Ajuste de Zernike.</li>
                <li><code style='color: {paleta["code_color"]};'>Ctrl + O</code>: Abrir / Cargar archivo CSV.</li>
                <li><code style='color: {paleta["code_color"]};'>Ctrl + Shift + X</code>: Abrir Vista Estilo Zemax OpticStudio.</li>
                <li><code style='color: {paleta["code_color"]};'>Ctrl + F</code>: Ver Animación / Flujo Completo de Zernike.</li>
                <li><code style='color: {paleta["code_color"]};'>Ctrl + S</code>: Exportar a Zemax OpticStudio (.zrn).</li>
                <li><code style='color: {paleta["code_color"]};'>Ctrl + T</code>: Alternar Tema Claro / Oscuro.</li>
                <li><code style='color: {paleta["code_color"]};'>Ctrl + R</code>: Restablecer parámetros iniciales.</li>
                <li><code style='color: {paleta["code_color"]};'>F1</code>: Desplegar este manual de usuario.</li>
            </ul>
        </div>
    """)
    layout.addWidget(text_edit)

    btn_close = QPushButton("Cerrar Manual")
    btn_close.clicked.connect(dialog.accept)
    layout.addWidget(btn_close)

    dialog.exec()


def mostrar_acerca_de(parent=None, url_portafolio: str = None):
    """Despliega el cuadro acerca de la aplicacion Zernike con enlace al portafolio del desarrollador."""
    if url_portafolio is None:
        url_portafolio = URL_PORTAFOLIO_DESARROLLADOR

    dialog = QDialog(parent)
    dialog.setWindowTitle("Acerca de Zernike")
    dialog.setFixedSize(480, 260)

    if parent is not None and hasattr(parent, 'styleSheet'):
        dialog.setStyleSheet(parent.styleSheet())

    tema = getattr(parent, 'tema_actual', 'claro')
    paleta = obtener_paleta_tema(tema)

    layout = QVBoxLayout(dialog)
    text_edit = QTextBrowser()
    text_edit.setReadOnly(True)
    text_edit.setOpenExternalLinks(True)
    text_edit.setHtml(f"""
        <div style='color: {paleta["body_color"]}; font-family: sans-serif; font-size: 13px; text-align: center; padding: 8px;'>
            <h2 style='color: {paleta["h2_color"]}; margin-bottom: 6px;'>Zernike v1.1.0</h2>
            <p>Ajuste y caracterización metrológica de superficies ópticas mediante <b>Polinomios Ortogonales de Zernike (ISO 10110-5 / ANSI Z80.28)</b>.</p>
            <p style='margin-top: 6px;'>Algoritmo de Gram-Schmidt discreto (Malacara, 1990 — <i>Optical Shop Testing</i>).</p>
            <hr style='border: none; border-top: 1px solid {paleta["hr_color"]}; margin: 12px 0;'>
            <p style='font-size: 13px; font-weight: bold;'>
                Desarrollado por: <a href='{url_portafolio}' style='color: {paleta["accent_secondary"]}; text-decoration: underline;'>Portafolio / Contacto del Desarrollador</a>
            </p>
        </div>
    """)
    layout.addWidget(text_edit)

    btn_aceptar = QPushButton("Aceptar")
    btn_aceptar.clicked.connect(dialog.accept)
    layout.addWidget(btn_aceptar)

    dialog.exec()
