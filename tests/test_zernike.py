"""Pruebas unitarias para el motor matemático central de Zernike (lib/zernike.py)."""

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
    """Verifica que la base de Zernike cargue exactamente 21 polinomios para grado k=5."""
    polinomios = polinomios_zernike()
    assert len(polinomios) == 21


def test_resultado_zernike_structure():
    """Valida la inmutabilidad y el doble acceso (atributo y clave) de la NamedTuple ResultadoZernike."""
    dummy_vec = np.zeros(21)
    
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

    assert res.A is dummy_vec
    assert res.D.shape == (21, 21)

    assert res['A'] is dummy_vec
    assert res['D'].shape == (21, 21)

    with pytest.raises(KeyError):
        _ = res['CLAVE_QUE_NO_EXISTE']


def test_ajuste_completo_sintetico():
    """Prueba el flujo completo de ajuste de Zernike sobre una superficie suave aleatoria."""
    X, Y, W = generar_datos_circulo(N=100, semilla=42)
    polinomios = polinomios_zernike()
    k = 5

    res = ajuste_completo(X, Y, W, polinomios, k)

    assert isinstance(res, ResultadoZernike)
    assert len(res.A) == 21
    assert verificar_ortogonalidad(res.V) is True
    assert verificar_formulas(res) is True

    error_rms = np.sqrt(np.mean((W - res.W_fit) ** 2))
    assert error_rms < 1e-2


def test_ajuste_completo_polinomio_complejo():
    """Prueba la reconstrucción exacta de una superficie polinómica de 3er orden por la base de Zernike."""
    expr = "-y - 1.5*y*y*y + 1.5*x*x*y + x*y*y - 0.33*x*x*x + 2*x*x + 2*y*y + 0.5*x - 1"
    func = parsear_ecuacion_z(expr)

    X, Y, W = generar_datos_circulo(N=120, semilla=123, func_z=func)
    polinomios = polinomios_zernike()
    k = 5

    res = ajuste_completo(X, Y, W, polinomios, k)

    error_rms = np.sqrt(np.mean((W - res.W_fit) ** 2))
    assert error_rms < 1e-5
    assert verificar_ortogonalidad(res.V) is True
    assert verificar_formulas(res) is True
