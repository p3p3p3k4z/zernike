# Zernike — Polinomios Ortogonales de Superficies Ópticas

Miniprograma para el ajuste de superficies ópticas mediante **polinomios ortogonales de Zernike** según la norma **ISO 10110-5**, implementando el algoritmo de Gram-Schmidt discreto con verificación cruzada (Malacara, 1990 — *Optical Shop Testing*).

---

## Descargas Directas de Ejecutables e Instaladores (Releases)

Puedes descargar los paquetes binarios precompilados de la aplicación gráfica directamente desde las **[Publicaciones del Repositorio (GitHub Releases)](../../releases)**:

| Sistema Operativo / Formato | Archivo de Descarga | Comando de Instalación / Ejecución |
|---|---|---|
| **Windows 10/11 (64-bit)** | `zernike-gui.exe` | Ejecutable standalone portable (doble clic) |
| **Debian / Ubuntu / Mint** | `zernike-gui_1.0.0_amd64.deb` | `sudo dpkg -i zernike-gui_1.0.0_amd64.deb` |
| **Fedora / RHEL / CentOS** | `zernike-gui-1.0.0-1.x86_64.rpm` | `sudo dnf install zernike-gui-1.0.0-1.x86_64.rpm` |
| **Linux (Binario Genérico)** | `zernike-gui` | `chmod +x zernike-gui && ./zernike-gui` |

---

## Requisitos para Desarrollo

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

## Modos de Ejecución (GUI & CLI)

El proyecto soporta **ambos modos de ejecución** de forma nativa e integrada:

### Modo 1: Interfaz Gráfica de Escritorio (GUI Estilo Zemax)
Puedes lanzarla directamente con cualquiera de estas opciones:
```bash
uv run python gui_app.py
# O también pasando la bandera --gui al archivo principal:
uv run python main.py --gui
```

### Modo 2: Consola de Comandos (CLI)
```bash
uv run python main.py
```
Al ejecutar `main.py` sin banderas, la consola interactiva te presentará el siguiente menú (incluyendo la opción `0` para conmutar a la GUI):

| Opción | Flujo / Descripción |
|---|---|
| **0 — GUI** | Inicia la ventana gráfica PySide6 de escritorio estilo Zemax. |
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
├── .agents/               # Infraestructura de Agentes de IA Especializados (Reglas y Skills)
│   ├── AGENTS.md          # Reglas globales del workspace (ISO 10110-5, estándar de comentarios)
│   └── skills/            # Habilidades: optics-researcher, software-architect, code-documenter, etc.
├── lib/
│   ├── __init__.py        # Exporta todos los símbolos públicos
│   ├── zernike.py         # Motor matemático (Gram-Schmidt, ResultadoZernike, coeficientes A, B, C)
│   ├── matriz.py          # Parser AST seguro, descomposición de aberraciones, mallas CCD y pupila
│   ├── interferometria.py # Demodulación 2D FFT de Takeda, desenvolvimiento de fase y interferograma sintético
│   ├── io.py              # Sistema de logging estándar y exportación a CSV, Zemax y CODE V
│   ├── visualizacion.py   # Renderizado 2D/3D, interferogramas sintéticos y mapas de error residual
│   └── fortran_runner.py  # Wrapper CFFI de aceleración nativa Fortran
├── gui/                   # Interfaz gráfica de usuario en PySide6 / Qt6
│   ├── main_window.py     # Ventana principal estilo Zemax con 4 pestañas de visualización
│   ├── components/        # Componentes POO desacoplados (menú, panel de control, tablas)
│   └── error_residual_dialog.py # Diálogo 3D flotante no modal del mapa de error residual
├── tests/
│   ├── README.md          # Guía didáctica de pruebas unitarias
│   ├── test_matriz.py     # Pruebas para normalización, parser AST y aberraciones
│   ├── test_zernike.py    # Pruebas para Gram-Schmidt, ortogonalidad y ajuste completo
│   ├── test_gui.py        # Pruebas automatizadas de la interfaz gráfica PySide6
│   ├── test_interferometria.py # Pruebas de demodulación Takeda 2D y síntesis de franjas
│   └── test_fortran.py    # Validación cruzada Python vs. Fortran
├── docs/                  # Documentación teórica y guías de desarrollo
├── main.py                # Orquestador CLI e iniciador de la GUI
├── gui_app.py             # Punto de entrada directo a la interfaz de escritorio
└── pyproject.toml         # Configuración del proyecto y dependencias (uv)
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

### `lib.interferometria`

| Función | Descripción |
|---|---|
| `demodular_fase_fft2d(img)` | Extracción de fase continua mediante la Transformada de Fourier 2D (Takeda et al., 1982) e isolación del pico $+f_0$. |
| `desenvolver_fase_2d(fase_wrap)` | Desenvolviendo de fase 2D (*phase unwrapping*) eliminando discontinuidades de $2\pi$. |
| `extraer_puntos_pupila_circular(fase, img)` | Recorta y normaliza los puntos dentro del disco unitario $\rho \le 1.0$. |
| `sintetizar_interferograma_desde_zernike(A, N, carrier, escala)` | Genera la simulación óptica directa $I(x,y)$ con frecuencia portadora inclinada $(f_x, f_y)$ e iluminación gaussiana de fondo. |

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
| `inicializar_logger(filename)` | Configura el logger estándar de Python (`logging.getLogger("zernike")`) para consola y archivo en `output/` sin monkey-patching. |
| `exportar_resultados_csv(...)` | Exporta coordenadas, datos reales, ajustados y error residual a CSV. |
| `exportar_zemax(A, R_pupila, lambda)` | Exporta los coeficientes de Zernike al formato estándar de Zemax OpticStudio (`.zrn`). |
| `exportar_codev(A, R_pupila)` | Exporta los coeficientes al formato de superficie de CODE V (`.dat`). |

### `lib.visualizacion`

| Función | Descripción |
|---|---|
| `graficar_flujo_zernike(resultados)` | Ventana interactiva de Matplotlib con la animación del flujo recursivo de capas. |
| `mapa_fase_3d(X, Y, Z_diff)` | Gráfica 3D del error residual ($Z_{exp} - Z_{fit}$) para identificar deformaciones ópticas no capturadas. |
| `graficar_interferograma_sintetico(...)` | Renderizado bidimensional del interferograma óptico sintético adaptado al tema dinámico (Oscuro/Claro). |


---

## Compilación de Ejecutables Standalone (Linux y Windows)

El proyecto incluye la configuración y automatizaciones necesarias para empaquetar la aplicación en un ejecutable independiente (*standalone*) que no requiere la instalación de Python ni dependencias en el sistema de destino. El ejecutable lanza directamente la interfaz gráfica en PySide6.

Para generar el ejecutable en el sistema actual (Linux o Windows):

```bash
# 1. Sincronizar el entorno y dependencias de desarrollo
uv sync --all-groups

# 2. Generar el ejecutable standalone
uv run python build_executable.py
```

- **Linux**: El ejecutable binario se generará en `dist/zernike-gui`.
- **Windows**: El ejecutable se generará en `dist\zernike-gui.exe`.

---

## Referencias

> Malacara, D. (Ed.). (1990). *Optical Shop Testing* (2nd ed.). Wiley.  
> ISO 10110-5: *Optics and photonics — Preparation of drawings for optical elements and systems — Part 5: Surface form tolerances*.

---

## Licencia

Este proyecto está licenciado bajo los términos de la **[Licencia MIT](LICENSE)**. Eres libre de usar, modificar y distribuir este software para propósitos académicos, científicos o comerciales.


