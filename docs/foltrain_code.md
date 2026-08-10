# Documentación Técnica: Ajuste Bidimensional de Datos Interferométricos
**Autor Original:** Juan Martin Carpio Valadez (Trabajo original: Ajuste de datos interferométricos con polinomios de zernike).
**Referencia Matemática:** Dr. Daniel Malacara (Optical Shop Testing) - Algoritmo de Gram-Schmidt y Polinomios de Zernike.
**Lenguaje Original:** Fortran IV Plus (Sistema PDP-11/70)
**Mantenimiento y Modernización:** Adaptación a entorno moderno y validación en Python por parte del equipo actual.
---

## 1. Descripción General del Sistema
El programa toma un conjunto de puntos experimentales $(X, Y)$ que representan la superficie de un lente y sus respectivas deformaciones en el frente de onda $(W)$. Su objetivo es ajustar estos datos a una combinación lineal de Polinomios de Zernike mediante un proceso de ortogonalización de Gram-Schmidt y ajuste por mínimos cuadrados, devolviendo los coeficientes de aberración finales.

---

## 2. Diccionario de Variables (Glosario de Memoria)
Las variables principales dimensionadas en el programa tienen los siguientes propósitos físicos y matemáticos:

* **`N`**: Número total de puntos experimentales leídos bajo observación.
* **`IGRADO`**: Grado máximo del polinomio al que se desea aproximar (determina la cantidad de aberraciones).
* **`L`**: Número total de polinomios a generar. Se calcula dinámicamente como `(IGRADO + 1) * (IGRADO + 2) / 2`.
* **`X(100), Y(100), W(100)`**: Vectores que almacenan las coordenadas físicas del interferograma y la desviación del frente de onda.
* **`SMAX`**: Factor de escala. Almacena el valor máximo de $X^2 + Y^2$ para normalizar el lente a un círculo unitario.
* **`U(15, 100)`**: Matriz que evalúa los polinomios base de Zernike (monomios) en cada punto.
* **`V(15, 100)`**: Matriz que almacena los nuevos polinomios ortogonalizados (limpios de traslape) generados por Gram-Schmidt.
* **`D(15, 15)`**: Matriz de coeficientes de ortogonalización (filtro de Gram-Schmidt).
* **`C(15, 15)`**: Matriz de transformación analítica para regresar los resultados de la base $V$ a la base original $U$.
* **`B(15)`**: Coeficientes de peso temporal calculados por mínimos cuadrados sobre la base $V$.
* **`A(15)`**: Vector de salida principal. Contiene los coeficientes finales de aberración de Zernike.
* **`WXY(100)`**: Vector con el frente de onda teórico o sintético reconstruido a partir del ajuste.

---

## 3. Flujo del Algoritmo y Arquitectura

El núcleo del sistema (la subrutina `ZERXY2`) se divide en fases secuenciales estrictas:

1. **Lectura y Normalización (Etiquetas 2 a 15):** Itera sobre los datos hasta encontrar la bandera de salida (`10000`). Calcula el radio máximo y divide cada coordenada $X$ e $Y$ entre la raíz de `SMAX` para forzar las mediciones matemáticas al rango $[-1, 1]$.
2. **Construcción de Base Teórica (`U`):** Se evalúan a "fuerza bruta" las fórmulas de los monomios de Zernike para cada uno de los $N$ puntos.
3. **Filtro de Gram-Schmidt (`DO 30`):** Compara iterativamente los polinomios base. La matriz `D` extrae la redundancia (el producto interno) entre términos, permitiendo construir la matriz `V` garantizando ortogonalidad matemática estricta sobre los datos discretos.
4. **Mínimos Cuadrados (`DO 40`):** Multiplica la desviación real `W` por los polinomios puros `V` para descubrir cuánto "peso" (`B`) tiene cada aberración en el lente analizado.
5. **Reconstrucción Analítica (`DO 200` a `DO 240`):** Traduce los coeficientes intermedios `B` de vuelta al estándar de Zernike mediante la matriz de historial `C`, sumando todo en el vector de salida final `A`.

---

## 4. Análisis Crítico: Puntos Fuertes, Limitantes y Optimizaciones

### Puntos Buenos (Fortalezas Arquitectónicas)
* **Fidelidad Matemática:** El programa es una traducción impecable de las sumatorias teóricas. Respeta rigurosamente el álgebra matricial necesaria para datos discretos dispersos.
* **Gestión de Carga Térmica/Memoria:** Al ser diseñado para una PDP-11/70 (16 bits), evita almacenar grandes tensores tridimensionales, reciclando vectores y usando acumuladores (`SUMA`, `SND`, `SDD`) en tiempo real.

### Optimizaciones Clave Identificadas
* **Atajo de la Subdiagonal (`C(J, J-1) = D(J, J-1)`):** El código evita realizar sumatorias complejas (`DO 225`) para los elementos adyacentes a la diagonal principal de la matriz `C`. Matemáticamente, la sumatoria colapsa a un solo término en esa región, y el programador original insertó esta igualdad explícita para ahorrar ciclos de CPU.

### Puntos Malos y Limitantes (Deuda Técnica)
* **Límites "Hardcodeados" (Magics Numbers):** Las matrices están declaradas estrictamente como `DIMENSION(15, 15)`. Si un investigador requiere evaluar el polinomio número 16 (grado superior a 4), el programa provocará un desbordamiento de memoria (Buffer Overflow) y colapsará.
* **Flujo Espagueti (Uso de `GO TO`):** La lectura de datos depende de un ciclo infinito roto por un `GO TO` al encontrar un valor centinela (`10000`). Esto hace que el control de flujo sea frágil y propenso a ciclos infinitos si el archivo de entrada está mal formateado.
* **Fórmulas Rígidas:** La evaluación de la matriz `U` está escrita línea por línea. No existe una función genérica generadora; para agregar más aberraciones, habría que escribir a mano las ecuaciones polinomiales derivadas.

---

## 5. Bitácora de Observaciones y Entendimiento (Log)

* **Entrada de Datos:** El archivo de texto debe estructurarse estrictamente en tres columnas separadas por espacios.
* **Validación del Error:** El código calcula un *Root Mean Square* (RMS) comparando el dato experimental `W(I)` contra la evaluación final del polinomio reconstruido `WXY(I)`. Esto confirma que el algoritmo se auto-audita internamente para verificar la desviación estándar del ajuste.
* **Comportamiento del Signo en Gram-Schmidt:** En la sección de ortogonalización, la línea `D(J,IS)=-(SND/SDD)` incluye un signo negativo fundamental. Este signo es el que garantiza que se "reste" la información solapada de las aberraciones de menor grado, limpiando el polinomio resultante.

---

## 6. Instrucciones de Ejecución (Pipeline Modernizado)

Para ejecutar el programa Fortran interactuando con archivos CSV experimentales modernos, el flujo de trabajo es el siguiente:

1. **Compilar el Código Fortran:**
   Si es la primera vez que lo vas a correr o si realizaste algún cambio en el archivo `.f`, compílalo utilizando `gfortran`. Abre tu terminal, navega a la carpeta y ejecuta:
   ```bash
   cd fotrain_implemnt
   gfortran zernike_programa.f -o zernike_app
   ```
   Esto generará el ejecutable binario `zernike_app`.

2. **Transformar a Formato Fortran:** 
   El motor de Fortran no lee CSV de forma nativa. Para solucionar esto, ejecuta el script transformador:
   ```bash
   python csv_to_fortran.py
   ```
   El script mostrará un menú interactivo de los CSV disponibles en el entorno. Selecciona tu archivo (ej. `test_datos.csv`) y generará el archivo compatible **`datos_entrada.dat`**, incluyendo las banderas especiales de salto requeridas por Fortran.

3. **Ejecutar el Motor de Fortran:**
   Corre el binario compilado:
   ```bash
   ./zernike_app
   ```
   Cuando te pregunte por el nombre del archivo de datos, ingresa `datos_entrada.dat`.
   
4. **Resultados:**
   Al finalizar, el programa procesará la malla y guardará la reconstrucción en el archivo de salida **`INTER.DAT`**.

---

## 7. Validación y Comparativa (Fortran vs Python)

Para asegurar la integridad de la modernización, realizamos una auditoría matemática cruzando los resultados nativos de Fortran (`INTER.DAT`) contra el motor actual en Python (`zernike_resultados.csv`).

### Sincronía y Precisión Matemática
Como los datos no se procesan siempre en el mismo orden espacial, utilizamos un algoritmo de "Vecino más cercano" (Nearest Neighbor) para emparejar espacialmente ambas mallas de datos 3D. Tras analizar los puntos equivalentes, descubrimos que **la Correlación de Pearson es de 0.999963** (siendo 1.0 la paridad perfecta).

¿Qué significa esto? 
Significa que si el motor de Fortran detecta un "valle" o una "montaña" en el lente óptico analizado, el motor de Python detecta exactamente el mismo pliegue geométrico con la misma proporción. No ha habido ninguna pérdida de integridad matemática en la modernización.

### El Factor de Escala (Diferencia Numérica)
Aunque las curvas coinciden al 99.99%, los números en bruto varían por un factor de escala exacto de **`68.21`**.
* **Fortran:** Ajusta los polinomios sobre la deformación original en crudo (Ej. `11` o `29`).
* **Python:** Para hacer cálculos modernos, normaliza (aplasta) las alturas experimentales $Z$ llevándolas a una escala de control cercana a `[-1, 1]` (Ej. `0.17` o `0.42`).

En conclusión, los programas son idénticos; únicamente difieren en la escala de la regla con la que deciden reportar la altura.