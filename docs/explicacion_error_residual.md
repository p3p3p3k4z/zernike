# Explicación del Mapa de Error Residual 3D

Este documento ofrece una explicación intuitiva, formal y pedagógica sobre el concepto del Mapa de Error Residual, su origen físico en la metrología óptica, la problemática visual detectada en las representaciones tridimensionales y la solución técnica implementada en el proyecto.

---

## 1. Introducción: ¿Qué es el Mapa de Error Residual?

En la metrología de superficies ópticas, el **Mapa de Error Residual** representa la diferencia punto por punto entre la superficie o frente de onda experimental medido ($Z_{\text{exp}}$) y el modelo matemático reconstruido mediante la combinación de polinomios ortogonales de Zernike ($Z_{\text{fit}}$):

$$\text{Error Residual}(x,y) = Z_{\text{exp}}(x,y) - Z_{\text{fit}}(x,y)$$

En términos sencillos, el error residual describe **todo aquello que la reconstrucción polinomial de Zernike no logró capturar**. Muestra la discrepancia local exacta entre la medición física del laboratorio y la aproximación matemática teórica.

---

## 2. Origen: ¿Cómo y Por Qué se Produce el Error Residual?

El error residual es un fenómeno natural y esperado en cualquier proceso de medición óptica. Se origina principalmente por tres factores:

1. **Límite del Orden Polinomial**:
   Los polinomios de Zernike incorporados en este sistema (hasta el término 21) representan de manera excelente las aberraciones ópticas globales de bajo y mediano orden (como desenfoque, inclinación, astigmatismo o aberración esférica). Sin embargo, las superficies reales presentan pequeñas variaciones espaciales de alta frecuencia que requerirían cientos de términos adicionales para ser modeladas por completo.

2. **Micro-rugosidad de Pulido y Tallado**:
   Durante la fabricación de elementos ópticos (lentes o espejos), los procesos mecánicos de maquinado y pulido dejan diminutas marcas o imperfecciones locales que no responden a formas polinomiales suaves.

3. **Ruido Experimental del Detector**:
   En las capturas fotográficas de interferogramas o en las lecturas de sensores CCD/CMOS, existen pequeñas fluctuaciones de intensidad causadas por turbulencia térmica del aire, vibraciones ambientales o ruido electrónico del propio sensor.

---

## 3. Problemática Visual: Los Picos y Artefactos en la Gráfica 3D

Al representar el error residual como una superficie tridimensional sobre la pupila circular de la óptica, se observaba un comportamiento indeseado: la aparición de **picos agudos desproporcionados y crestas artificiales**, especialmente en las orillas de la gráfica.

### ¿Por qué se producían estos picos?
* **Triangulación Directa sobre Puntos Dispersos**: El método inicial unía los puntos de medición construyendo triángulos directamente entre ellos (*Triangulación de Delaunay*).
* **Deformación en los Bordes Circulares**: Al recortar la grilla sobre la pupila circular, los triángulos creados cerca de la frontera resultaban muy alargados y estrechos. Cualquier pequeña diferencia de valor en la orilla se proyectaba como un pico o "aguja" totalmente artificial.
* **Ruido Áspero**: El ruido aleatorio del detector producía asperezas puntuales que dificultaban la apreciación visual del perfil real de la superficie.

---

## 4. Solución Implementada: Grilla Regular e Interpolación Suave

Para corregir estos artefactos visuales sin alterar los cálculos cuantitativos del sistema (tales como las métricas globales PV y RMS de las tablas de resumen), se diseñó un proceso de renderizado en tres etapas:

1. **Interpolación a Grilla Cartesiana Regular**:
   Los puntos dispersos se proyectan a una matriz regular uniforme ($N \times N$) mediante superficies spline cúbicas bidimensionales. Esto asegura que la transición entre puntos vecinos sea continua y suave.

2. **Re-Enmascaramiento de Pupila**:
   Se aplica un recorte circular limpio sobre la matriz regular. Los puntos ubicados fuera del disco unitario ($\rho \le 1.0$) se omiten, eliminando por completo los picos estirados de las orillas.

3. **Filtro Gaussiano Espacial Interactivo ($\sigma$)**:
   Se añadió un control directo en la barra de herramientas 3D (`ControlBar3D`) que permite aplicar un filtro de suavizado gaussiano espacial. Este control atenúa el ruido de alta frecuencia para que el usuario pueda visualizar la tendencia topográfica real con comodidad.

---

## 5. Utilidad Práctica en la Metrología Óptica

La visualización adecuada del error residual ofrece grandes beneficios al ingeniero u óptico:
* **Verificación de la Calidad del Ajuste**: Un mapa residual plano y cercano a cero confirma que la superficie fue correctamente caracterizada por los coeficientes de Zernike calculados.
* **Identificación de Defectos Locales**: Facilita la detección visual de marcas de pulido o deformaciones mecánicas puntuales en la lente.
* **Guía para Procesos de Tallado**: Permite orientar procesos de pulido asistido por computadora para corregir zonas específicas de la superficie.
