# Teoría y Análisis Matemático de Interferogramas: Extracción de Fase y Superficies Ópticas

Este documento detalla los fundamentos ópticos, las etapas algorítmicas detalladas y el tratamiento matemático riguroso para la extracción de mapas de deformación de frente de onda $W(x,y)$ (Diferencia de Camino Óptico, OPD) a partir de una **imagen de interferograma** (patrón de franjas de interferencia).

Esta metodología es la base metrológica utilizada en paquetes de software industrial y científico como **Zemax OpticStudio**, **Zygo MetroPro**, **4Sight** y sistemas de interferometría Fizeau/Twyman-Green.

---

## 0. Justificación Conceptual e Ingeniería del Procesamiento

### El Problema Fundamental: ¿Por qué no podemos medir la superficie directamente con la cámara?
1. **La cámara solo mide Intensidad $I(x,y)$ (fotones)**:
   Los sensores CCD/CMOS no pueden medir la fase de la onda de luz $\phi(x,y)$ ni la forma tridimensional $W(x,y)$ directamente; sólo registran cuánta luz llega a cada píxel (escala de grises entre 0 y 255).
2. **La Trampa del Coseno**:
   Al interferir la luz, la fase queda "atrapada" dentro de la función coseno:
   $$I(x,y) = a(x,y) + b(x,y) \cos(\phi(x,y))$$
   Como la función coseno es simétrica ($\cos(\theta) = \cos(-\theta)$), **una elevación (montaña) en la lente produce exactamente el mismo patrón visual que una depresión (valle)**. Es imposible saber si la superficie sobresale o se hunde con una simple foto sin procesar.

---

### ¿Por qué elegimos el Método de la Transformada de Fourier 2D (Takeda)?

Existen dos formas principales en metrología óptica para resolver este problema:

| Característica | Método Tradicional (Phase Shifting - PSI) | Método de Takeda 2D (Fourier FFT) |
| :--- | :--- | :--- |
| **Tomas Fotográficas** | Requiere de 4 a 5 imágenes consecutivas. | **Una sola fotografía (Single-shot)**. |
| **Requisito Mecánico** | Desplazar un espejo con motor piezoeléctrico (PZT) con precisión nanométrica ($0.05\,\mu\text{m}$). | Ninguno. Solo inclinar ligeramente el haz de referencia para crear franjas. |
| **Sensibilidad a Vibraciones** | **Extremadamente alta**. Cualquier corriente de aire o vibración echa a perder la medición. | **Inmune a vibraciones**. Funciona en entornos industriales reales y en tiempo real. |

---

### Explicación Intuitiva del Flujo Algorítmico (Paso a Paso)

```
[Foto Original] ──► [FFT 2D (Frecuencias)] ──► [Filtrado Pase-Banda] ──► [IFFT 2D + Atan2] ──► [Unwrapping] ──► [Zernike (Python/Fortran)]
   (Intensidad)      (Separa Fondo vs Fase)      (Aísla señal útil)      (Fase [-π, +π])     (Fase Continua)     (Coeficientes de Aberración)
```

1. **Transformada de Fourier 2D (FFT2D)**:
   Separa la imagen espacial en tres regiones de frecuencia: el centro $(0,0)$ contiene el ruido e iluminación de fondo $a(x,y)$, mientras que las manchas laterales $+f_0$ y $-f_0$ contienen la información pura de la deformación óptica $\phi(x,y)$.
2. **Filtrado Pase-Banda Gaussiano y Centrado**:
   Usamos un filtro espacial para eliminar el centro (ruido de fondo) y la mancha conjugada. Al desplazar la mancha $+f_0$ al origen $(0,0)$, **eliminamos matemáticamente la inclinación del haz de referencia, dejando únicamente la forma real del elemento óptico**.
3. **Transformada Inversa (IFFT2D) y Arcotangente ($\text{atan2}$)**:
   Convertimos el espectro demodulado de vuelta al plano de la imagen como un número complejo $c(x,y) = \text{Re} + i\,\text{Im}$. Al calcular $\text{atan2}(\text{Im}, \text{Re})$, "liberamos" la fase del interior del coseno.
4. **Desenvolvimiento de Fase (*Phase Unwrapping*)**:
   Debido a que la tangente se repite cada $2\pi$, la fase inicial tiene cortes en forma de "dientes de sierra" en $[-\pi, +\pi]$. El algoritmo suma o resta múltiplos de $2\pi$ en las discontinuidades para obtener una superficie continua y suave en nanómetros.
5. **Filtrado Estricto de Pupila Circular y Ajuste a Zernike**:
   Filtramos los puntos estrictamente dentro del disco unitario $x^2 + y^2 \le 1.0$ y los enviamos al motor de ortogonalización de Gram-Schmidt (Python o Fortran). El motor descompone la superficie en las aberraciones físicas estandarizadas por la norma ISO 10110-5:
   * **Desenfoque ($A_4$)**: Error de curvatura o enfoque.
   * **Astigmatismo ($A_5, A_6$)**: Deformación tipo "silla de montar".
   * **Coma ($A_7, A_8$)**: Asimetría lateral tipo "cometa".
   * **Aberración Esférica ($A_9$)**: Desviación en los bordes de la lente.

---


## 1. Naturaleza Física de los Interferogramas

Un **interferograma** es una imagen bidimensional producida por la superposición de dos haces de luz coherente (usualmente láser de $\lambda = 632.8\text{ nm}$ He-Ne):
1. **Haz de Referencia**: Una onda plana ideal o esférica sin aberraciones.
2. **Haz de Prueba**: Una onda que ha atravesado o se ha reflejado en el elemento óptico en estudio (lente, espejo o superficie).

La distribución espacial de intensidad luminosa $I(x,y)$ registrada en la matriz del detector CCD/CMOS viene dada por la ecuación fundamental de interferencia:

$$I(x,y) = a(x,y) + b(x,y) \cos\Big(\phi(x,y) + 2\pi (f_x x + f_y y)\Big)$$

Donde:
* $a(x,y)$: Intensidad de fondo (*background intensity*), asociada a variaciones no uniformes de iluminación.
* $b(x,y)$: Amplitud de modulación de la franja (*contrast/visibility*).
* $\phi(x,y)$: **Fase espacial del frente de onda**, relacionada directamente con la deformación física $W(x,y)$ por:

$$\phi(x,y) = \frac{2\pi}{\lambda} W(x,y)$$

* $(f_x, f_y)$: Frecuencias portadoras espaciales (*spatial carrier frequency*), introducidas intencionalmente al inclinar ligeramente el espejo o haz de referencia para separar el espectro en el dominio de Fourier.

---

## 2. El Método de la Transformada de Fourier 2D (Takeda et al., 1982)

El método desarrollado por Mitsuo Takeda (*Fourier-transform method of fringe-pattern analysis*, 1982) es el estándar dorado para demodular interferogramas de franja portadora sin contacto directo a partir de una sola toma fotográfica.

### Desglose de las 4 Etapas de Procesamiento

```
[Etapa 1: Imagen Original] 
       │ Auto-recorte Bounding Box + Limpieza de Fondo Oscuro
       ▼
[Etapa 2: Espectro FFT 2D] 
       │ Filtro Pase-Banda Gaussiano + Desplazamiento a DC (0,0)
       ▼
[Etapa 3: Fase Enrollada] 
       │ Arcotangente Atan2 [-π, +π]
       ▼
[Etapa 4: Fase Continua & Puntos] 
       │ Desenvolvimiento 2D + Filtrado Estricto de Pupila Circular [-1, 1]
       ▼
[Ajuste de Polinomios de Zernike (Python / Fortran)]
```

---

### Etapa 1: Preprocesamiento, Auto-recorte Bounding Box y Limpieza de Fondo Oscuro

1. **Normalización de Intensidad**: Se convierte la imagen a escala de grises flotante $I(x,y) \in [0.0, 1.0]$.
2. **Detección de Bounding Box**: Se identifican las coordenadas de píxeles que pertenecen a la señal real del interferograma ignorando el fondo oscuro:

$$\{(x, y) \mid I(x,y) > \text{umbral\_fondo}\}, \quad \text{donde } \text{umbral\_fondo} \approx 0.06$$

3. **Geometría de Cuadrado Perfecto Centrado**: Se calcula el centro del disco $(c_x, c_y)$ y el lado máximo $L = \max(\Delta x, \Delta y)$. Se recorta un cuadrado centrado para no distorsionar la pupila circular en una elipse.
4. **Limpieza Circular Externa**: Se establece a $0.0$ todo píxel fuera del radio de la pupila $R_{\text{pupila}} = \frac{L}{2} \cdot 0.98$:

$$\text{Mascara}(x,y) = \begin{cases} 1 & \text{si } (x-c_x)^2 + (y-c_y)^2 \le R_{\text{pupila}}^2 \\ 0 & \text{en otro caso} \end{cases}$$

---

### Etapa 2: Transformada Rápida de Fourier 2D (FFT) y Filtro Pase-Banda Espectral

1. **Reformulación Compleja**: Mediante la identidad de Euler $\cos(\theta) = \frac{e^{i\theta} + e^{-i\theta}}{2}$, reescribimos la intensidad:

$$I(x,y) = a(x,y) + c(x,y) e^{i 2\pi (f_x x + f_y y)} + c^*(x,y) e^{-i 2\pi (f_x x + f_y y)}$$

Donde el término complejo $c(x,y) = \frac{1}{2} b(x,y) e^{i \phi(x,y)}$ contiene la fase del frente de onda.

2. **Transformada de Fourier 2D**: Al aplicar la FFT2D a la imagen $I(x,y)$, obtenemos el espectro tricolor en el dominio de la frecuencia $(u,v)$:

$$\mathcal{F}\{I(x,y)\} = A(u,v) + C(u - f_x, v - f_y) + C^*(u + f_x, v + f_y)$$

* **Pico Central $A(u,v)$**: Representa las variaciones lentas de fondo e iluminación (frecuencias bajas cerca de $(0,0)$).
* **Pico Lateral Positivo $C(u - f_x, v - f_y)$**: Contiene la información completa de la fase $\phi(x,y)$ desplazada en la frecuencia portadora $+f_0$.
* **Pico Lateral Conjugado $C^*$**: Imagen especular en $-f_0$.

3. **Filtrado Pase-Banda Gaussiano**: Se aísla únicamente el pico positivo $C(u - f_x, v - f_y)$ multiplicando por una ventana gaussiana $H(u,v)$:

$$H(u,v) = \exp\left( -\frac{(u - f_x)^2 + (v - f_y)^2}{2 \sigma^2} \right)$$

4. **Desplazamiento al Origen (Demodulación)**: Se traslada el pico aislado de vuelta al centro del espectro $(0,0)$ para remover la inclinación portadora $2\pi f_0 x$.

---

### Etapa 3: Transformada Inversa 2D (IFFT) y Fase Enrollada (*Wrapped Phase*)

1. **Transformada Inversa 2D (IFFT)**: Se aplica la IFFT2D al espectro filtrado para recuperar el campo complejo demodulado en el espacio real:

$$c(x,y) = \mathcal{F}^{-1}\big\{C(u,v)\big\} = \frac{1}{2} b(x,y) e^{i \phi(x,y)}$$

2. **Cálculo de Fase por Arcotangente**: La fase se extrae calculando el arcotangente de 2 cuadrantes sobre la parte imaginaria y real de $c(x,y)$:

$$\psi(x,y) = \text{atan2}\Big(\text{Im}[c(x,y)], \text{Re}[c(x,y)]\Big)$$

3. **Discontinuidades de $2\pi$**: Debido al rango periódico del arcotangente, la fase extraída $\psi(x,y)$ queda restringida ("enrollada" o *wrapped*) estrictamente en el intervalo discontinuo $[-\pi, +\pi]$.

---

### Etapa 4: Desenvolvimiento de Fase 2D (*Phase Unwrapping*) y Extracción de Puntos en Pupila Circular

1. **Desenvolvimiento Espacial (Eliminación de Saltos de $2\pi$)**: Se integran los gradientes de fase contiguos eliminando cualquier salto superior a $\pi$:

$$\Delta \psi = \text{wrap}\Big(\psi(x+1, y) - \psi(x, y)\Big)$$

$$\text{wrap}(\Delta) = \Delta - 2\pi \cdot \text{round}\left(\frac{\Delta}{2\pi}\right)$$

$$\phi(x,y) = \psi(x,0) + \sum_{k=1}^x \text{wrap}\big(\Delta \psi(k)\big)$$

2. **Mapeo a Coordenadas Normalizadas**: Se transforma el centro físico $(c_x, c_y)$ y el radio $R_{\text{pupila}}$ a coordenadas adimensionales de pupila:

$$X_{\text{norm}} = \frac{x - c_x}{R_{\text{pupila}}}, \quad Y_{\text{norm}} = \frac{y - c_y}{R_{\text{pupila}}}$$

3. **Filtrado Estricto de Pupila Circular**: Se extrae únicamente el conjunto de puntos 3D $(X_i, Y_i, Z_i)$ que satisfacen rigurosamente:

$$\mathcal{S} = \left\{ (X_{\text{norm}}, Y_{\text{norm}}, \phi) \;\middle|\; X_{\text{norm}}^2 + Y_{\text{norm}}^2 \le 1.0 \;\land\; I(x,y) > 0.01 \right\}$$

Esto garantiza un disco circular perfecto sin esquinas ni recuadros.

---

## 3. Método del Esqueleto de Franjas (*Fringe Skeletonization*)

Para interferogramas concéntricos o cerrados sin frecuencia portadora lineal (donde la FFT2D no puede separar picos), se utiliza el algoritmo morfológico de esqueletización:

1. **Filtrado y Suavizado**: Reducción de ruido speckle mediante filtro mediano $3\times 3$.
2. **Detección de Crestas de Intensidad (Hessiano)**: Localización de máximos locales mediante la matriz Hessiana de la imagen $\mathbf{H} = \begin{bmatrix} I_{xx} & I_{xy} \\ I_{xy} & I_{yy} \end{bmatrix}$.
3. **Adelgazamiento Morfológico (*Thinning*)**: Reducción de cada franja continua a un esqueleto de 1 píxel de ancho.
4. **Asignación de Orden de Franja $m$**: Etiquetado secuencial de franjas $m \in \{1, 2, 3, \dots\}$.
5. **Cálculo de Elevación Óptica**:

$$Z(X,Y) = m \cdot \frac{\lambda}{2}$$

---

## 4. Ajuste a Polinomios de Zernike (ISO 10110-5 / ANSI Z80.28)

La nube de puntos extraída $(X_i, Y_i, Z_i)$ se convierte a coordenadas polares de pupila $(\rho_i, \theta_i)$:

$$\rho_i = \sqrt{X_i^2 + Y_i^2} \le 1.0, \quad \theta_i = \text{atan2}(Y_i, X_i)$$

Se evalúa la matriz ortogonal de Zernike $\mathbf{Z}$ y se resuelven los coeficientes de aberración $\mathbf{A} = (A_1, A_2, \dots, A_{21})^T$ mediante el motor seleccionado:
* **Motor Python**: Descomposición QR / SVD en NumPy con norma de ortogonalidad $k=5$.
* **Motor Fortran Nativo**: Re-ortogonalización rápida de Gram-Schmidt binaria con $k=4$.

$$A = (Z^T Z)^{-1} Z^T W$$

---

## 5. Síntesis del Interferograma Óptico Sintético desde Zernike

Para simular la captura de laboratorio de una superficie evaluada y verificar visualmente la reconstrucción del frente de onda, el sistema implementa la simulación directa (*Forward Optical Modeling*).

### 5.1. Ecuación Directa de Intensidad
A partir del mapa de frente de onda reconstruido $W_{\text{fit}}(x,y) = \sum A_j Z_j(x,y)$, la intensidad luminosa bidimensional $I(x,y)$ se modela como:

$$I(x,y) = \text{clip}\Big( a(x,y) + b(x,y) \cos\big( \phi_{\text{óptica}}(x,y) + \phi_{\text{portadora}}(x,y) \big), \, 0.0, \, 1.0 \Big)$$

Donde:
* **Fase Óptica Real**: $\phi_{\text{óptica}}(x,y) = 2\pi \cdot \text{escala\_opd} \cdot W_{\text{fit}}(x,y)$, escala la diferencia de camino óptico (OPD) en múltiplos de la longitud de onda.
* **Portadora Espacial Inclinada**: $\phi_{\text{portadora}}(x,y) = 2\pi (f_x X + f_y Y)$, introduce las franjas de inclinación de referencia con frecuencia $f_x = 12$ y $f_y = 3$.
* **Iluminación Gaussiana de Fondo**: $a(x,y) = 0.48 + 0.07 \cdot \exp(-1.5 (X^2 + Y^2))$, imita el perfil de haz de láser He-Ne de laboratorio.
* **Modulación de Contraste**: $b(x,y) = 0.42$, fija la visibilidad de las franjas dentro del rango dinámico $[0, 1]$.
* **Enmascaramiento Pupilar**: Supresión limpia del fondo fuera del disco circular $\rho = \sqrt{x^2+y^2} \le 0.96$.

---

### 5.2. ¿Por qué Aparecen Múltiples Franjas en la Sintetización?

La aparición de una cantidad considerable de franjas de interferencia en la imagen sintética responde a dos causas físicas y metrológicas fundamentales:

1. **Efecto de la Frecuencia Portadora Espacial ($f_x, f_y$)**:
   Incluso cuando **ningún término de Zernike está activo** (todos los coeficientes $A_j = 0$), el interferograma sintético **no es una imagen blanca o uniforme**. En su lugar, muestra un patrón de **12 franjas paralelas de inclinación** (*carrier tilt fringes*). Esto recrea el comportamiento de un interferómetro real (Fizeau o Twyman-Green), donde el espejo de referencia se inclina intencionadamente para separar el espectro de fase en el dominio de Fourier (método de Takeda) sin ambigüedad de signo.

2. **Densidad de Fase por Amplitud de Aberración ($\text{escala\_opd}$)**:
   Cada incremento de $1.0\lambda$ en la diferencia de camino óptico añade $2\pi$ radianes a la fase $\phi_{\text{óptica}}$, lo que equivale a la formación de una **nueva franja oscura y clara**. Dado que la deformación reconstruida $W_{\text{fit}}$ puede alcanzar valores de varios micrómetros o maderas de longitud de onda (por ejemplo $2.5\lambda$), al multiplicar por el factor $\text{escala\_opd} = 2.0$, la fase angular abarca decenas de ciclos completos ($10\pi$). Esto se traduce en un patrón con una densidad elevada de franjas curvas.

---

### 5.3. Funcionamiento de la Selección de Coeficientes ($Z_1$ a $Z_{21}$)

En la Pestaña 4 de la interfaz gráfica, el usuario dispone de una cuadrícula de **21 casillas de verificación** ($Z_1$ a $Z_{21}$). Al seleccionar o desmarcar coeficientes específicos, el sistema evalúa únicamente la contribución óptica de los términos activos:

$$W_{\text{seleccionado}}(x,y) = \sum_{k \in \text{activos}} A_k Z_k(x,y)$$

Los coeficientes desmarcados se establecen temporalmente en $0$. Esto permite aislar y estudiar el impacto individual o combinado de aberraciones específicas sobre la morfología de las franjas:

* **Inclinación pura (Pistón y Tilt, $Z_1, Z_2, Z_3$)**: Modifica la orientación o el espaciado de las franjas rectas portadoras.
* **Desenfoque ($Z_4$)**: Curva las franjas rectas de la portadora convirtiéndolas en arcos parabólicos o concéntricos.
* **Astigmatismo ($Z_5, Z_6$)**: Deforma las franjas en patrones hiperbólicos en forma de "silla de montar".
* **Coma ($Z_7, Z_8$)**: Introduce asimetría lateral transversal en las franjas (forma de cometa).
* **Aberración Esférica ($Z_{13}$)**: Produce curvatura simétrica radial de alto orden hacia el borde de la pupila.
* **Ningún término seleccionado (Limpiar selección)**: Cancela la fase óptica ($W = 0$) y muestra únicamente las 12 franjas rectas de la portadora de referencia.

---

## 6. Fuentes de Información y Referencias Académicas

Las siguientes referencias constituyen el fundamento científico e industrial utilizado en esta implementación:

1. **Takeda, M., Ina, H., & Kobayashi, S. (1982)**. *Fourier-transform method of fringe-pattern analysis for computer-based topography and interferometry*. **Journal of the Optical Society of America / Applied Optics**, 21(8), 1332–1338.
   * *Artículo seminal original que introdujo el método de demodulación 2D por FFT.*

2. **Malacara, D. (2007)**. *Optical Shop Testing* (3rd ed.). John Wiley & Sons.
   * *Capítulo 13: Zernike Polynomials and Wavefront Fitting.*
   * *Capítulo 14: Phase Shifting and Fourier Transform Interferometry.*

3. **Ghiglia, D. C., & Pritt, M. D. (1998)**. *Two-Dimensional Phase Unwrapping: Theory, Algorithms, and Software*. John Wiley & Sons.
   * *Texto de referencia principal para algoritmos de desenvolvimiento de fase 2D y eliminación de salto de 2π.*

4. **Yu, Q., Liu, X., & Andresen, K. (1994)**. *Fringe-orientation maps and skeleton extraction in interferometry*. **Applied Optics**, 33(29), 6873–6878.
   * *Referencia para la extracción morfológica de crestas y esqueleto de franjas.*

5. **ISO 10110-5:2015 / ANSI Z80.28-2017**. *Optics and photonics — Preparation of drawings for optical elements and systems — Part 5: Surface form tolerances*.
   * *Norma internacional que define la convención estándar de representación de aberraciones y polinomios de Zernike.*

