"""
lib/ — Libreria de Polinomios Ortogonales de Zernike (ISO 10110-5)

Modulos:
  zernike       → Motor matematico: evaluacion, Gram-Schmidt, coeficientes, polinomios
  matriz        → Generacion e impresion de matrices de datos
  visualizacion → Animacion del flujo recursivo con matplotlib
"""

from .zernike import (
    polinomios_zernike,
    evaluar_polinomios,
    construir_base_ortogonal,
    calcular_B,
    calcular_C,
    calcular_A,
    reconstruir_W,
    ajuste_completo,
    verificar_ortogonalidad,
    verificar_formulas,
)

from .matriz import (
    normalizar_vector,
    generar_datos_circulo,
    matriz3d_cuadrante,
    imprimir_matriz_n_puntos,
    imprimir_matriz_D,
    imprimir_vectores_V,
    imprimir_matriz_C,
)

from .visualizacion import (
    graficar_flujo_zernike,
)

__all__ = [
    # zernike
    "polinomios_zernike",
    "evaluar_polinomios",
    "construir_base_ortogonal",
    "calcular_B",
    "calcular_C",
    "calcular_A",
    "reconstruir_W",
    "ajuste_completo",
    "verificar_ortogonalidad",
    "verificar_formulas",
    # matriz
    "normalizar_vector",
    "generar_datos_circulo",
    "matriz3d_cuadrante",
    "imprimir_matriz_n_puntos",
    "imprimir_matriz_D",
    "imprimir_vectores_V",
    "imprimir_matriz_C",
    # visualizacion
    "graficar_flujo_zernike",
]
