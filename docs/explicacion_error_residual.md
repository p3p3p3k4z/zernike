# Explicación del Mapa de Error Residual (2D y 3D)

Este documento ofrece una explicación intuitiva, formal y pedagógica sobre el concepto del Mapa de Error Residual, su fundamento físico y matemático en la metrología óptica de superficies, la interpretación de sus representaciones bidimensionales y tridimensionales, el tratamiento digital de la grilla de datos y el funcionamiento del panel de control interactivo.

---

## 1. Introducción: ¿Qué es el Mapa de Error Residual?

En la caracterización metrológica de superficies ópticas y frentes de onda, el **Mapa de Error Residual** representa la diferencia punto por punto entre la superficie experimental medida ($W_{\text{exp}}$) y la reconstrucción polinomial teórica obtenida a partir de los Polinomios de Zernike ($W_{\text{fit}}$):

$$\text{Error Residual}(x,y) = W_{\text{exp}}(x,y) - W_{\text{fit}}(x,y)$$

La evaluación del error se realiza strictly en el disco de la pupila circular normalizada:

$$\rho = \sqrt{x^2 + y^2} \le 1.0$$

En términos metrológicos, el error residual describe **todo aquello que el modelo polinomial de Zernike no logró capturar**. Corresponde a la discrepancia local en unidades de longitud de onda ($\lambda$) o diferencia de camino óptico (OPD) entre el componente óptico físico real y su aproximación matemática.

---

## 2. Origen Físico y Metrológico del Error Residual

El error residual es un fenómeno inevitable y representativo en la caracterización de ópticas de precisión. Proviene principalmente de tres fuentes:

1. **Límite del Orden Polinomial (Truncamiento de la Base)**:
   La base de Zernike truncada a 21 términos (ISO 10110-5) modela con alta fidelidad las aberraciones ópticas globales de bajo y mediano orden (tales como pistón, inclinación, desenfoque, astigmatismo, coma y aberración esférica). Las variaciones topográficas de alta frecuencia espacial requieren órdenes polinomiales muy superiores para ser representadas.

2. **Micro-rugosidad de Pulido y Tallado Mecánico**:
   Durante el proceso de pulido o maquinado de lentes y espejos, la herramienta abrasiva deja pequeñas marcas locales, asperezas y patrones de herramientas que no pueden ser descritos por polinomios suaves.

3. **Ruido Instrumental y Ambiental del Detector**:
   En interferometría digital de franjas o detección CCD/CMOS, existen fluctuaciones de fase producidas por gradientes térmicos del aire, vibraciones mecánicas y ruido electrónico del detector.

---

## 3. Representación Gráfica: Modalidades 3D y 2D

El sistema Zernike proporciona dos modalidades complementarias de visualización para analizar la topografía del error residual:

### 3.1. Representación Tridimensional (Superficie 3D)

La vista 3D proyecta la amplitud del error residual como una elevación espacial en el eje vertical $Z$:

- **Perspectiva Dinámica**: Permite orientar la cámara en el espacio ajustando los ángulos de **Elevación** ($\theta \in [-90^\circ, 90^\circ]$) y **Azimut** ($\phi \in [0^\circ, 360^\circ]$).
- **Escala de Amplitud ($Z_{\text{scale}}$)**: Permite multiplicar manualmente la amplitud vertical de $0.1\times$ a $10.0\times$ para resaltar pequeños relieves o atenuar deformaciones excesivas.
- **Modos de Malla (Wireframe y Sólido)**: Alterna entre el renderizado de superficie sólida continua con iluminación simétrica y el renderizado de malla de alambre (*wireframe*) para inspeccionar la estructura de la grilla.
- **Proyección de Contornos en el Piso**: Muestra las isolíneas proyectadas directamente sobre la base del plano $Z_{\text{min}}$, facilitando la correlación entre la elevación 3D y las cotas de nivel.
- **Caso de uso**: Ideal para una apreciación intuitiva y cualitativa de la deformación estructural global, alabeo o curvatura espacial de la pieza.

### 3.2. Representación Bidimensional (Mapa de Calor 2D e Isolíneas)

La vista 2D proyecta la magnitud del error directamente sobre el plano cartesiano ortogonal $(X,Y)$ de la pupila normalizada:

- **Proyección 1:1 Sin Distorsión**: Elimina la distorsión de perspectiva geométrica inherente a las proyecciones 3D, ofreciendo una correspondencia espacial exacta con la apertura física de la lente o espejo.
- **Mapa de Calor (Colormap)**: Asigna gradientes de color continuos (como `viridis`, `coolwarm`, `seismic`, `inferno`) a la amplitud del error residual en cada coordenada $(x,y)$.
- **Curvas de Nivel Superpuestas (Isolíneas)**: Permite dibujar contornos cuantitativos de igual fase o elevación, ajustando la densidad de niveles ($N \in [3, 50]$).
- **Caso de uso**: Indispensable en el taller óptico para guiado de maquinado asistido por computadora (pulido por haz de iones o CCKP) y verificación de tolerancias locales según la norma ISO 10110-5.

---

## 4. Tratamiento Digital de Datos: Interpolación y Suavizado

Para evitar picos agudos y artefactos de borde ocasionados por la triangulación directa sobre puntos dispersos, el sistema aplica un procesamiento en tres etapas:

1. **Interpolación a Grilla Cartesiana Regular ($N \times N$)**:
   Los puntos experimentales dispersos $(x_i, y_i, z_i)$ se interpolan a una matriz regular mediante superficies *spline* cúbicas bidimensionales (`scipy.interpolate.griddata`).

2. **Recorte de Pupila Circular Unitaria**:
   Se aplica una máscara circular estricta. Todo punto ubicado fuera del disco unitario ($\rho > 1.0$) se asigna a valor no numérico (`NaN`), garantizando un borde circular nítido sin deformaciones periféricas.

3. **Suavizado Gaussiano Espacial ($\sigma$)**:
   El usuario puede aplicar un filtro de suavizado gaussiano espacial bidimensional. Este filtro atenúa el ruido de alta frecuencia del sensor sin alterar la tendencia topográfica real de la superficie.

---

## 5. Arquitectura del Panel de Control (`ControlBar3D`)

Los parámetros de visualización y filtrado se manipulan en tiempo real mediante la barra de controles `ControlBar3D`, estructurada en dos filas horizontales ordenadas:

### Fila 1: Perspectiva, Cámara y Rango
- **Botón Vista 3D / Vista 2D**: Alterna instantáneamente entre el renderizado de superficie 3D y el mapa de calor 2D. En modo 2D, los controles de cámara 3D se deshabilitan automáticamente.
- **Mapa de Colores (Colormap)**: Selector desplegable con paletas estandarizadas (`viridis`, `coolwarm`, `seismic`, `twilight`, `inferno`, `plasma`, `magma`, `rainbow`, `Spectral`, `jet`, `cividis`).
- **Elevación y Azimut**: Ajuste fino en grados de la inclinación vertical y rotación horizontal de la cámara.
- **Escala Z**: Factor de multiplicación manual de la amplitud vertical.

### Fila 2: Opciones de Malla, Filtros Espaciales e Isolíneas
- **Wireframe y Cuadrícula**: Casillas de verificación para alternar la malla de alambre y la cuadrícula de los ejes.
- **Grilla ($N \times N$)**: Configuración de la resolución de la grilla de interpolación (30 a 200 puntos por lado).
- **Suavizado ($\sigma$)**: Factor de suavizado gaussiano espacial ($0.0$ a $5.0$).
- **Curvas de Nivel y Niveles**: Casilla de activación y selector numérico (3 a 50) para la cantidad de isolíneas a superponer.
- **Botón Restablecer Vista**: Restaura todos los parámetros de cámara, filtros e isolíneas a sus valores por defecto.

---

## 6. Utilidad Práctica en Metrología y Taller Óptico

La combinación del mapa de error residual 2D y 3D proporciona ventajas métricas fundamentales:

- **Validación del Ajuste Polinomial**: Un mapa residual homogéneo y con bajos valores RMS confirma que la base de Zernike utilizada capturó adecuadamente la forma de la superficie.
- **Localización de Errores Zonales**: Permite identificar anillos de pulido, deformaciones mecánicas por soportes de celda y aberraciones locales no simétricas.
- **Control de Calidad ISO 10110-5**: Facilita la extracción de estadísticas de desviación máxima (Peak-to-Valley, P-V) y desviación cuadrática media (RMS) para informes de certificación óptica.
