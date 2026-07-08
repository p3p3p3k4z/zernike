"""
lib/matriz.py
=============
Funciones para generacion, normalizacion e impresion de matrices
de datos de superficie optica.

Fuente: poliOrtogonal.ipynb (Cuaderno de Jupyter del proyecto)
"""

import numpy as np
import pandas as pd


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


def generar_datos_circulo(N=50, semilla=42):
    """
    Genera N puntos aleatorios dentro del circulo unitario con
    densidad uniforme en area, y calcula Z = 3xy + 2x.

    Por que sqrt(random)?
    La distribucion radial uniforme en area requiere rho ~ sqrt(U)
    donde U ~ Uniform(0,1). Esto garantiza que los puntos no se
    acumulen en el centro sino que se distribuyan uniformemente.

    Parametros
    ----------
    N      : int  -- numero de puntos (defecto 50)
    semilla: int  -- semilla para reproducibilidad

    Retorna
    -------
    X, Y, Z : ndarray (N,) -- coordenadas y valores de superficie
    """
    np.random.seed(semilla)
    rho   = np.sqrt(np.random.rand(N))
    theta = 2 * np.pi * np.random.rand(N)
    X = rho * np.cos(theta)
    Y = rho * np.sin(theta)
    Z = 3 * X * Y + 2 * X
    return X, Y, Z


def matriz3d_cuadrante(x_start, x_end, y_start, y_end, n_x=5, n_y=10):
    """
    Genera una malla cartesiana de puntos en el cuadrante definido
    por [x_start, x_end] x [y_start, y_end] y calcula Z = 3xy + 2x.

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

    Retorna
    -------
    X_flat, Y_flat, Z_flat : ndarray (N,) donde N = n_x * n_y
    """
    x_vals = np.linspace(x_start, x_end, n_x).astype(int)
    y_vals = np.linspace(y_start, y_end, n_y).astype(int)

    xv, yv   = np.meshgrid(x_vals, y_vals)
    x_flat   = xv.flatten()
    y_flat   = yv.flatten()
    z_flat   = (3 * x_flat * y_flat + 2 * x_flat).astype(int)

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
