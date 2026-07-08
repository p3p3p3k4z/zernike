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
    generar_malla_ccd,
    centrar_coordenadas,
    filtrar_pupila,
    imprimir_matriz_n_puntos,
    imprimir_matriz_D,
    imprimir_vectores_V,
    imprimir_matriz_C,
    poli_zenike_print,
)
from lib.visualizacion import (
    graficar_flujo_zernike,
    graficar_distribucion_ccd,
    graficar_pupila,
)


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


def seccion_ccd():
    """
    Flujo CCD: genera los 4 cuadrantes con matriz3d_cuadrante,
    los une, aplica el filtro de pupila circular y lanza el ajuste
    de Zernike con los puntos que quedan dentro.
    """
    print("\n" + "="*60)
    print("  Flujo CCD: Sensor + Pupila Optica")
    print("="*60)

    print("\n  Generando los 4 cuadrantes...")
    X1, Y1, Z1 = matriz3d_cuadrante(1,  5,  1,  10)
    X2, Y2, Z2 = matriz3d_cuadrante(-5, -1,  1,  10)
    X3, Y3, Z3 = matriz3d_cuadrante(-5, -1, -10, -1)
    X4, Y4, Z4 = matriz3d_cuadrante(1,  5, -10, -1)

    X_all = np.concatenate([X1, X2, X3, X4]).astype(float)
    Y_all = np.concatenate([Y1, Y2, Y3, Y4]).astype(float)
    Z_all = np.concatenate([Z1, Z2, Z3, Z4]).astype(float)

    print(f"  Total de puntos: {len(X_all)}")
    print(f"  X en [{X_all.min():.1f}, {X_all.max():.1f}]")
    print(f"  Y en [{Y_all.min():.1f}, {Y_all.max():.1f}]")

    r_max = np.sqrt(X_all**2 + Y_all**2).max()
    diametro = float(input(
        f"\n  Radio maximo de los datos: {r_max:.1f}\n"
        f"  Ingresa el diametro de la pupila: "
    ))

    print("\n" + "-"*40)
    datos_pupila = filtrar_pupila(X_all, Y_all, Z_all, diametro)

    if datos_pupila['mascara'].sum() == 0:
        print("  ERROR: Ningun punto quedo dentro de la pupila.")
        print("  Usa un diametro mayor.")
        return None

    graficar_distribucion_ccd(X_all, Y_all)
    graficar_pupila(X_all, Y_all, datos_pupila['mascara'], datos_pupila['R'])
    plt.show(block=False)
    plt.pause(0.1)
    return seccion_zernike(
        datos_pupila['X_norm'],
        datos_pupila['Y_norm'],
        datos_pupila['Z_norm'],
        nombre_flujo="CCD — Puntos dentro de la pupila",
    )

def seccion_ccd_sensor():
    """
    Flujo CCD Sensor: el usuario define el tamano fisico del sensor
    (N filas x M columnas) y el diametro de la pupila. Se genera una
    malla regular de N*M puntos que simula los pixeles del detector,
    se centra al origen optico y se filtra por el circulo de la pupila.

    Diferencia con seccion_ccd():
      - seccion_ccd()        usa los puntos fijos de los 4 cuadrantes
      - seccion_ccd_sensor() genera una malla a partir de N, M ingresados
    """
    print("\n" + "="*60)
    print("  Flujo CCD Sensor: Malla generada por parametros")
    print("="*60)

    print("\n  Ingresa las dimensiones del sensor:")
    N = int(input("    Numero de filas  (N): "))
    M = int(input("    Numero de columnas (M): "))
    diametro = float(input(
        f"\n  Diametro maximo posible: {min(N, M):.0f} px\n"
        f"  Ingresa el diametro de la pupila: "
    ))

    print("\n" + "-"*40)
    print(f"  Generando malla de {N} x {M} = {N*M} pixeles...")
    X_pixel, Y_pixel, Z_raw = generar_malla_ccd(N, M)
    X_c, Y_c = centrar_coordenadas(X_pixel, Y_pixel, N, M)
    
    print(f"  Centro optico en (0, 0)")
    print(f"  X en [{X_c.min():.1f}, {X_c.max():.1f}]")
    print(f"  Y en [{Y_c.min():.1f}, {Y_c.max():.1f}]")

    print("\n" + "-"*40)
    datos_pupila = filtrar_pupila(X_c, Y_c, Z_raw, diametro)

    if datos_pupila['mascara'].sum() == 0:
        print("  ERROR: Ningun punto quedo dentro de la pupila.")
        print("  Usa un diametro mayor o un sensor mas grande.")
        return None

    graficar_distribucion_ccd(X_c, Y_c)
    graficar_pupila(X_c, Y_c, datos_pupila['mascara'], datos_pupila['R'])
    plt.show(block=False)
    plt.pause(0.1)

    return seccion_zernike(
        datos_pupila['X_norm'],
        datos_pupila['Y_norm'],
        datos_pupila['Z_norm'],
        nombre_flujo=f"CCD Sensor {N}x{M} — Pupila d={diametro:.0f}px",
    )


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("  LIBRERIA DE POLINOMIOS ORTOGONALES DE ZERNIKE")
    print("  ISO 10110 |  Grado k=5  |  L=21 polinomios")
    print("#"*60)

    # Selecciona el flujo:
    #   "CCD"        -> 4 cuadrantes fijos + filtro de pupila
    #   "CCD_SENSOR" -> malla N x M generada por parametros + filtro de pupila
    #   "CIRCULO"    -> circulo unitario aleatorio
    #   "CUADRANTE"  -> cuadrante I (genera cancelacion catastrofica)
    FLUJO = "CCD_SENSOR"

    if FLUJO == "CUADRANTE":
        X1_n, Y1_n, Z1_n = seccion_matrices()
        resultados, X, Y, W_n = seccion_zernike(X1_n, Y1_n, Z1_n, "Cuadrante I")
        seccion_animacion(resultados)

    elif FLUJO == "CIRCULO":
        print("\n" + "="*60)
        print("  Generando datos en el Circulo Unitario Completo")
        print("="*60)
        N = 50
        X_c, Y_c, Z_c = generar_datos_circulo(N, semilla=42)
        Z_c_n = normalizar_vector(Z_c)
        imprimir_matriz_n_puntos(X_c, Y_c, Z_c_n, "MATRIZ: CIRCULO UNITARIO")
        resultados, X, Y, W_n = seccion_zernike(X_c, Y_c, Z_c_n, "Circulo Unitario")
        seccion_animacion(resultados)

    elif FLUJO == "CCD":
        resultado_ccd = seccion_ccd()
        if resultado_ccd is not None:
            resultados, *_ = resultado_ccd
            seccion_animacion(resultados)

    elif FLUJO == "CCD_SENSOR":
        resultado_ccd = seccion_ccd_sensor()
        if resultado_ccd is not None:
            resultados, *_ = resultado_ccd
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
