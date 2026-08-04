"""
lib/ — Libreria de Polinomios Ortogonales de Zernike (ISO 10110-5)

Modulos:
  zernike       → Motor matematico: evaluacion, Gram-Schmidt, coeficientes, polinomios
  matriz        → Generacion e impresion de matrices de datos
  visualizacion → Animacion del flujo recursivo con matplotlib
"""

from .zernike import (
    ResultadoZernike,
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
    parsear_ecuacion_z,
    descomponer_aberraciones,
)

from .visualizacion import (
    graficar_flujo_zernike,
    mapa_fase_3d,
)

from .io import (
    inicializar_logger,
    exportar_resultados_csv,
    cargar_datos_csv,
    exportar_datos_iniciales_csv,
    exportar_zemax,
    exportar_codev,
)

__all__ = [
    # zernike
    "ResultadoZernike",
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
    "parsear_ecuacion_z",
    "descomponer_aberraciones",
    # visualizacion
    "graficar_flujo_zernike",
    "mapa_fase_3d",
    # io
    "inicializar_logger",
    "exportar_resultados_csv",
    "cargar_datos_csv",
    "exportar_datos_iniciales_csv",
    "exportar_zemax",
    "exportar_codev",
]
