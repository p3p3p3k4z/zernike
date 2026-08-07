"""
Pruebas unitarias para la interfaz gráfica GUI (PySide6)
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication
from gui.main_window import ZernikeZemaxMainWindow
from gui.components import ControlBar3D
from gui.worker import ZernikeWorker


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_main_window_initialization(qapp):
    """
    Verifica que la ventana principal de Zernike OpticStudio se instancie correctamente.
    """
    window = ZernikeZemaxMainWindow()
    assert window is not None
    assert "Zernike" in window.windowTitle()
    assert window.combo_modo.count() == 4
    assert window.tabla_coef.rowCount() == 21



def test_parameter_validation(qapp):
    """
    Verifica que la validación en tiempo real deshabilite el botón e ilumine en rojo campos inválidos.
    """
    window = ZernikeZemaxMainWindow()
    panel = window.panel_parametros

    # Entrada correcta por defecto
    assert panel.btn_ejecutar.isEnabled() is True

    # Introducir N inválido (< 5)
    panel.input_N.setText("2")
    assert panel.btn_ejecutar.isEnabled() is False
    assert "border: 2px solid #EF4444" in panel.input_N.styleSheet()

    # Corregir N
    panel.input_N.setText("50")
    assert panel.btn_ejecutar.isEnabled() is True
    assert panel.input_N.styleSheet() == ""


def test_summary_tables_clipboard(qapp):
    """
    Verifica el copiado de tablas al portapapeles.
    """
    window = ZernikeZemaxMainWindow()
    tables = window.summary_tables
    tables._copiar_toda_tabla(tables.tabla_coef, "Coeficientes de Zernike")

    clipboard_text = QGuiApplication.clipboard().text()
    assert "Índice" in clipboard_text
    assert "Coeficiente A" in clipboard_text
    assert "Descripción Óptica" in clipboard_text


def test_control_bar_3d(qapp):
    """
    Verifica las señales y comportamiento de la barra de control 3D.
    """
    bar = ControlBar3D()
    angles = []
    cmaps = []

    bar.cambio_camara.connect(lambda e, a: angles.append((e, a)))
    bar.cambio_colormap.connect(lambda c: cmaps.append(c))

    bar.spin_elev.setValue(45)
    bar.spin_azim.setValue(90)
    bar.combo_cmap.setCurrentText("plasma")

    assert (45, 90) in angles
    assert "plasma" in cmaps

    bar.restablecer_vista()
    assert bar.spin_elev.value() == 30
    assert bar.spin_azim.value() == 45


def test_zernike_worker_async(qapp):
    """
    Verifica la ejecución síncrona/asíncrona del worker ZernikeWorker.
    """
    worker = ZernikeWorker(modo=0, eq_str="3*x*y + 2*x", N=20, M=20, diametro=20.0)
    finalizado = []
    worker.calculo_finalizado.connect(lambda *args: finalizado.append(args))
    
    worker.run()  # Ejecución directa del bucle del thread para pruebas
    assert len(finalizado) == 1
    resultados = finalizado[0][0]
    assert len(resultados.A) == 21


def test_colormap_change_no_typeerror(qapp):
    """
    Verifica que cambiar el colormap 3D llame correctamente a _actualizar_grafica_3d sin TypeError.
    """
    window = ZernikeZemaxMainWindow()
    worker = ZernikeWorker(modo=0, eq_str="3*x*y + 2*x", N=10, M=10, diametro=10.0)
    
    def on_done(resultados, W_in, X_in, Y_in, X_raw_all, Y_raw_all, mask_all, R_pup):
        window._al_finalizar_worker(resultados, W_in, X_in, Y_in, X_raw_all, Y_raw_all, mask_all, R_pup)

    worker.calculo_finalizado.connect(on_done)
    worker.run()

    # Probar cambiar colormap
    window._al_cambiar_colormap_3d("plasma")
    window._al_cambiar_colormap_3d("inferno")


def test_error_residual_3d_dialog(qapp):
    """
    Verifica que la ventana flotante modular ErrorResidual3DDialog se instancie con controles 3D reutilizados.
    """
    import numpy as np
    from gui.dialogs import mostrar_ventana_3d_error_residual

    x = np.linspace(-1, 1, 5)
    y = np.linspace(-1, 1, 5)
    xx, yy = np.meshgrid(x, y)
    X = xx.ravel()
    Y = yy.ravel()
    W_exp = X**2 + Y**2
    W_fit = X**2 + Y**2 * 0.9

    dialog = mostrar_ventana_3d_error_residual(X, Y, W_exp, W_fit)
    assert dialog is not None
    assert dialog.control_bar is not None
    dialog.control_bar.combo_cmap.setCurrentText("inferno")
    dialog.close()


def test_preset_manager_persistence(qapp, tmp_path):
    """
    Verifica la persistencia JSON, el almacenamiento del historial y los presets personalizados.
    """
    from gui.components.preset_manager import PresetStorage, PresetManagerDialog

    json_file = str(tmp_path / "test_presets.json")
    storage = PresetStorage(filepath=json_file)

    # 1. Agregar al historial
    storage.agregar_historial("x**2 + y**2")
    storage.agregar_historial("3*x*y")
    assert storage.data["historial"][0] == "3*x*y"
    assert storage.data["historial"][1] == "x**2 + y**2"

    # 2. Agregar personalizado
    ok = storage.agregar_personalizado("Prueba Asferica", "x**4 + y**4")
    assert ok is True
    assert storage.data["personalizados"][0]["nombre"] == "Prueba Asferica"

    # 3. Instanciar dialogo
    dialog = PresetManagerDialog(ecuacion_actual="2*x", parent=None)
    assert dialog is not None
    dialog.close()


def test_zernike_viewer_3d_dialog(qapp):
    """
    Verifica que el visor 3D de los 21 Polinomios de Zernike se instancie y navegue correctamente entre r=1 y r=21.
    """
    from gui.zernike_viewer_dialog import ZernikeViewer3DDialog

    dialog = ZernikeViewer3DDialog(resultado_zernike=None, parent=None)
    assert dialog is not None
    assert dialog.r_actual == 1

    dialog._siguiente_polinomio()
    assert dialog.r_actual == 2

    dialog._anterior_polinomio()
    assert dialog.r_actual == 1

    dialog.combo_polinomio.setCurrentIndex(4)  # r=5 Defocus
    assert dialog.r_actual == 5

    # Probar controles manuales ampliado (Escala Z, Wireframe, Grid)
    dialog.control_bar.spin_escala_z.setValue(2.0)
    dialog.control_bar.chk_wireframe.setChecked(True)
    dialog.control_bar.chk_grid.setChecked(False)

    dialog.close()


def test_base_3d_dialog_and_controls(qapp):
    """
    Verifica que Base3DPlotDialog administre de forma unificada los controles manuales de escala Z, wireframe y grid.
    """
    from gui.components.base_3d_dialog import Base3DPlotDialog

    class TestDialog(Base3DPlotDialog):
        def __init__(self, parent=None):
            super().__init__(titulo="Prueba 3D", parent=parent)

        def _actualizar_grafico_3d(self):
            pass

    dlg = TestDialog()
    cmap, elev, azim, z_scale, wireframe, show_grid = dlg._obtener_parametros_render()
    assert z_scale == 1.0
    assert wireframe is False
    assert show_grid is True

    dlg.control_bar.restablecer_vista()
    dlg.close()







