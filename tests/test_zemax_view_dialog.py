"""
tests/test_zemax_view_dialog.py
================================
Prueba unitaria para verificar la ventana de análisis estilo Zemax OpticStudio (ZemaxViewDialog).
"""

import pytest
import numpy as np
from PySide6.QtWidgets import QApplication

from gui.zemax_view_dialog import ZemaxViewDialog
from lib.zernike import ResultadoZernike


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_zemax_view_dialog_instantiation(qapp):
    """
    Verifica que ZemaxViewDialog se cree correctamente sin datos iniciales.
    """
    dialog = ZemaxViewDialog(resultado_zernike=None, parent=None)
    assert dialog is not None
    assert dialog.windowTitle() == "Zernike Polynomials — Vista Modo Zemax OpticStudio"
    assert dialog.txt_irregularity.text() == "0.000"
    assert dialog.txt_power.text() == "0.000"
    assert dialog.txt_rms.text() == "0.000"
    dialog.close()


def test_zemax_view_dialog_poblado_y_edicion(qapp):
    """
    Verifica que al pasar un ResultadoZernike los campos se pueblen correctamente y que la modificación manual actualice las métricas de Quick Fit.
    """
    A_mock = np.zeros(21)
    A_mock[0] = 1.59   # Piston
    A_mock[1] = 0.265  # X Tilt
    A_mock[2] = -2.77  # Y Tilt
    A_mock[4] = 1.055  # Focus
    A_mock[12] = 0.01  # Spherical (r=13)

    x = np.linspace(-1, 1, 100)
    y = np.linspace(-1, 1, 100)
    res_mock = ResultadoZernike(
        U=np.array([]), V=[], D=np.array([]), F=None,
        B=np.array([]), C=np.array([]),
        A=A_mock, W_fit=np.array([]), X=x, Y=y, W=np.ones(100)
    )

    dialog = ZemaxViewDialog(resultado_zernike=res_mock, parent=None)

    assert dialog.txt_piston.value() == pytest.approx(1.59, abs=1e-3)
    assert dialog.txt_xtilt.value() == pytest.approx(0.265, abs=1e-3)
    assert dialog.txt_ytilt.value() == pytest.approx(-2.77, abs=1e-3)
    assert dialog.txt_focus.value() == pytest.approx(1.055, abs=1e-3)
    assert dialog.txt_power.text() == "1.055"

    # Editar un coeficiente manualmente
    dialog.dict_spins_matriz[6].setValue(0.5) # Astig 0° r=6
    assert dialog.coeficientes[5] == 0.5
    assert float(dialog.txt_rms.text()) > 0.0

    # Probar cambios en términos (Set Order)
    dialog.spin_terms.setValue(9)
    assert dialog.spin_terms.value() == 9

    # Limpiar coeficientes
    dialog._limpiar_coeficientes()
    assert dialog.txt_power.text() == "0.000"
    assert dialog.txt_rms.text() == "0.000"

    dialog.close()


def test_todos_los_coeficientes_coinciden_exactamente_con_matriz_zemax(qapp):
    """
    Verifica que los 21 coeficientes Zernike coincidan 1:1 entre el ResultadoZernike
    y los spins de la matriz de ZemaxViewDialog redondeados a 4 decimales.
    """
    np.random.seed(42)
    A_aleatorios = np.random.uniform(-5.0, 5.0, 21)

    res_mock = ResultadoZernike(
        U=np.array([]), V=[], D=np.array([]), F=None,
        B=np.array([]), C=np.array([]),
        A=A_aleatorios, W_fit=np.array([]), X=np.array([0]), Y=np.array([0]), W=np.array([1.0])
    )

    dialog = ZemaxViewDialog(resultado_zernike=res_mock, parent=None)

    # Verificar los 4 términos de la barra superior
    assert dialog.txt_piston.value() == pytest.approx(round(A_aleatorios[0], 4), abs=1e-4)
    assert dialog.txt_xtilt.value() == pytest.approx(round(A_aleatorios[1], 4), abs=1e-4)
    assert dialog.txt_ytilt.value() == pytest.approx(round(A_aleatorios[2], 4), abs=1e-4)
    assert dialog.txt_focus.value() == pytest.approx(round(A_aleatorios[4], 4), abs=1e-4)

    # Verificar los 17 términos de la matriz cuadrícula
    for r_idx, spin in dialog.dict_spins_matriz.items():
        val_spin = spin.value()
        val_esperado = round(A_aleatorios[r_idx - 1], 4)
        assert val_spin == pytest.approx(val_esperado, abs=1e-4), f"Desfase en coeficiente Zernike A_{r_idx}"

    dialog.close()


