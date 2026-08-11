"""
gui/engine_comparison_dialog.py
================================
Cuadro de dialogo interactivo para comparar matematicamente
el motor de calculo en Python (NumPy) frente al motor nativo en Fortran.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt

from gui.canvas import MplCanvasWidget
from lib.zernike import polinomios_zernike, ajuste_completo
from lib.fortran_runner import ejecutar_zernike_fortran, asegurar_binario_fortran


class EngineComparisonDialog(QDialog):
    """
    Dialogo flotante para la comparacion cuantitativa y visual (Scatter plot & Tabla de Coeficientes)
    entre los resultados de los motores Python y Fortran.
    """
    def __init__(self, X_in, Y_in, W_in, parent=None):
        super().__init__(parent)
        self.X_in = X_in
        self.Y_in = Y_in
        self.W_in = W_in

        self.setWindowTitle("Comparador de Motores Numéricos — Python (NumPy) vs. Fortran Nativo")
        self.resize(980, 720)

        if parent is not None and hasattr(parent, 'styleSheet'):
            self.setStyleSheet(parent.styleSheet())

        self._construir_ui()
        self._ejecutar_comparacion()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 1. Panel de Resumen Estadistico
        grupo_stats = QGroupBox("Estadísticas de Correlación (1.0 = Igualdad Perfecta)")
        layout_stats = QHBoxLayout(grupo_stats)

        self.lbl_corr_exp = QLabel("Correlación Z Exp: ---")
        self.lbl_corr_exp.setStyleSheet("font-weight: bold; font-size: 12px; color: #2563EB;")
        layout_stats.addWidget(self.lbl_corr_exp)

        self.lbl_corr_fit = QLabel("Correlación Z Fit: ---")
        self.lbl_corr_fit.setStyleSheet("font-weight: bold; font-size: 12px; color: #16A34A;")
        layout_stats.addWidget(self.lbl_corr_fit)

        self.lbl_escala = QLabel("Factor Escala (Fortran / Py): ---")
        self.lbl_escala.setStyleSheet("font-weight: bold; font-size: 12px; color: #D97706;")
        layout_stats.addWidget(self.lbl_escala)

        layout.addWidget(grupo_stats)

        # 2. Contenedor Horizontal: Tabla a la Izquierda, Grafico Scatter a la Derecha
        layout_cuerpo = QHBoxLayout()

        # Tabla de Coeficientes A
        self.tabla_coef = QTableWidget()
        self.tabla_coef.setColumnCount(4)
        self.tabla_coef.setHorizontalHeaderLabels(["Polinomio", "A (Python)", "A (Fortran)", "|Diferencia|"])
        self.tabla_coef.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_cuerpo.addWidget(self.tabla_coef, stretch=4)

        # Canvas Matplotlib Scatter Plot
        self.canvas = MplCanvasWidget(self)
        layout_cuerpo.addWidget(self.canvas, stretch=6)

        layout.addLayout(layout_cuerpo)

    def _ejecutar_comparacion(self):
        try:
            ok, msg = asegurar_binario_fortran()
            if not ok:
                QMessageBox.warning(self, "Compilador Fortran No Disponible", msg)
                return

            if len(self.X_in) > 50000:
                QMessageBox.warning(
                    self,
                    "Límite de Datos",
                    f"El motor Fortran admite un máximo de 50,000 puntos. Se recibieron {len(self.X_in)} puntos."
                )
                return

            # 1. Ejecutar Motor Python (k=5, 21 polinomios)
            polinomios = polinomios_zernike()
            res_python = ajuste_completo(self.X_in, self.Y_in, self.W_in, polinomios, k=5)

            # 2. Ejecutar Motor Fortran (k=4, 15 polinomios)
            res_fortran = ejecutar_zernike_fortran(self.X_in, self.Y_in, self.W_in)

            # 3. Analisis de Correlacion y Factor de Escala
            N_comun = min(len(res_python.W_fit), len(res_fortran.W_fit))
            fit_py = res_python.W_fit[:N_comun]
            fit_ft = res_fortran.W_fit[:N_comun]
            exp_py = res_python.W[:N_comun]
            exp_ft = res_fortran.W[:N_comun]

            corr_exp = np.corrcoef(exp_ft, exp_py)[0, 1] if len(exp_py) > 1 else 1.0
            corr_fit = np.corrcoef(fit_ft, fit_py)[0, 1] if len(fit_py) > 1 else 1.0

            with np.errstate(divide='ignore', invalid='ignore'):
                ratio = fit_ft / fit_py
                factor_escala = float(np.nanmedian(ratio))

            self.lbl_corr_exp.setText(f"Correlación Z Exp: {corr_exp:.6f}")
            self.lbl_corr_fit.setText(f"Correlación Z Fit: {corr_fit:.6f}")
            self.lbl_escala.setText(f"Factor Escala (Fortran / Py): {factor_escala:.4f}")

            # 4. Llenar Tabla Comparativa A_1 a A_15
            self.tabla_coef.setRowCount(15)
            nombres = ["Piston", "Tilt X", "Tilt Y", "Astig 45", "Defocus", "Astig 0",
                       "Trefoil Y", "Coma X", "Coma Y", "Trefoil X", "Quadrafoil Y",
                       "Astig 2do Y", "Esferica 4to", "Astig 2do X", "Quadrafoil X"]

            for r in range(1, 16):
                val_py = res_python.A[r - 1]
                val_ft = res_fortran.A[r - 1]
                diff = abs(val_py - val_ft)

                item_r = QTableWidgetItem(f"A_{r} ({nombres[r-1]})")
                item_py = QTableWidgetItem(f"{val_py:.6f}")
                item_ft = QTableWidgetItem(f"{val_ft:.6f}")
                item_diff = QTableWidgetItem(f"{diff:.6f}")

                item_r.setTextAlignment(Qt.AlignCenter)
                item_py.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item_ft.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item_diff.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                self.tabla_coef.setItem(r - 1, 0, item_r)
                self.tabla_coef.setItem(r - 1, 1, item_py)
                self.tabla_coef.setItem(r - 1, 2, item_ft)
                self.tabla_coef.setItem(r - 1, 3, item_diff)

            # 5. Generar Grafico Scatter Comparativo en Canvas
            # Crear figura directamente con Figure() para no registrarla en pyplot (Gcf),
            # evitando la aparicion de ventanas nativas vacias (FigureManagerQT) en Windows.
            fig = Figure(figsize=(8, 5))
            ax = fig.add_subplot(111)

            ax.scatter(fit_py, fit_ft, alpha=0.7, color='#2563EB', edgecolor='#1E40AF', s=25, label='Puntos (Z_fit Py vs Fortran)')

            # Linea de identidad ideal y=x
            lims = [min(fit_py.min(), fit_ft.min()), max(fit_py.max(), fit_ft.max())]
            ax.plot(lims, lims, 'r--', alpha=0.8, linewidth=1.5, label='Identidad Ideal (y=x)')

            ax.set_title(f"Dispersión: Ajuste Zernike (Correlación R = {corr_fit:.6f})", fontsize=11, fontweight='bold')
            ax.set_xlabel("Z_fit Python (NumPy)")
            ax.set_ylabel("Z_fit Fortran (Gram-Schmidt)")
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc='upper left')

            fig.tight_layout()
            self.canvas.set_figure(fig)

        except Exception as e:
            QMessageBox.critical(self, "Error en Comparación", f"Ocurrió un error al comparar motores:\n{str(e)}")
