# Manual Técnico y Guía de Usuario: Interfaz Gráfica (GUI) del Proyecto Zernike

Este documento proporciona la especificación completa, flujo de operación y manual de usuario para la interfaz gráfica de escritorio desarrollada en **PySide6 (Qt6 para Python)**.

---

## 1. Arquitectura y Visión General

La interfaz gráfica del sistema está estructurada bajo el patrón de diseño **Módulo-Vista-Controlador (MVC)** desacoplado, separando estrictamente la presentación gráfica de los motores numéricos de cálculo (`lib/zernike.py` y `lib/fortran_runner.py`).

La ventana principal (`ZernikeZemaxMainWindow`) implementa una distribución tripartita:
1. **Barra de Menú Superior (`AppMenuBar`)**: Acceso estructurado a herramientas de E/S, utilidades ópticas y control de la interfaz.
2. **Panel Lateral de Entrada de Parámetros (`ParameterInputPanel`)**: Panel de control interactivo para configurar modos de datos, ecuaciones y motores.
3. **Área Central Multipestaña (`QTabWidget`)**: Espacio de trabajo principal que actualiza de forma automática y simultánea cuatro vistas de análisis.

---

## 2. Barra de Menú Superior (`AppMenuBar`)

La barra de menú superior organiza las operaciones del sistema en cinco categorías:

### 2.1. Menú Archivo
* **Cargar Archivo CSV...**: Abre un selector de archivos de diálogo para importar un archivo de coordenadas experimentales `.csv` con encabezados `X, Y, Z`.
* **Exportar Resultados a CSV...**: Guarda las coordenadas normalizadas, la superficie real $Z_{\text{exp}}$, la superficie ajustada $Z_{\text{fit}}$ y el error residual en un archivo `.csv` dentro de la carpeta `output/`.
* **Exportar a Zemax OpticStudio (.zrn)...**: Genera un archivo de superficie de Zernike con formato industrial estándar compatible con **Zemax OpticStudio**, especificando el radio de pupila y la longitud de onda de referencia.
* **Exportar a CODE V (.dat)...**: Exporta el vector de coeficientes de aberración $A_j$ en el formato de superficie equivalente para **CODE V**.
* **Salir (Ctrl+Q)**: Finaliza la aplicación de forma segura.

### 2.2. Menú Herramientas
* **Abrir Procesador de Imágenes de Interferograma (Takeda FFT)**: Abre el diálogo especializado para la demodulación 2D de franjas fotográficas reales.
* **Gestor de Presets e Historial de Ecuaciones...**: Despliega el administrador para seleccionar, guardar y consultar ecuaciones de prueba e historial reciente.
* **Visualizador de Polinomios de Zernike (3D)...**: Abre una ventana interactiva para inspeccionar la forma tridimensional pura de cualquiera de los 21 polinomios de la base.
* **Sintetizar Interferograma Óptico desde Zernike**: Genera la reconstrucción óptica 2D del patrón de interferencia a partir del ajuste obtenido.
* **Comparar Motor Python (NumPy) vs. Fortran Nativo...**: Ejecuta una prueba cruzada simultánea en ambos motores y despliega una tabla comparativa de precisión y tiempos.

### 2.3. Menú Ver
* **Cambiar Tema (Oscuro / Claro)**: Alterna dinámicamente la paleta de colores de la interfaz (estilo Nord Dark o estilo Zemax Light) e iguala los fondos de todas las gráficas de Matplotlib.
* **Ver Mapa de Error Residual 3D**: Abre el diálogo flotante no modal del mapa de error residual para análisis independiente.
* **Ver Interferograma Sintético (Ctrl+I)**: Enfoca directamente la Pestaña 4 del área central.

### 2.4. Menú Motor Numérico
Permite conmutar el motor computacional activo para la ejecución:
* **Python (NumPy / SVD-QR)**: Motor estándar de alta precisión implementado en Python.
* **Fortran Nativo (Gram-Schmidt CFFI)**: Motor binario acelerado compilado en Fortran.

### 2.5. Menú Ayuda
* **Manual de Usuario y Referencia Matemática**: Muestra la ventana modal con la teoría metrológica y el flujo algorítmico.
* **Acerca de Zernike Metrology**: Información de versión, estándares ISO 10110-5 y créditos.

---

## 3. Panel Lateral de Entrada de Parámetros (`ParameterInputPanel`)

El panel de control izquierdo administra la ingesta de datos y los parámetros de simulación:

### 3.1. Selector de Modo de Entrada de Datos
El menú desplegable `combo_modo` permite conmutar entre cuatro modos de operación:
1. **Modo 0: 1. Malla CCD Sensor**:
   - Genera una cuadrícula cartesiana regular $N \times M$ que representa los píxeles de un sensor CCD.
   - **Campo Ecuación $Z(x,y)$**: Permite ingresar expresiones analíticas evaluadas de forma segura mediante un parser AST (ej. `3*x*y + 2*x`, `sin(x) + cos(y)`, `x^2 + y^2`).
   - **Presets Rápidos**: Cuatro botones de acceso inmediato a aberraciones conocidas.
   - **Filas ($N$) y Columnas ($M$)**: Dimensiones de la matriz del sensor (mínimo 5).
   - **Diámetro Pupila (px)**: Diámetro en píxeles de la apertura circular inscrita.
   - **Etiqueta Informativa Dinámica**: Muestra en tiempo real el cálculo geométrico de la matriz:
     $$\text{Píxeles Totales} = N \times M, \quad \text{Píxeles Útiles en Pupila} \approx \frac{\pi}{4} (N \times M)$$
2. **Modo 1: 2. Archivo de Entrada CSV**:
   - Muestra el campo de texto y el botón "Examinar..." para seleccionar archivos `.csv` externos.
3. **Modo 2: 2. Círculo Unitario Sintético**:
   - Muestra la entrada para especificar la cantidad exacta de puntos aleatorios $N$ a distribuir dentro de la pupila circular unitaria $\rho \le 1.0$.
4. **Modo 3: 2. Imagen de Interferograma**:
   - Muestra el selector de imágenes (`*.png`, `*.jpg`, `*.bmp`) y el botón para abrir el Procesador Takeda FFT.

### 3.2. Botón Principal de Ejecución
* **Ejecutar Ajuste de Zernike**: Inicia la orquestación asíncrona en un hilo secundario `ZernikeWorker` (QThread), evitando el congelamiento de la GUI.

---

## 4. Área Central Multipestaña (`QTabWidget`)

Al finalizar el cálculo, la interfaz actualiza sincrónicamente sus cuatro pestañas de trabajo:

### 4.1. Pestaña 1: Resumen & Aberraciones (`SummaryTablesWidget`)
Despliega tres tablas informativas de alta precisión con botones para copiar los datos al portapapeles en formato TSV/CSV:

#### Tabla 1: Coeficientes de Zernike (Norma ISO 10110-5 / ANSI Z80.28)
Presenta la lista de los 21 términos de la base polinomial ortogonal ($k=5$):
* **Índice ($r$)**: Posición secuencial del término ($1 \dots 21$).
* **Grado Radial ($n$)**: Grado del polinomio radial.
* **Frecuencia Azimutal ($m$)**: Frecuencia angular.
* **Descripción Óptica**: Denominación estándar (Pistón, Tilt, Desenfoque, Astigmatismo, Coma, Aberración Esférica, Trefoil, Tetrafoil, etc.).
* **Coeficiente $A_j$**: Valor numérico obtenido del ajuste en unidades de deformación.

#### Tabla 2: Aberraciones Ópticas Primarias de Seidel
Traduce los coeficientes a los componentes físicos fundamentales:
* **Pistón**: Desplazamiento de fase constante ($A_1$).
* **Inclinación X / Y (Tilt)**: Pendiente angular del haz ($A_2, A_3$).
* **Desenfoque (Defocus)**: Error de enfoque o curvatura ($A_5$).
* **Astigmatismo a 0° / 45°**: Deformación anular asimétrica ($A_4, A_6$).
* **Coma X / Y**: Asimetría lateral comética ($A_7, A_8$).
* **Aberración Esférica (3er Orden)**: Deformación simétrica marginal ($A_{13}$).
* **RMS Total**: Error cuadrático medio acumulado de la superficie.

#### Tabla 3: Métricas Globales del Ajuste
* **Peak-to-Valley (PV)**: Diferencia máxima entre el punto más alto y más bajo ($Z_{\text{max}} - Z_{\text{min}}$).
* **Desviación Estándar (RMS Error)**: Variación cuadrática media del residuo $Z_{\text{exp}} - Z_{\text{fit}}$.
* **Puntos Evaluados**: Número de píxeles/puntos contenidos dentro de la pupila.
* **Tiempo de Cómputo**: Duración de la ejecución en milisegundos.

---

### 4.2. Pestaña 2: Malla CCD & Pupila
Muestra un gráfico bidimensional en Matplotlib que delimita la grilla completa del sensor cartesiano y destaca en color el conjunto de puntos contenidos dentro de la pupila circular de normalización.

---

### 4.3. Pestaña 3: Error Residual 3D
Muestra la superficie tridimensional interactiva correspondiente al mapa de diferencias:

$$\text{Error Residual}(x,y) = Z_{\text{exp}}(x,y) - Z_{\text{fit}}(x,y)$$

La pestaña incluye la barra de controles dinámicos `ControlBar3D`:
* **Paleta de Colores (Colormap)**: Selección de escalas cromáticas (viridis, plasma, inferno, coolwarm, magma, cividis).
* **Ángulos de Vista**: Controles numéricos para la elevación y azimut de la cámara 3D.
* **Escala Z**: Factor de amplificación vertical de la deformación.
* **Modo Malla de Alambre (Wireframe)**: Conmutador entre superficie sólida renderizada y estructura de alambre.
* **Cuadrícula**: Conmutador para mostrar u ocultar la grilla de ejes.

---

### 4.4. Pestaña 4: Interferograma Sintético
Genera la reconstrucción bidimensional del patrón óptico de franjas de interferencia que corresponde al frente de onda ajustado, basándose en la ecuación de simulación directa:

$$I(x,y) = a(x,y) + b(x,y) \cos\left(2\pi \cdot \text{escala\_opd} \cdot W_{\text{fit}}(x,y) + 2\pi(f_x X + f_y Y)\right)$$

Incorpora iluminación gaussiana de fondo $a(x,y)$, visibilidad de franja $b(x,y) = 0.42$ e inclinación de la portadora espacial ($f_x = 12, f_y = 3$).

---

## 5. Herramientas Especializadas y Diálogos Flotantes

### 5.1. Procesador Visual de Imágenes Takeda (`InterferogramProcessorDialog`)
Diálogo interactivo para procesar imágenes fotográficas de interferogramas reales:
1. **Filtro Espectral 2D**: Aplica la Transformada de Fourier 2D y permite seleccionar e aislar el pico portador $+f_0$ mediante un filtro pase-banda gaussiano.
2. **Extracción de Fase Arcotangente**: Calcula $\text{atan2}(\text{Im}, \text{Re})$ para obtener la fase enrollada en $[-\pi, +\pi]$.
3. **Desenvolviendo 2D (*Phase Unwrapping*)**: Elimina las discontinuidades de $2\pi$ generando una superficie continua lista para ser ajustada por Zernike.

### 5.2. Comparador Numérico Cruzado (`EngineComparisonDialog`)
Ejecuta de forma paralela el mismo conjunto de datos sobre el motor Python (NumPy) y el motor Fortran CFFI. Despliega una tabla comparativa término a término y reporta la diferencia absoluta máxima y la aceleración en tiempo de cómputo.

### 5.3. Visualizador 3D de Polinomios de Zernike (`ZernikePolynomialViewerDialog`)
Permite seleccionar cualquiera de los 21 polinomios de la base de Zernike ($Z_1 \dots Z_{21}$) y renderizar su superficie teórica pura en 3D con controles completos de rotación y paleta cromática.

### 5.4. Gestor de Presets e Historial (`PresetManagerDialog`)
Permite guardar expresiones matemáticas personalizadas, etiquetarlas y consultar el registro de ecuaciones evaluadas recientemente.

### 5.5. Diálogo Flotante de Error Residual 3D (`ErrorResidual3DDialog`)
Permite desanclar el mapa de error residual 3D a una ventana flotante no modal para comparar visualmente superficies mientras se modifican parámetros en el panel principal.

---

## 6. Diagrama de Flujo Completo de Operación de la GUI

```text
[Entrada: CCD / CSV / Círculo / Imagen]
                    │
                    ▼
       [ParameterInputPanel] ──► Configura Ecuación, N, M, Diámetro y Motor
                    │
                    ▼  (Clic en "Ejecutar Ajuste de Zernike")
          [ZernikeWorker (QThread)]
                    │
                    ├──► Evaluacion de Base U y Gram-Schmidt (Python / Fortran)
                    ├──► Calculo de Coeficientes A_j (ISO 10110-5)
                    └──► Reconstrucción W_fit y Descomposición de Aberraciones
                    │
                    ▼  (Emisión de Señales Qt)
        [Actualización Sincrónica de Pestañas]
                    ├─► Tab 1: Resumen & Aberraciones (Tablas 1, 2 y 3)
                    ├─► Tab 2: Malla CCD & Pupila (Gráfico 2D)
                    ├─► Tab 3: Error Residual 3D (Render 3D + ControlBar3D)
                    └─► Tab 4: Interferograma Sintético (Simulación Óptica 2D)
```
