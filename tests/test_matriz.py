"""Pruebas unitarias para las funciones de matriz y procesamiento de datos (lib/matriz.py)."""

import pytest
import numpy as np
from lib.matriz import (
    normalizar_vector,
    parsear_ecuacion_z,
    descomponer_aberraciones,
    filtrar_pupila,
    centrar_coordenadas,
)


def test_normalizar_vector():
    """Valida la normalización de vectores al rango [-1, 1] dividiendo entre el máximo absoluto."""
    v_entrada = np.array([2.0, -4.0, 1.0, 0.0])
    v_obtenido = normalizar_vector(v_entrada)
    
    assert np.max(np.abs(v_obtenido)) == 1.0
    
    v_esperado = np.array([0.5, -1.0, 0.25, 0.0])
    assert np.allclose(v_obtenido, v_esperado)

    v_ceros = np.zeros(5)
    assert np.array_equal(normalizar_vector(v_ceros), v_ceros)


def test_parsear_ecuacion_z_valid():
    """Prueba la conversión de cadenas de texto matemáticas en funciones ejecutables seguras usando AST."""
    func1 = parsear_ecuacion_z("3*x*y + 2*x")
    assert func1(1.0, 2.0) == 8.0

    func2 = parsear_ecuacion_z("sin(x) + cos(y)")
    assert np.isclose(func2(0.0, 0.0), 1.0)

    func3 = parsear_ecuacion_z("sqrt(x^2 + y^2)")
    assert np.isclose(func3(3.0, 4.0), 5.0)

    func4 = parsear_ecuacion_z("y**2 - x**2")
    assert np.isclose(func4(2.0, 3.0), 5.0)

    func5 = parsear_ecuacion_z("2*x*y")
    assert np.isclose(func5(3.0, 4.0), 24.0)

    expr6 = "-y - 1.5*y*y*y + 1.5*x*x*y + x*y*y - 0.33*x*x*x + 2*x*x + 2*y*y + 0.5*x - 1"
    func6 = parsear_ecuacion_z(expr6)
    x_test, y_test = 0.5, -0.5
    resultado_teorico = -y_test - 1.5*y_test**3 + 1.5*x_test**2*y_test + x_test*y_test**2 - 0.33*x_test**3 + 2*x_test**2 + 2*y_test**2 + 0.5*x_test - 1
    assert np.isclose(func6(x_test, y_test), resultado_teorico)


def test_parsear_ecuacion_z_invalid():
    """Verifica que el parser AST seguro rechace expresiones mal formadas o variables no autorizadas."""
    assert parsear_ecuacion_z("   ") is None

    with pytest.raises(ValueError):
        parsear_ecuacion_z("3 * x + * y")

    with pytest.raises(ValueError):
        func = parsear_ecuacion_z("x + y + z")
        func(1, 1)

    with pytest.raises(ValueError):
        func = parsear_ecuacion_z("eval('1+1')")
        func(1, 1)


def test_descomponer_aberraciones():
    """Comprueba el mapeo de coeficientes de Zernike a magnitudes de aberraciones ópticas de Seidel."""
    A = np.zeros(21)
    A[0] = 0.5
    A[1] = 1.0
    A[2] = -1.0
    A[4] = 0.75
    A[5] = 0.3
    A[12] = 0.1

    aberraciones = descomponer_aberraciones(A)

    assert aberraciones['Piston'] == 0.5
    assert aberraciones['Tilt_X'] == 1.0
    assert aberraciones['Tilt_Y'] == -1.0
    assert np.isclose(aberraciones['Tilt_Total'], np.sqrt(2.0))
    assert aberraciones['Defocus'] == 0.75
    assert aberraciones['Astigmatismo_0'] == 0.3
    assert aberraciones['Esferica_3er_orden'] == 0.1


def test_filtrar_pupila_y_centrado():
    """Valida el centrado de coordenadas al origen geométrico y el filtrado circular por pupila unitaria."""
    N, M = 10, 10
    X_pix, Y_pix = np.meshgrid(np.arange(M), np.arange(N))
    X_flat, Y_flat = X_pix.flatten(), Y_pix.flatten()
    Z_flat = X_flat + Y_flat

    X_c, Y_c = centrar_coordenadas(X_flat, Y_flat, N, M)
    
    assert np.isclose(np.mean(X_c), 0.0)
    assert np.isclose(np.mean(Y_c), 0.0)

    datos_pupila = filtrar_pupila(X_c, Y_c, Z_flat, diametro=6.0)
    
    assert datos_pupila['R'] == 3.0
    assert np.all(np.abs(datos_pupila['X_norm']) <= 1.0)
    assert np.all(np.abs(datos_pupila['Y_norm']) <= 1.0)


def test_exportar_zemax_y_codev(tmp_path):
    """Valida la generación de archivos de exportación a Zemax OpticStudio (.zrn) y CODE V (.dat)."""
    from lib.io import exportar_zemax, exportar_codev

    A_test = np.zeros(21)
    A_test[1] = 0.0267
    A_test[3] = 1.0012

    file_zemax = tmp_path / "test_zemax.zrn"
    ok_zemax = exportar_zemax(A_test, R_pupila=50.0, longitud_onda=0.6328, filepath=str(file_zemax))
    assert ok_zemax is True
    assert file_zemax.exists()

    contenido_zemax = file_zemax.read_text(encoding='utf-8')
    assert "ZEMAX OpticStudio" in contenido_zemax
    assert "PUPIL_RADIUS_MM      50.000000" in contenido_zemax
    assert "NUM_COEFFICIENTS     21" in contenido_zemax

    file_codev = tmp_path / "test_codev.dat"
    ok_codev = exportar_codev(A_test, R_pupila=50.0, filepath=str(file_codev))
    assert ok_codev is True
    assert file_codev.exists()

    contenido_codev = file_codev.read_text(encoding='utf-8')
    assert "CODE V Zernike Surface Data File" in contenido_codev
    assert "NRAD 50.000000" in contenido_codev
    assert "ZFR 21" in contenido_codev

