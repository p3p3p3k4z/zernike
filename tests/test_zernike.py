"""
===============================================================================
MÓDULO DE PRUEBAS UNITARIAS: lib.zernike
===============================================================================
Este archivo evalúa el motor matemático central de los Polinomios Ortogonales 
de Zernike (`lib/zernike.py`), incluyendo:
1. Conteo e integridad de la base polinomial.
2. Estructura de resultados inmutable (`ResultadoZernike`).
3. Algoritmo de ortogonalización de Gram-Schmidt.
4. Cumplimiento de identidades algebraicas según la norma ISO 10110-5.
5. Ajuste completo sobre superficies complejas de 3er orden.
===============================================================================
"""

import pytest
import numpy as np
from lib.zernike import (
    polinomios_zernike,
    ajuste_completo,
    verificar_ortogonalidad,
    verificar_formulas,
    ResultadoZernike,
)
from lib.matriz import generar_datos_circulo, parsear_ecuacion_z


def test_polinomios_zernike_count():
    """
    OBJETIVO: Verificar que la base de Zernike cargue la cantidad exacta de polinomios.
    
    ¿CÓMO FUNCIONA LA MATEMÁTICA?
    Para un grado máximo k=5, la cantidad total de polinomios de Zernike (L) 
    viene dada por la fórmula triangular:
        L = (k + 1) * (k + 2) / 2
        L = (5 + 1) * (5 + 2) / 2 = (6 * 7) / 2 = 21 polinomios.
    """
    polinomios = polinomios_zernike()
    assert len(polinomios) == 21


def test_resultado_zernike_structure():
    """
    OBJETIVO: Validar la estructura de datos `ResultadoZernike` (NamedTuple).
    
    ¿QUÉ PROBAMOS AQUÍ?
    Que la estructura sea inmutable pero permita DOS formas de acceso a los datos:
    1. Acceso orientado a objetos: `resultado.A`
    2. Acceso orientado a diccionario (retrocompatibilidad): `resultado['A']`
    Y que intentar acceder a una clave inexistente dispare un `KeyError`.
    """
    dummy_vec = np.zeros(21)
    
    # Instanciamos la NamedTuple con sus 11 campos requeridos
    res = ResultadoZernike(
        U=np.zeros((21, 5)),
        X=np.zeros(5),
        Y=np.zeros(5),
        D=np.eye(21),
        F=dummy_vec,
        V=[dummy_vec],
        B=dummy_vec,
        C=np.eye(21),
        A=dummy_vec,
        W_fit=dummy_vec,
        W=dummy_vec,
    )

    # 1. Validación de acceso por Atributo
    assert res.A is dummy_vec
    assert res.D.shape == (21, 21)

    # 2. Validación de acceso tipo Diccionario
    assert res['A'] is dummy_vec
    assert res['D'].shape == (21, 21)

    # 3. Validación de manejo de errores (clave no válida)
    with pytest.raises(KeyError):
        _ = res['CLAVE_QUE_NO_EXISTE']


def test_ajuste_completo_sintetico():
    """
    OBJETIVO: Probar el flujo completo de ajuste de Zernike sobre una superficie suave aleatoria.
    
    PASOS DEL TEST:
    1. Generar 100 puntos en el círculo unitario.
    2. Ejecutar `ajuste_completo`.
    3. Comprobar la ortogonalidad estricta de la base calculada V.
    4. Comprobar que todas las relaciones de Gram-Schmidt (matriz D, C, etc.) se cumplan.
    5. Asegurar que el error RMS global sea menor a 1e-2.
    """
    # 1. Generar datos sintéticos en el círculo
    X, Y, W = generar_datos_circulo(N=100, semilla=42)
    polinomios = polinomios_zernike()
    k = 5

    # 2. Invocación del motor matemático
    res = ajuste_completo(X, Y, W, polinomios, k)

    # 3. Verificaciones de integridad
    assert isinstance(res, ResultadoZernike)
    assert len(res.A) == 21

    # 4. Ortogonalidad de los vectores V (<V_i, V_j> = 0 para i != j)
    assert verificar_ortogonalidad(res.V) is True

    # 5. Verificación cruzada de fórmulas ISO (retorna True si todas pasan)
    assert verificar_formulas(res) is True

    # 6. Error RMS del ajuste (raíz del error cuadrático medio)
    error_rms = np.sqrt(np.mean((W - res.W_fit) ** 2))
    assert error_rms < 1e-2


def test_ajuste_completo_polinomio_complejo():
    """
    OBJETIVO: Probar el ajuste con la ecuación polinómica de 3er orden especificada:
    Z = -y - 1.5*y^3 + 1.5*x^2*y + x*y^2 - 0.33*x^3 + 2*x^2 + 2*y^2 + 0.5*x - 1
    
    ¿POR QUÉ ESTA PRUEBA ES CRUCIAL?
    Como esta superficie es una combinación exacta de términos de grado <= 3, 
    nuestra base de Zernike (que llega hasta grado k=5) DEBE ser capaz de 
    reconstruirla casi PERFECTAMENTE.
    
    Por lo tanto, esperamos que el Error RMS sea prácticamente cero (< 1e-5).
    """
    # 1. Construir la funcion matematica desde la cadena
    expr = "-y - 1.5*y*y*y + 1.5*x*x*y + x*y*y - 0.33*x*x*x + 2*x*x + 2*y*y + 0.5*x - 1"
    func = parsear_ecuacion_z(expr)

    # 2. Evaluar 120 puntos dentro del círculo unitario
    X, Y, W = generar_datos_circulo(N=120, semilla=123, func_z=func)
    polinomios = polinomios_zernike()
    k = 5

    # 3. Reconstruir la superficie con Zernike
    res = ajuste_completo(X, Y, W, polinomios, k)

    # 4. Comprobacion: El error cuadrático medio debe ser mínimo (< 1e-5)
    error_rms = np.sqrt(np.mean((W - res.W_fit) ** 2))
    assert error_rms < 1e-5

    # 5. Comprobar ortogonalidad y consistencia matemática de nuevo
    assert verificar_ortogonalidad(res.V) is True
    assert verificar_formulas(res) is True
