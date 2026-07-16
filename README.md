# Zernike — Polinomios Ortogonales de Superficies Ópticas

Miniprograma para el ajuste de superficies ópticas mediante **polinomios ortogonales de Zernike** según la norma **ISO 10110-5**, implementando el algoritmo de Gram-Schmidt discreto con verificación cruzada (Malacara, 1990 — *Optical Shop Testing*).

---

## Requisitos

- [uv](https://docs.astral.sh/uv/) ≥ 0.5  
- Python ≥ 3.10

---

## Instalación del entorno

```bash
# Clonar / entrar al directorio del proyecto
cd zernike

# Crear entorno virtual e instalar dependencias principales
uv sync

# (opcional) instalar con dependencias de desarrollo: Jupyter, ipykernel
uv sync --extra dev

# (opcional) instalar dependencias experimentales para el modelo SR-GAN
uv sync --extra srgan
```

El entorno virtual se crea automáticamente en `.venv/`.

---

## Ejecutar el programa principal

```bash
uv run python main.py
```

El programa realiza las siguientes etapas en secuencia y muestra la animación al final:

| Sección | Descripción |
|---------|-------------|
| **1 — Matrices** | Genera 4 matrices de cuadrante con `Z = 3xy + 2x`, las normaliza con `normalizar_vector` e imprime |
| **2 — Flujo Zernike** | Crea 50 puntos en el círculo unitario, ejecuta el flujo completo (U → V → D → B → C → A), verifica ortogonalidad y fórmulas, imprime coeficientes y error RMS |
| **3 — Animación** | Ventana interactiva de matplotlib con la animación del flujo recursivo |

---

## Estructura del proyecto

```
zernike/
├── lib/
│   ├── __init__.py        # Exporta todos los símbolos públicos
│   ├── zernike.py         # Motor matemático (Gram-Schmidt, coeficientes A, B, C)
│   ├── matriz.py          # Generación e impresión de matrices de datos
│   └── visualizacion.py   # Animación matplotlib del flujo recursivo
├── main.py                # Programa de pruebas (punto de entrada)
├── pyproject.toml         # Configuración del proyecto (uv)
├── test_flujo.py          # Script de referencia original
├── poliOrtogonal.ipynb    # Cuaderno Jupyter de desarrollo
└── README.md
```

---

## Flujo matemático del algoritmo

```
Datos (X, Y, W)
      │
      ▼  normalizar_vector(W)
      │
      ▼  evaluar_polinomios()
      U  ── Matriz de diseño (L × N),  L=21, N=puntos
      │
      ▼  construir_base_ortogonal()   [Gram-Schmidt]
   V, D, F ── Base ortogonal / coef. proyección / normas²
      │
      ▼  calcular_B()
      B  ── Pesos en la base ortogonal   B_p = ⟨W, V_p⟩ / F_p
      │
      ▼  calcular_C()                 [Ec. 23, Malacara 1990]
      C  ── Matriz de traducción V → U
      │
      ▼  calcular_A()                 [Ec. 26, Malacara 1990]
      A  ── Coeficientes de Zernike ISO 10110-5
      │
      ▼  reconstruir_W()
   W_fit  ── Superficie ajustada  = A · U
```

**Invariante verificable:**  
`W_fit = Σ Bᵣ Vᵣ = Σ Aᵣ Uᵣ`  (equivalencia de bases, error < 1e-12)

---

### `lib.zernike`

| Función | Descripción |
|---------|-------------|
| `polinomios_zernike()` | Lista de 21 lambdas (k=5, ISO 10110-5) |
| `evaluar_polinomios(X, Y, polis)` | Construye matriz U (L × N) |
| `construir_base_ortogonal(U)` | Gram-Schmidt → V, D, F |
| `calcular_B(W, V, F)` | Pesos ortogonales B |
| `calcular_C(D, L)` | Matriz de traducción C |
| `calcular_A(B, C, L)` | Coeficientes ISO A |
| `reconstruir_W(A, U)` | Superficie ajustada W_fit |
| `ajuste_completo(X, Y, W, polis)` | Orquestador — devuelve dict con U,V,D,F,B,C,A,W_fit |
| `verificar_ortogonalidad(V)` | Valida ⟨Vᵢ, Vⱼ⟩ ≈ 0 |
| `verificar_formulas(resultados)` | Validación cruzada de Ecs. 23 y 26 |

### `lib.matriz`

| Función | Descripción |
|---------|-------------|
| `normalizar_vector(datos)` | Escala al rango [-1, 1] por max absoluto |
| `generar_datos_circulo(N, semilla)` | N puntos uniformes en el círculo unitario, Z = 3xy + 2x |
| `matriz3d_cuadrante(x0,x1,y0,y1)` | Malla cartesiana de un cuadrante, Z = 3xy + 2x |
| `imprimir_matriz_n_puntos(X,Y,Z,nombre)` | Imprime [X, Y, Z] en bloques de 5 |
| `imprimir_matriz_D(D)` | Imprime D triangular inferior |
| `imprimir_vectores_V(V, n_puntos)` | Muestreo de los vectores ortogonales |
| `imprimir_matriz_C(C)` | Imprime C triangular inferior |

### `lib.visualizacion`

| Función | Descripción |
|---------|-------------|
| `graficar_flujo_zernike(resultados, intervalo_ms)` | Animación del flujo con matplotlib |

---

## Animación del flujo

La animación revela cada etapa **barra a barra**, con un color distintivo por variable:

| Variable | Color | Rol |
|----------|-------|-----|
| **U** | 🔵 Azul `#2196F3` | Base de Zernike evaluada |
| **V** | 🟢 Verde `#4CAF50` | Base ortogonalizada |
| **D** | 🔴 Rojo `#F44336` | Coeficientes de proyección |
| **B** | 🟠 Naranja `#FF9800` | Pesos en base ortogonal |
| **C** | 🟣 Púrpura `#9C27B0` | Matriz de traducción |
| **A** | 🔵 Cian `#00BCD4` | Coeficientes Zernike ISO |

La ventana incluye además un **diagrama de pipeline** (inferior) que resalta la etapa activa, y un **scatter** de la superficie ajustada W_fit sobre el círculo unitario.

---
### Zernike en C
Rescritura del programa en **C** para garantizar el máximo rendimiento, gestionando memoria explícitamente y evitando dependencias de Python para equipos con menos recursos.

### Requisitos para C
- Compilador `gcc` y herramientas de construcción (`make`).
- Librería de desarrollo de ncurses (ej. `libncurses5-dev` en Ubuntu/Debian).

### Compilar y Ejecutar

```bash
cd c_impl
make clean
make
./bin/zernike_app
```

---

## Ejecutar el Jupyter Notebook

```bash
uv sync --extra dev
uv run jupyter notebook poliOrtogonal.ipynb
```

---

## Módulo Experimental de Superresolución (SR-GAN)

Hemos incorporado un entorno experimental para aumentar la resolución de interferogramas de $32\times32$ a $128\times128$ píxeles, empleando una red neuronal generativa (SR-GAN), seguido de una reconstrucción matemática idealizada con Zernike.

**1. Preprocesamiento Inteligente (Bounding Box)**  
Antes de alimentar la red, el sistema incluye un algoritmo de **Auto-Recorte Inteligente**. Este detecta la pupila circular ignorando el ruido oscuro del sensor y ajusta un cuadrado perfecto (Bounding Box) alrededor del interferograma para evitar deformaciones elípticas.
Puedes probar cómo recorta tus fotos sin necesidad de correr la red neuronal:
```bash
uv run python test/inference.py test/Interferogramas/Imagen10.jpg --preprocess-only
```
Esto guardará la imagen centrada y recortada en `test/resultados_sr/`.

**2. Entrenar el modelo (Generación de pesos)**  
Para poder realizar la inferencia completa, primero necesitas generar los pesos de la red. Ejecuta:
```bash
uv run python test/train_srgan.py --epochs 100
```
Esto creará los archivos de pesos (`generator_epoch_100.pth` y `discriminator_epoch_100.pth`) dentro de la carpeta `test`.

**3. Inferencia Completa y Reconstrucción Zernike**  
Pasa una imagen para ejecutar todo el flujo: recortará, hará superresolución con SR-GAN (128x128), y finalmente extraerá el modelo idealizado libre de ruido (`W_fit`) con los polinomios de Zernike.

```bash
uv run python test/inference.py test/Interferogramas/Imagen10.jpg
```
*Si tu archivo de pesos está en otra ubicación, usa `--weights /ruta/al/archivo.pth`.*
Se abrirá una gráfica comparativa y se guardarán 4 variantes de resultados en `test/resultados_sr/`.

---

## Referencia

> Malacara, D. (Ed.). (1990). *Optical Shop Testing* (2nd ed.). Wiley.  
> ISO 10110-5: *Optics and photonics — Preparation of drawings for optical elements and systems — Part 5: Surface form tolerances*.
