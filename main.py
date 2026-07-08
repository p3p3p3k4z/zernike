"""
Programa principal de pruebas para la libreria de polinomios
ortogonales de Zernike

Estructura:
  1. Generacion de matrices por cuadrante  (lib.matriz)
  2. Normalizacion e impresion de matrices
  3. Generacion de datos en el circulo unitario
  4. Flujo completo de Zernike             (lib.zernike)
  5. Verificacion de ortogonalidad y formulas
  6. Reporte de coeficientes A y error RMS
  7. Animacion del flujo recursivo         (lib.visualizacion)
"""

import numpy as np
import matplotlib.pyplot as plt

from lib.zernike import (
    polinomios_zernike,
    ajuste_completo,
    verificar_ortogonalidad,
    verificar_formulas,
)
from lib.matriz import (
    normalizar_vector,
    generar_datos_circulo,
    matriz3d_cuadrante,
    imprimir_matriz_n_puntos,
    imprimir_matriz_D,
    imprimir_vectores_V,
    imprimir_matriz_C,
    poli_zenike_print,
)
from lib.visualizacion import graficar_flujo_zernike


def seccion_matrices():
    print("\n" + "="*60)
    print("  Matrices de datos por cuadrante")
    print("  Superficie de prueba: Z = 3xy + 2x")
    print("="*60)

    # Cuadrante I  (x+, y+)
    X1, Y1, Z1 = matriz3d_cuadrante(1, 5, 1, 10)
    # Cuadrante II (x-, y+)
    X2, Y2, Z2 = matriz3d_cuadrante(-5, -1, 1, 10)
    # Cuadrante III (x-, y-)
    X3, Y3, Z3 = matriz3d_cuadrante(-5, -1, -10, -1)
    # Cuadrante IV (x+, y-)
    X4, Y4, Z4 = matriz3d_cuadrante(1, 5, -10, -1)

    imprimir_matriz_n_puntos(X1, Y1, Z1, "MATRIZ 1: CUADRANTE I")
    #imprimir_matriz_n_puntos(X2, Y2, Z2, "MATRIZ 2: CUADRANTE II")
    #imprimir_matriz_n_puntos(X3, Y3, Z3, "MATRIZ 3: CUADRANTE III")
    #imprimir_matriz_n_puntos(X4, Y4, Z4, "MATRIZ 4: CUADRANTE IV")

    print("\n--- Normalizacion (x / max|x|) ---")
    X1_n = normalizar_vector(X1)
    Y1_n = normalizar_vector(Y1)
    Z1_n = normalizar_vector(Z1)
    
    #X2_n = normalizar_vector(X2)
    #Y2_n = normalizar_vector(Y2)
    #Z2_n = normalizar_vector(Z2)
    
    #X3_n = normalizar_vector(X3)
    #Y3_n = normalizar_vector(Y3)
    #Z3_n = normalizar_vector(Z3)
    
    #X4_n = normalizar_vector(X4)
    #Y4_n = normalizar_vector(Y4)
    #Z4_n = normalizar_vector(Z4)

    imprimir_matriz_n_puntos(X1_n, Y1_n, Z1_n, "MATRIZ 1 NORMALIZADA: CUADRANTE I")
    #imprimir_matriz_n_puntos(X2_n, Y2_n, Z2_n, "MATRIZ 2 NORMALIZADA: CUADRANTE II")
    #imprimir_matriz_n_puntos(X3_n, Y3_n, Z3_n, "MATRIZ 3 NORMALIZADA: CUADRANTE III")
    #imprimir_matriz_n_puntos(X4_n, Y4_n, Z4_n, "MATRIZ 4 NORMALIZADA: CUADRANTE IV")

    return X1_n, Y1_n, Z1_n


def seccion_zernike(X_n, Y_n, W_n, nombre_flujo="Cuadrante I"):
    print("\n" + "="*60)
    print("  Flujo de ajuste de Zernike")
    print(f"  Datos: {nombre_flujo}")
    print("  Grado polinomial: k = 5  (L = 21 polinomios)")
    print("="*60)

    # Generar datos en el circulo unitario
    # N = 50
    # X, Y, W = generar_datos_circulo(N, semilla=42)
    
    N = len(X_n)
    print(f"\nPuntos generados: {N}")
    print(f"  X en [{X_n.min():.4f}, {X_n.max():.4f}]")
    print(f"  Y en [{Y_n.min():.4f}, {Y_n.max():.4f}]")
    print(f"  W en [{W_n.min():.4f}, {W_n.max():.4f}]")

    # Polinomios de Zernike (k=5, L=21)
    polinomios = polinomios_zernike()
    k = 5
    L = (k + 1) * (k + 2) // 2
    print(f"\nBase de Zernike: {L} polinomios (grado k={k})")

    resultados = ajuste_completo(X_n, Y_n, W_n, polinomios, k)

    poli_zenike_print(X_n, Y_n, polinomios, n_rows=N)

    imprimir_matriz_D(resultados['D'])
    imprimir_vectores_V(resultados['V'], n_puntos=N)
    imprimir_matriz_C(resultados['C'])

    verificar_ortogonalidad(resultados['V'])
    verificar_formulas(resultados)

    print("\n--- Coeficientes de Zernike A ---")
    A = resultados['A']
    for r in range(L):
        print(f"  A_{r+1:2d} = {A[r]:+.6f}")

    # ---- Error RMS ----
    error = W_n - resultados['W_fit']
    rms = np.sqrt(np.mean(error**2))
    print(f"\nError RMS del ajuste: {rms:.2e}")

    return resultados, X_n, Y_n, W_n


def seccion_animacion(resultados):
    print("\n" + "="*60)
    print("  Animacion Recursiva")
    print("="*60)

    fig, anim = graficar_flujo_zernike(resultados, intervalo_ms=800, repetir=True)
    plt.show()


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("  LIBRERIA DE POLINOMIOS ORTOGONALES DE ZERNIKE")
    print("  ISO 10110 |  Grado k=5  |  L=21 polinomios")
    print("#"*60)

    FLUJO = "CIRCULO" 
#    FLUJO = "CUADRANTE"
    
    if FLUJO == "CUADRANTE":
        X1_n, Y1_n, Z1_n = seccion_matrices()
        resultados, X, Y, W_n = seccion_zernike(X1_n, Y1_n, Z1_n, "Cuadrante I")
    else:
        print("\n" + "="*60)
        print("  Generando datos en el Círculo Unitario Completo")
        print("="*60)
        N = 50
        X_c, Y_c, Z_c = generar_datos_circulo(N, semilla=42)
        
        # W (Z) se normaliza. X e Y ya están en [-1, 1] porque el radio rho <= 1
        Z_c_n = normalizar_vector(Z_c)
        imprimir_matriz_n_puntos(X_c, Y_c, Z_c_n, "MATRIZ: CIRCULO UNITARIO")
        
        resultados, X, Y, W_n = seccion_zernike(X_c, Y_c, Z_c_n, "Círculo Unitario")

    seccion_animacion(resultados)

"""
============================================================
  NOTA SOBRE FALLOS DE VALIDACION (DOMINIO ASIMETRICO):
  Al evaluar en un solo cuadrante, los polinomios pierden simetria
  circular y se vuelven matematicamente casi colineales. Esto causa
  una 'Cancelacion Catastrofica' en la precision de la computadora.
  Los fallos mostrados anteriormente (ortogonalidad, V_r y W_fit)
  no son errores de codigo, sino desbordamientos de precision por
  forzar a Zernike fuera del circulo unitario completo.
============================================================
"""
