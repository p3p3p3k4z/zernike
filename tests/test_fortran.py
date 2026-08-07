"""
tests/test_fortran.py
======================
Pruebas unitarias para el modulo ejecutor y compilador multiplataforma de Fortran.
"""

import os
import sys
import pytest
import numpy as np

from lib.fortran_runner import (
    obtener_nombre_binario, verificar_gfortran,
    preparar_datos_entrada_dat, asegurar_binario_fortran,
    ejecutar_zernike_fortran
)


def test_obtener_nombre_binario():
    bin_name = obtener_nombre_binario()
    if sys.platform == "win32":
        assert bin_name == "zernike_app.exe"
    else:
        assert bin_name == "zernike_app"


def test_preparar_datos_entrada_dat(tmp_path):
    x = np.array([0.1, 0.2, 0.3])
    y = np.array([0.4, 0.5, 0.6])
    w = np.array([1.0, 1.1, 1.2])

    target = str(tmp_path / "datos_entrada.dat")
    preparar_datos_entrada_dat(x, y, w, target)

    assert os.path.exists(target)
    with open(target, 'r') as f:
        lines = f.readlines()

    assert len(lines) == 4
    assert lines[-1].strip() == "10000.0 0.0 0.0"


def test_ejecutar_zernike_fortran_si_gfortran_disponible():
    gfortran_path = verificar_gfortran()
    if not gfortran_path:
        pytest.skip("gfortran no está instalado en este sistema.")

    ok, msg = asegurar_binario_fortran()
    assert ok is True

    # Generar 50 puntos de datos de prueba (onda simple)
    np.random.seed(42)
    x = np.linspace(-0.8, 0.8, 50)
    y = np.linspace(-0.8, 0.8, 50)
    xx, yy = np.meshgrid(x, y)
    mask = (xx**2 + yy**2) <= 0.64
    X_in = xx[mask]
    Y_in = yy[mask]
    W_in = X_in**2 + Y_in**2

    res = ejecutar_zernike_fortran(X_in, Y_in, W_in)

    assert res is not None
    assert hasattr(res, 'A')
    assert len(res.A) == 21
    assert len(res.W_fit) == len(X_in)
