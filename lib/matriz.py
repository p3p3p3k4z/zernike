"""
lib/matriz.py
=============
Funciones para generacion, normalizacion e impresion de matrices
de datos de superficie optica.

Fuente: poliOrtogonal.ipynb (Cuaderno de Jupyter del proyecto)
"""

import numpy as np
import pandas as pd
from typing import Tuple


def normalizar_vector(datos):
    """
    Normaliza un vector dividiendo cada elemento por el valor
    maximo absoluto encontrado en el vector.

    Esta normalizacion escala los datos al rango [-1, 1] sin
    deformar la distribucion relativa de los puntos, cumpliendo
    con el requisito del circulo unitario de la norma ISO 10110.

    Parametros
    ----------
    datos : ndarray (N,)

    Retorna
    -------
    ndarray (N,) normalizado, o el original si max == 0.
    """
    max_val = np.max(np.abs(datos))
    if max_val == 0:
        return datos.copy()
    return datos / max_val


def normalizar_por_radio(X, Y):
    """
    Normaliza coordenadas cartesianas para que todos los puntos
    caigan dentro del circulo unitario (radio maximo = 1).
    Util para datos experimentales con apertura circular.
    Norma ISO 10110
    """
    radio = np.sqrt(X**2 + Y**2)
    R_max = np.max(radio)
    if R_max == 0:
        return X, Y
    return X / R_max, Y / R_max


def generar_datos_circulo(N=50, semilla=42, func_z=None):
    """
    Genera N puntos aleatorios dentro del circulo unitario con
    densidad uniforme en area, y calcula Z.

    Por que sqrt(random)?
    La distribucion radial uniforme en area requiere rho ~ sqrt(U)
    donde U ~ Uniform(0,1). Esto garantiza que los puntos no se
    acumulen en el centro sino que se distribuyan uniformemente.

    Parametros
    ----------
    N      : int  -- numero de puntos (defecto 50)
    semilla: int  -- semilla para reproducibilidad
    func_z : callable, opt -- funcion personalizada para calcular Z(X, Y)

    Retorna
    -------
    X, Y, Z : ndarray (N,) -- coordenadas y valores de superficie
    """
    np.random.seed(semilla)
    rho   = np.sqrt(np.random.rand(N))
    theta = 2 * np.pi * np.random.rand(N)
    X = rho * np.cos(theta)
    Y = rho * np.sin(theta)
    if func_z is None:
        Z = 3 * X * Y + 2 * X
    else:
        Z = func_z(X, Y)
    return X, Y, Z


def matriz3d_cuadrante(x_start, x_end, y_start, y_end, n_x=5, n_y=10, func_z=None):
    """
    Genera una malla cartesiana de puntos en el cuadrante definido
    por [x_start, x_end] x [y_start, y_end] y calcula Z.

    Proceso interno:
      1. linspace -> vectores de ejes
      2. meshgrid -> plano bidimensional
      3. flatten  -> vectores 1D de N=n_x*n_y puntos
      4. calculo vectorizado de Z

    Parametros
    ----------
    x_start, x_end : float -- limites del eje X
    y_start, y_end : float -- limites del eje Y
    n_x, n_y       : int   -- numero de puntos por eje
    func_z         : callable, opt -- funcion personalizada para calcular Z(X, Y)

    Retorna
    -------
    X_flat, Y_flat, Z_flat : ndarray (N,) donde N = n_x * n_y
    """
    x_vals = np.linspace(x_start, x_end, n_x).astype(int)
    y_vals = np.linspace(y_start, y_end, n_y).astype(int)

    xv, yv   = np.meshgrid(x_vals, y_vals)
    x_flat   = xv.flatten()
    y_flat   = yv.flatten()
    if func_z is None:
        z_flat   = (3 * x_flat * y_flat + 2 * x_flat).astype(int)
    else:
        z_flat   = func_z(x_flat, y_flat)

    return x_flat, y_flat, z_flat


def imprimir_matriz_n_puntos(x_vals, y_vals, z_vals, nombre):
    """
    Imprime en consola los N puntos de una matriz en formato
    [X, Y, Z], agrupados en bloques de 5 por linea.

    Parametros
    ----------
    x_vals, y_vals, z_vals : ndarray (N,)
    nombre                 : str  -- titulo descriptivo
    """
    n = len(z_vals)
    print(f"\n{'='*25} {nombre} ({n} Puntos) {'='*25}")
    for start in range(0, n, 5):
        bloque = []
        for k in range(start, min(start + 5, n)):
            bloque.append(f"[{x_vals[k]:.4g}, {y_vals[k]:.4g}, {z_vals[k]:.4g}]")
        print(" ; ".join(bloque))


def imprimir_matriz_D(D):
    """
    Imprime la matriz de coeficientes de Gram-Schmidt D en
    formato triangular inferior con etiquetas de fila/columna.

    Parametros
    ----------
    D : ndarray (L, L)
    """
    L = D.shape[0]
    print("\n" + "="*42)
    print("  MATRIZ DE COEFICIENTES D (Gram-Schmidt)")
    print("="*42)
    for i in range(L):
        partes = []
        for j in range(i + 1):
            if D[i, j] != 0:
                partes.append(f"{D[i,j]:7.3f}")
            else:
                partes.append("   .   ")
        print(f"r{i:02d} | {'  '.join(partes)}")


def imprimir_vectores_V(V, n_puntos=10):
    """
    Imprime los primeros n_puntos valores de cada vector ortogonal V_r.

    Parametros
    ----------
    V        : list[ndarray] -- base ortogonal
    n_puntos : int           -- cuantos puntos mostrar por vector
    """
    print("\n" + "="*42)
    print(f"  VECTORES ORTOGONALES V (primeros {n_puntos} pts)")
    print("="*42)
    for i, vec in enumerate(V):
        muestra  = vec[:n_puntos]
        fmtv = "  ".join(f"{val:8.4f}" for val in muestra)
        print(f"V{i+1:02d} -> [{fmtv}]")


def imprimir_matriz_C(C):
    """
    Imprime la matriz de traduccion C en formato triangular inferior.
    Solo se muestran los elementos con valor absoluto > 1e-10.

    Parametros
    ----------
    C : ndarray (L, L)
    """
    print("\n" + "="*42)
    print("  MATRIZ DE TRADUCCION C  (V -> U)")
    print("="*42)
    for i, fila in enumerate(C):
        partes = []
        for j in range(i + 1):
            if abs(fila[j]) > 1e-10:
                partes.append(f"{fila[j]:9.4f}")
            else:
                partes.append("   .     ")
        print(f"r{i:02d} | {'  '.join(partes)}")

def poli_zenike_print(X, Y, polinomios, n_rows=None):
    """
    Evalúa la lista de polinomios hardcodeados en los puntos (X,Y)
    y muestra una tabla con los valores.
    Parámetros:
        X, Y: arreglos de coordenadas (1D)
        polinomios: lista de funciones lambda
        n_rows: número de filas a mostrar (None = todas)
    """
    N = len(X)
    # Crear un DataFrame con los puntos y los valores de cada polinomio
    data = {'x': X, 'y': Y}
    for i, func in enumerate(polinomios):
        r = i + 1
        data[f'U{r}'] = func(X, Y)
    df = pd.DataFrame(data)

    # Mostrar solo las primeras n_rows filas
    if n_rows is None:
        n_rows = N
    else:
        n_rows = min(n_rows, N)

    print("\n" + "="*80)
    print(f" EVALUACION DE POLINOMIOS (primeras {n_rows} filas de {N})")
    print("="*80)
    print(df.head(n_rows).to_string(index=False))

def imprimir_vector_F(F):
    print("\n" + "="*42)
    print("  VECTOR F (Normas al cuadrado)")
    print("="*42)
    for i, f in enumerate(F):
        print(f"  F_{i+1:02d} = {f:.6e}")

def imprimir_vector_B(B):
    print("\n" + "="*42)
    print("  VECTOR B (Pesos en Base Ortogonal)")
    print("="*42)
    for i, b in enumerate(B):
        print(f"  B_{i+1:02d} = {b:+.6f}")

# ============================================================
# Funciones de simulación CCD
# ============================================================

def generar_malla_ccd(
    N: int, M: int, func_z=None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Genera una malla cartesiana completa de N x M puntos que representa
    los pixeles de un sensor CCD. El origen es la esquina superior
    izquierda (0, 0).

    Parametros
    ----------
    N      : int            -- numero de filas del sensor (eje Y)
    M      : int            -- numero de columnas del sensor (eje X)
    func_z : callable, opt  -- funcion Z(x, y) para la superficie.
                              Por defecto usa Z = 3xy + 2x.

    Retorna
    -------
    X_pixel, Y_pixel, Z : ndarray (N*M,)
    """
    cols = np.arange(M, dtype=float)   # eje X -> columnas
    filas = np.arange(N, dtype=float)  # eje Y -> filas

    xv, yv = np.meshgrid(cols, filas)
    X_pixel = xv.flatten()
    Y_pixel = yv.flatten()

    X_c = X_pixel - (M - 1) / 2.0
    Y_c = Y_pixel - (N - 1) / 2.0

    if func_z is None:
        Z = 3 * X_c * Y_c + 2 * X_c
    else:
        Z = func_z(X_c, Y_c)

    return X_pixel, Y_pixel, Z


def centrar_coordenadas(
    X_pixel: np.ndarray, Y_pixel: np.ndarray, N: int, M: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Traslada las coordenadas de pixel al centro optico del sensor,
    de modo que el pixel central quede en (0, 0).

    Transformacion:
        X_c = X_pixel - M / 2
        Y_c = Y_pixel - N / 2

    Parametros
    ----------
    X_pixel, Y_pixel : ndarray (N*M,) -- coordenadas en espacio de pixel
    N, M             : int             -- dimensiones del sensor

    Retorna
    -------
    X_c, Y_c : ndarray (N*M,) -- coordenadas centradas al origen optico
    """
    X_c = X_pixel - (M - 1) / 2.0
    Y_c = Y_pixel - (N - 1) / 2.0
    return X_c, Y_c


def filtrar_pupila(
    X_c: np.ndarray,
    Y_c: np.ndarray,
    Z: np.ndarray,
    diametro: float,
) -> dict:
    """
    Filtra los puntos del sensor CCD segun si caen dentro o fuera
    del diametro de la pupila optica circular.

    Coordenadas polares:
        rho   = sqrt(X_c^2 + Y_c^2)          # distancia al centro
        theta = arctan2(Y_c, X_c)             # angulo (solo informativo)

    Condicion de filtrado:
        rho <= R_pupila  ->  punto DENTRO de la pupila
        rho >  R_pupila  ->  punto FUERA  de la pupila

    Los puntos dentro se normalizan al circulo unitario dividiendo
    entre R_pupila para que sean compatibles con el algoritmo de Zernike.

    Parametros
    ----------
    X_c, Y_c : ndarray (K,)  -- coordenadas centradas (pixeles)
    Z        : ndarray (K,)  -- valores de superficie
    diametro : float         -- diametro de la pupila en pixeles

    Retorna dict con:
        rho    : ndarray (K,)     -- distancias al centro (todos los puntos)
        theta  : ndarray (K,)     -- angulos en radianes  (todos los puntos)
        mascara: ndarray bool (K,)-- True si esta dentro de la pupila
        X_norm : ndarray (K_in,)  -- X de puntos dentro, normalizados [-1,1]
        Y_norm : ndarray (K_in,)  -- Y de puntos dentro, normalizados [-1,1]
        Z_norm : ndarray (K_in,)  -- Z de puntos dentro, normalizados [-1,1]
        R      : float            -- radio de la pupila en pixeles
    """
    R = diametro / 2.0

    rho   = np.sqrt(X_c**2 + Y_c**2)
    theta = np.arctan2(Y_c, X_c)

    mascara = rho <= R

    X_dentro = X_c[mascara]
    Y_dentro = Y_c[mascara]
    Z_dentro = Z[mascara]

    # Normalizar al circulo unitario dividiendo entre R
    X_norm = X_dentro / R
    Y_norm = Y_dentro / R
    Z_norm = normalizar_vector(Z_dentro)

    n_total  = len(X_c)
    n_dentro = int(np.sum(mascara))
    n_fuera  = n_total - n_dentro

    print(f"\n  Total de pixeles : {n_total}")
    print(f"  Dentro de pupila : {n_dentro}  ({100*n_dentro/n_total:.1f}%)")
    print(f"  Fuera de pupila  : {n_fuera}   ({100*n_fuera/n_total:.1f}%)")

    return {
        'rho':    rho,
        'theta':  theta,
        'mascara': mascara,
        'X_norm': X_norm,
        'Y_norm': Y_norm,
        'Z_norm': Z_norm,
        'R':      R,
    }


def parsear_ecuacion_z(expr_str: str):
    """
    Convierte una cadena de texto que contiene una formula matematica en x, y
    en una funcion ejecutable (callable) de Python.
    Permite el uso de numpy (como np.sin, np.cos, np.sqrt, np.exp, etc.).
    """
    expr_str = expr_str.strip()
    if not expr_str:
        return None

    # Entorno seguro de evaluacion con funciones matematicas usuales de numpy
    safe_dict = {
        'x': None,
        'y': None,
        'np': np,
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'sqrt': np.sqrt,
        'exp': np.exp,
        'log': np.log,
        'pi': np.pi,
        'abs': np.abs,
    }

    # Permitir la notacion '^' reemplazandola por '**'
    expr_eval = expr_str.replace('^', '**')

    # Retorna una funcion ejecutable
    def func(x, y):
        context = safe_dict.copy()
        context['x'] = x
        context['y'] = y
        try:
            return eval(expr_eval, {"__builtins__": None}, context)
        except Exception as e:
            raise ValueError(f"Error al evaluar la ecuacion '{expr_str}': {e}")

    return func
