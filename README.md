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

# (opcional) instalar dependencias de desarrollo (Jupyter, pytest):
uv sync --extra dev

# (opcional) instalar dependencias experimentales para el modelo SR-GAN:
uv sync --extra srgan
```

El entorno virtual se crea automáticamente en `.venv/`.

---

## Ejecutar el programa principal

```bash
uv run python main.py
```

El programa principal incluye varios flujos de simulación interactivos (Malla CCD, Importación CSV, Círculo unitario aleatorio, etc.):

| Flujo | Descripción |
|---|---|
| **1 — CCD_SENSOR** | Malla simétrica $N \times M$ de píxeles CCD con origen en el centro óptico, filtrada por pupila circular y evaluación matemática configurable. |
| **2 — CSV** | Carga de datos experimentales desde archivo `.csv` $(X, Y, Z)$. |
| **3 — CIRCULO** | Generación uniforme de puntos en el círculo unitario ($N=50$). |
| **4 — CCD (Legacy)** | Simulación sobre 4 cuadrantes fijos con filtro de pupila. |
| **5 — CUADRANTE** | Demostración de desbordamiento por dominio asimétrico (Cuadrante I). |

Al finalizar la sección de Zernike, el programa imprime los coeficientes $A$, realiza la **descomposición de aberraciones ópticas primarias** y muestra el **mapa tridimensional del error residual**.

---

## Ejecutar las Pruebas Unitarias

El proyecto cuenta con una suite completa de pruebas unitarias automatizadas en la carpeta `tests/`:

```bash
uv run pytest
```

Para ver la ejecución detallada de cada test:
```bash
uv run pytest -v
```

*(Consulta la guia en [tests/README.md](file:///home/m4r10/Documents/projects/zernike/tests/README.md) para más información sobre cómo funcionan las pruebas).*

---

## Estructura del proyecto

```
zernike/
├── lib/
│   ├── __init__.py        # Exporta todos los símbolos públicos
│   ├── zernike.py         # Motor matemático (Gram-Schmidt, ResultadoZernike, coeficientes A, B, C)
│   ├── matriz.py          # Parser AST seguro, descomposición de aberraciones, mallas CCD y pupila
│   ├── io.py              # Sistema de logging estándar y exportación a CSV
│   └── visualizacion.py   # Animación de flujo recursivo y mapa 3D de error residual
├── tests/
│   ├── README.md          # Guía didáctica de pruebas unitarias
│   ├── test_matriz.py     # Pruebas para normalización, parser AST y aberraciones
│   └── test_zernike.py    # Pruebas para Gram-Schmidt, ortogonalidad y ajuste completo
├── main.py                # Programa principal e interfaz interactiva CLI
├── pyproject.toml         # Configuración del proyecto y dependencias (uv)
├── poliOrtogonal.ipynb    # Cuaderno Jupyter de desarrollo
└── README.md              # Documentación general del proyecto
```

---

## Flujo matemático del algoritmo

```
Datos (X, Y, W)
      │
      ▼  normalizar_vector(W) / filtrar_pupila()
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
      ▼  reconstruir_W() & descomponer_aberraciones()
   W_fit ── Superficie ajustada  = A · U
```

**Invariante verificable:**  
`W_fit = Σ Bᵣ Vᵣ = Σ Aᵣ Uᵣ`  (equivalencia de bases, error < 1e-12)

---

## Resumen de Módulos y Funciones

### `lib.zernike`

| Función / Estructura | Descripción |
|---|---|
| `ResultadoZernike` | Contenedor de datos inmutable (NamedTuple) con acceso doble: atributo (`res.A`) y clave dict (`res['A']`). |
| `polinomios_zernike()` | Lista de 21 lambdas ($k=5$, ISO 10110-5). |
| `evaluar_polinomios(X, Y, polis)` | Construye matriz $U$ ($L \times N$). |
| `construir_base_ortogonal(U)` | Gram-Schmidt $\rightarrow V, D, F$. |
| `calcular_B(W, V, F)` | Pesos ortogonales $B$. |
| `calcular_C(D, L)` | Matriz de traducción $C$. |
| `calcular_A(B, C, L)` | Coeficientes ISO $A$. |
| `reconstruir_W(A, U)` | Superficie ajustada $W_{fit}$. |
| `ajuste_completo(X, Y, W, polis)` | Orquestador — devuelve `ResultadoZernike`. |
| `verificar_ortogonalidad(V)` | Valida $\langle V_i, V_j \rangle \approx 0$. |
| `verificar_formulas(resultados)` | Validación cruzada de Ecs. 23 y 26 (retorna `bool`). |

### `lib.matriz`

| Función | Descripción |
|---|---|
| `parsear_ecuacion_z(expr_str)` | Evaluador de ecuaciones seguro basado en AST (soporta polinómicas, trigonométricas `sin, cos, tan`, `sqrt, exp, log` y constantes `pi, e`). |
| `descomponer_aberraciones(A)` | Traduce el vector $A$ a Pistón, Tilt X/Y, Defocus, Astigmatismo 0°/45°, Coma X/Y, Aberración Esférica de 3er orden y RMS Total. |
| `normalizar_vector(datos)` | Escala vectores al rango $[-1, 1]$ por su valor máximo absoluto. |
| `generar_malla_ccd(N, M, func_z)` | Genera una cuadrícula de $N \times M$ píxeles de un sensor CCD. |
| `centrar_coordenadas(X, Y, N, M)` | Centra las coordenadas cartesianas al centro óptico $(0, 0)$. |
| `filtrar_pupila(X, Y, Z, diametro)` | Filtra y normaliza los puntos dentro del círculo de la pupila. |

### `lib.io`

| Función | Descripción |
|---|---|
| `inicializar_logger(filename)` | Configura el logger estándar de Python (`logging.getLogger("zernike")`) para consola y archivo sin monkey-patching. |
| `exportar_resultados_csv(...)` | Exporta coordenadas, datos reales, ajustados y error residual a CSV. |
| `exportar_zemax(A, R_pupila, lambda)` | Exporta los coeficientes de Zernike al formato estándar de Zemax OpticStudio (`.zrn`). |
| `exportar_codev(A, R_pupila)` | Exporta los coeficientes al formato de superficie de CODE V (`.dat`). |

### `lib.visualizacion`

| Función | Descripción |
|---|---|
| `graficar_flujo_zernike(resultados)` | Ventana interactiva de Matplotlib con la animación del flujo recursivo de capas. |
| `mapa_fase_3d(X, Y, Z_diff)` | Gráfica 3D del error residual ($Z_{exp} - Z_{fit}$) para identificar deformaciones ópticas no capturadas. |

---

## Referencias

> Malacara, D. (Ed.). (1990). *Optical Shop Testing* (2nd ed.). Wiley.  
> ISO 10110-5: *Optics and photonics — Preparation of drawings for optical elements and systems — Part 5: Surface form tolerances*.
