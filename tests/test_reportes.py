"""
Pruebas Unitarias para el Módulo de Generación de Reportes Metrológicos (lib/reportes.py)
"""

import os
import tempfile
import numpy as np
import pytest

from lib.zernike import ResultadoZernike
from lib.reportes import generar_html_reporte, exportar_reporte_html


@pytest.fixture
def resultado_mock():
    """Genera un objeto ResultadoZernike sintético para pruebas de reportes."""
    N = 40
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)
    X_flat = X.ravel()
    Y_flat = Y.ravel()

    # Coeficientes sintéticos: Defoco (A5=0.25) y Astigmatismo (A6=0.15)
    A = np.zeros(21)
    A[4] = 0.25
    A[5] = 0.15

    W_fit = A[4] * (2 * (X_flat**2 + Y_flat**2) - 1) + A[5] * (X_flat**2 - Y_flat**2)
    W_exp = W_fit + np.random.normal(0, 0.02, size=len(W_fit))

    return ResultadoZernike(
        U=np.array([]), V=[], D=np.array([]), F=None,
        B=np.array([]), C=np.array([]),
        A=A, W_fit=W_fit, X=X_flat, Y=Y_flat, W=W_exp
    )


def test_generar_html_reporte(resultado_mock):
    """Verifica que el HTML generado contenga la estructura y metadatos ISO 10110-5 esperados."""
    html_str = generar_html_reporte(resultado_mock, titulo="Prueba Metrológica")
    assert "<!DOCTYPE html>" in html_str
    assert "ISO 10110-5 / ANSI Z80.28" in html_str
    assert "Resumen Metrológico" in html_str
    assert "data:image/png;base64," in html_str
    assert "Z<sub>5</sub>" in html_str
    assert "Defocus" in html_str


def test_exportar_reporte_html(resultado_mock):
    """Verifica la creación física del archivo HTML en disco."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "reporte_test.html")
        ok = exportar_reporte_html(resultado_mock, filepath)
        assert ok is True
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 1000


def test_reporte_con_wfit_vacio():
    """Verifica que la generación de gráficas funcione correctamente incluso si W_fit viene vacío."""
    A = np.zeros(21)
    A[4] = 0.50  # Defocus
    res_vacio = ResultadoZernike(
        U=np.array([]), V=[], D=np.array([]), F=None,
        B=np.array([]), C=np.array([]),
        A=A, W_fit=np.array([]), X=np.array([]), Y=np.array([]), W=np.array([])
    )
    html_str = generar_html_reporte(res_vacio, titulo="Prueba Vacia")
    assert "data:image/png;base64," in html_str
    assert "+0.5000 λ" in html_str
