"""Cuadro de dialogo interactivo que replica la interfaz estandar de 'Zernike Polynomials' de Zemax OpticStudio."""

import numpy as np
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QTabWidget, QWidget,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt


class ZemaxViewDialog(QDialog):
    """Ventana flotante de analisis con diseno e interfaz identica a Zemax OpticStudio."""
    def __init__(self, resultado_zernike=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zernike Polynomials — Vista Modo Zemax OpticStudio")
        self.resize(980, 640)

        if parent is not None and hasattr(parent, 'styleSheet'):
            self.setStyleSheet(parent.styleSheet())

        self.resultado = resultado_zernike
        self.coeficientes = np.zeros(21)
        self.bloqueando_senales = False

        from gui.styles import obtener_paleta_tema
        self.es_oscuro = getattr(parent, 'tema_actual', 'claro') == 'oscuro'
        paleta = obtener_paleta_tema("oscuro" if self.es_oscuro else "claro")

        self.c_bg = paleta["card_bg"]
        self.c_fg = paleta["fg"]
        self.c_input_bg = paleta["input_bg"]
        self.c_input_fg = paleta["input_fg"]
        self.c_border = paleta["border"]
        self.c_header_bg = paleta["header_bg"]
        self.c_header_fg = paleta["header_fg"]
        self.c_empty_bg = paleta["empty_bg"]
        self.c_empty_border = paleta["empty_border"]

        self._construir_ui()
        if self.resultado is not None:
            self._poblar_datos_desde_resultado(self.resultado)
        else:
            self._recalcular_quick_fit()

    def actualizar_datos(self, resultado_zernike):
        """Actualiza dinámicamente la vista de Zemax con un nuevo resultado de ajuste de Zernike."""
        self.resultado = resultado_zernike
        if self.resultado is not None:
            self._poblar_datos_desde_resultado(self.resultado)


    def _construir_ui(self):
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(10, 10, 10, 10)
        layout_principal.setSpacing(12)

        panel_izquierdo = QVBoxLayout()
        panel_izquierdo.setSpacing(10)

        btn_delete = QPushButton("Delete")
        btn_delete.setToolTip("Restablece a cero todos los coeficientes de Zernike.")
        btn_delete.setStyleSheet("padding: 6px 12px; font-weight: bold;")
        btn_delete.clicked.connect(self._al_hacer_clic_delete)
        panel_izquierdo.addWidget(btn_delete)

        btn_split = QPushButton("Split")
        btn_split.setToolTip("Descompone la fase separando Aberraciones Primarias de Seidel vs Alto Orden.")
        btn_split.setStyleSheet("padding: 6px 12px; font-weight: bold;")
        btn_split.clicked.connect(self._al_hacer_clic_split)
        panel_izquierdo.addWidget(btn_split)

        btn_order = QPushButton("Set Order")
        btn_order.setToolTip("Configura el numero maximo de terminos de Zernike a evaluar (1..21).")
        btn_order.setStyleSheet("padding: 6px 12px; font-weight: bold;")
        btn_order.clicked.connect(self._al_hacer_clic_set_order)
        panel_izquierdo.addWidget(btn_order)

        panel_izquierdo.addSpacing(10)

        group_fit = QGroupBox("Quick Fit")
        group_fit.setStyleSheet(
            f"QGroupBox {{ font-weight: bold; font-size: 13px; border: 2px solid {self.c_border}; border-radius: 6px; margin-top: 6px; padding-top: 10px; color: {self.c_fg}; }} "
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {self.c_fg}; }}"
        )
        group_fit.setMinimumWidth(220)

        layout_fit = QGridLayout(group_fit)
        layout_fit.setContentsMargins(10, 14, 10, 14)
        layout_fit.setSpacing(10)

        labels_fit = [
            ("Irregularity", "txt_irregularity"),
            ("Power", "txt_power"),
            ("RMS", "txt_rms"),
            ("Peak-to-Valley", "txt_pv"),
            ("Points", "txt_points")
        ]

        for i, (txt_lbl, attr_name) in enumerate(labels_fit):
            lbl = QLabel(txt_lbl)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setStyleSheet(f"font-weight: bold; font-size: 12px; color: {self.c_fg};")
            line_edit = QLineEdit("0.000")
            line_edit.setReadOnly(True)
            line_edit.setAlignment(Qt.AlignRight)
            line_edit.setMinimumWidth(95)
            line_edit.setStyleSheet(f"font-weight: bold; font-size: 13px; background-color: {self.c_input_bg}; color: {self.c_input_fg}; padding: 5px; border: 1px solid {self.c_border}; border-radius: 4px;")
            setattr(self, attr_name, line_edit)
            layout_fit.addWidget(lbl, i, 0)
            layout_fit.addWidget(line_edit, i, 1)

        panel_izquierdo.addWidget(group_fit)
        panel_izquierdo.addStretch()

        layout_principal.addLayout(panel_izquierdo, stretch=0)

        group_data = QGroupBox("Zernike Polynomials")
        group_data.setStyleSheet(
            f"QGroupBox {{ font-weight: bold; font-size: 13px; border: 2px solid {self.c_border}; border-radius: 6px; margin-top: 6px; padding-top: 10px; color: {self.c_fg}; }} "
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {self.c_fg}; }}"
        )

        layout_data = QVBoxLayout(group_data)
        layout_data.setContentsMargins(10, 12, 10, 10)
        layout_data.setSpacing(10)

        layout_top_bar = QHBoxLayout()
        layout_top_bar.setSpacing(12)

        self.txt_piston = self._crear_spin_coef(1, "Piston:")
        self.txt_focus = self._crear_spin_coef(5, "Focus:")
        self.txt_ytilt = self._crear_spin_coef(3, "Y Tilt:")
        self.txt_xtilt = self._crear_spin_coef(2, "X Tilt:")

        layout_top_bar.addLayout(self._wrap_field("Piston:", self.txt_piston))
        layout_top_bar.addLayout(self._wrap_field("Focus:", self.txt_focus))
        layout_top_bar.addLayout(self._wrap_field("Y Tilt:", self.txt_ytilt))
        layout_top_bar.addLayout(self._wrap_field("X Tilt:", self.txt_xtilt))

        layout_top_bar.addStretch()

        lbl_terms = QLabel("Terms:")
        lbl_terms.setStyleSheet(f"font-weight: bold; color: {self.c_fg};")
        self.spin_terms = QSpinBox()
        self.spin_terms.setRange(1, 21)
        self.spin_terms.setValue(21)
        self.spin_terms.setStyleSheet(f"background-color: {self.c_input_bg}; color: {self.c_input_fg}; font-weight: bold; border: 1px solid {self.c_border}; border-radius: 3px; padding: 3px;")
        self.spin_terms.setToolTip("Numero de terminos de Zernike activos (ISO 10110-5).")
        self.spin_terms.valueChanged.connect(self._al_cambiar_terms)
        layout_top_bar.addWidget(lbl_terms)
        layout_top_bar.addWidget(self.spin_terms)

        layout_data.addLayout(layout_top_bar)

        line_sep = QFrame()
        line_sep.setFrameShape(QFrame.HLine)
        line_sep.setFrameShadow(QFrame.Sunken)
        layout_data.addWidget(line_sep)

        self.grid_matrix = QGridLayout()
        self.grid_matrix.setSpacing(4)

        headers_orden = ["3rd", "5th", "7th", "9th", "11th"]
        for col_idx, h_text in enumerate(headers_orden, start=1):
            lbl_h = QLabel(h_text)
            lbl_h.setAlignment(Qt.AlignCenter)
            lbl_h.setStyleSheet(f"font-weight: bold; background-color: {self.c_header_bg}; color: {self.c_header_fg}; padding: 4px; border-radius: 3px;")
            self.grid_matrix.addWidget(lbl_h, 0, col_idx)

        nombres_aberraciones = [
            "Spherical", "Y Coma", "X Coma", "45° Astig", "0° Astig",
            "0° Tri", "30° Tri", "22.5° Quad", "0° Quad",
            "18° Penta", "0° Penta", "15° Hex", "0° Hex"
        ]

        for row_idx, nombre in enumerate(nombres_aberraciones, start=1):
            lbl_l = QLabel(nombre)
            lbl_l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl_l.setStyleSheet(f"color: {self.c_fg}; font-size: 11px;")
            self.grid_matrix.addWidget(lbl_l, row_idx, 0)

            lbl_r = QLabel(nombre)
            lbl_r.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            lbl_r.setStyleSheet(f"color: {self.c_fg}; font-size: 11px;")
            self.grid_matrix.addWidget(lbl_r, row_idx, 6)

        self.mapeo_celda_zernike = {
            (1, 1): 13,  # Spherical 3rd (A_13)
            (1, 2): 9,   # Y Coma 3rd (A_9)
            (1, 3): 8,   # X Coma 3rd (A_8)
            (1, 4): 4,   # 45° Astig 3rd (A_4)
            (1, 5): 6,   # 0° Astig 3rd (A_6)
            (2, 2): 19,  # Y Coma 5th (A_19)
            (2, 3): 18,  # X Coma 5th (A_18)
            (2, 4): 12,  # 45° Astig 5th (A_12)
            (2, 5): 14,  # 0° Astig 5th (A_14)
            (2, 6): 10,  # 0° Tri 5th (A_10)
            (2, 7): 7,   # 30° Tri 5th (A_7)
            (3, 6): 20,  # 0° Tri 7th (A_20)
            (3, 7): 17,  # 30° Tri 7th (A_17)
            (3, 8): 11,  # 22.5° Quad 7th (A_11)
            (3, 9): 15,  # 0° Quad 7th (A_15)
            (4, 10): 16, # 18° Penta 9th (A_16)
            (4, 11): 21, # 0° Penta 9th (A_21)
        }


        self.dict_spins_matriz = {}

        for col_idx in range(1, 6):
            for row_idx in range(1, 14):
                key = (col_idx, row_idx)
                if key in self.mapeo_celda_zernike:
                    r_idx = self.mapeo_celda_zernike[key]
                    spin = self._crear_spin_coef(r_idx)
                    self.dict_spins_matriz[r_idx] = spin
                    self.grid_matrix.addWidget(spin, row_idx, col_idx)
                else:
                    lbl_empty = QLabel()
                    lbl_empty.setStyleSheet(f"background-color: {self.c_empty_bg}; border: 1px inset {self.c_empty_border};")
                    self.grid_matrix.addWidget(lbl_empty, row_idx, col_idx)

        layout_data.addLayout(self.grid_matrix)
        layout_data.addStretch()

        layout_bottom = QHBoxLayout()

        btn_exp_zemax = QPushButton("Exportar a Zemax (.zrn)")
        btn_exp_zemax.clicked.connect(self._exportar_zemax)
        layout_bottom.addWidget(btn_exp_zemax)

        btn_exp_codev = QPushButton("Exportar a CODE V (.dat)")
        btn_exp_codev.clicked.connect(self._exportar_codev)
        layout_bottom.addWidget(btn_exp_codev)

        btn_exp_html = QPushButton("Exportar Reporte HTML")
        btn_exp_html.setStyleSheet("font-weight: bold; background-color: #1e3a8a; color: #ffffff; padding: 4px 10px; border-radius: 4px;")
        btn_exp_html.clicked.connect(self._exportar_reporte_html_dialog)
        layout_bottom.addWidget(btn_exp_html)

        layout_bottom.addStretch()

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setDefault(True)
        btn_aceptar.clicked.connect(self.accept)
        layout_bottom.addWidget(btn_aceptar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        layout_bottom.addWidget(btn_cancelar)

        panel_derecho = QVBoxLayout()
        panel_derecho.addWidget(group_data, stretch=1)
        panel_derecho.addLayout(layout_bottom)

        layout_principal.addLayout(panel_derecho, stretch=1)

    def _wrap_field(self, label_text: str, widget: QWidget) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(4)
        lbl = QLabel(label_text)
        lbl.setStyleSheet(f"font-weight: bold; color: {self.c_fg};")
        layout.addWidget(lbl)
        layout.addWidget(widget)
        return layout

    def _crear_spin_coef(self, r_index: int, label: str = "") -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(-999.0, 999.0)
        spin.setDecimals(4)
        spin.setSingleStep(0.01)
        spin.setValue(0.0)
        spin.setAlignment(Qt.AlignRight)
        spin.setStyleSheet(f"font-weight: bold; font-size: 12px; background-color: {self.c_input_bg}; color: {self.c_input_fg}; border: 1px solid {self.c_border}; border-radius: 3px; padding: 2px;")
        spin.setToolTip(f"Coeficiente Zernike A_{r_index} (ISO 10110-5 / r={r_index})")
        spin.valueChanged.connect(lambda val, idx=r_index: self._al_cambiar_coeficiente(idx, val))
        return spin

    def _poblar_datos_desde_resultado(self, resultado):
        if hasattr(resultado, 'A') and resultado.A is not None:
            self.bloqueando_senales = True
            self.coeficientes = np.array(resultado.A, dtype=float)

            self.txt_piston.setValue(self.coeficientes[0])
            self.txt_xtilt.setValue(self.coeficientes[1])
            self.txt_ytilt.setValue(self.coeficientes[2])
            self.txt_focus.setValue(self.coeficientes[4])

            for r_idx, spin in self.dict_spins_matriz.items():
                if r_idx <= len(self.coeficientes):
                    spin.setValue(self.coeficientes[r_idx - 1])

            if hasattr(resultado, 'W') and resultado.W is not None:
                self.txt_points.setText(str(len(resultado.W)))

            self.bloqueando_senales = False
            self._recalcular_quick_fit()

    def _al_cambiar_coeficiente(self, r_index: int, valor: float):
        if self.bloqueando_senales:
            return
        if 1 <= r_index <= 21:
            self.coeficientes[r_index - 1] = valor
            self._sincronizar_campos(r_index, valor)
            self._recalcular_quick_fit()

    def _sincronizar_campos(self, r_index: int, valor: float):
        """Sincroniza los valores entre la barra superior (Piston/Focus/Tilts) y la matriz."""
        self.bloqueando_senales = True
        if r_index == 1:
            self.txt_piston.setValue(valor)
        elif r_index == 2:
            self.txt_xtilt.setValue(valor)
        elif r_index == 3:
            self.txt_ytilt.setValue(valor)
        elif r_index == 5:
            self.txt_focus.setValue(valor)

        if r_index in self.dict_spins_matriz:
            self.dict_spins_matriz[r_index].setValue(valor)
        self.bloqueando_senales = False

    def _al_cambiar_terms(self, max_terms: int):
        self.bloqueando_senales = True
        for r_idx in range(1, 22):
            activo = (r_idx <= max_terms)
            if r_idx in self.dict_spins_matriz:
                self.dict_spins_matriz[r_idx].setEnabled(activo)
        self.bloqueando_senales = False
        self._recalcular_quick_fit()

    def _limpiar_coeficientes(self):
        self.bloqueando_senales = True
        self.coeficientes.fill(0.0)
        self.txt_piston.setValue(0.0)
        self.txt_xtilt.setValue(0.0)
        self.txt_ytilt.setValue(0.0)
        self.txt_focus.setValue(0.0)
        for spin in self.dict_spins_matriz.values():
            spin.setValue(0.0)
        self.bloqueando_senales = False
        self._recalcular_quick_fit()

    def _al_hacer_clic_delete(self):
        """Accion del boton Delete: pregunta al usuario y limpia todos los coeficientes a cero."""
        reply = QMessageBox.question(
            self,
            "Delete / Limpiar Coeficientes",
            "Deseas restablecer a cero todos los coeficientes de Zernike (1..21)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._limpiar_coeficientes()

    def _al_hacer_clic_split(self):
        """Accion del boton Split: descompone el frente de onda en componentes Seidel vs Alto Orden."""
        terms_activos = self.spin_terms.value()
        A_active = self.coeficientes[:terms_activos]

        seidel_rms = np.sqrt(np.sum(A_active[1:9]**2)) if len(A_active) >= 9 else (np.sqrt(np.sum(A_active[1:]**2)) if len(A_active) > 1 else 0.0)
        high_order_rms = np.sqrt(np.sum(A_active[9:]**2)) if len(A_active) > 9 else 0.0
        total_rms = np.sqrt(np.sum(A_active[1:]**2)) if len(A_active) > 1 else 0.0

        msg = (
            "<b>Descomposicion de Fase (Split Component Analysis — Estilo Zemax):</b><br><br>"
            f"• <b>Aberraciones Primarias de Seidel (3er Orden A2..A9):</b> RMS = {seidel_rms:.4f} λ<br>"
            f"• <b>Aberraciones de Alto Orden (5to+ Orden A10..A21):</b> RMS = {high_order_rms:.4f} λ<br>"
            f"• <b>Error RMS Global Total (excluyendo Piston):</b> {total_rms:.4f} λ"
        )
        QMessageBox.information(self, "Split — Descomposicion de Fase", msg)

    def _al_hacer_clic_set_order(self):
        """Accion del boton Set Order: abre un dialogo modal para configurar el numero maximo de terminos activos."""
        from PySide6.QtWidgets import QInputDialog
        num_terms, ok = QInputDialog.getInt(
            self,
            "Set Order / Numero de Terminos Activos",
            "Selecciona el numero maximo de terminos de Zernike a evaluar (1 a 21):",
            value=self.spin_terms.value(),
            minValue=1, maxValue=21, step=1
        )
        if ok:
            self.spin_terms.setValue(num_terms)

    def _recalcular_quick_fit(self):
        """Recalcula dinamicamente las metricas de Quick Fit (RMS, P-V, Irregularity, Power)."""
        terms_activos = self.spin_terms.value()
        A_active = self.coeficientes[:terms_activos]

        power_val = A_active[4] if len(A_active) >= 5 else 0.0
        self.txt_power.setText(f"{power_val:.3f}")

        if len(A_active) > 1:
            rms_val = np.sqrt(np.sum(A_active[1:]**2))
        else:
            rms_val = 0.0
        self.txt_rms.setText(f"{rms_val:.3f}")

        indices_alto_orden = [i for i in range(len(A_active)) if i not in (0, 1, 2, 4)]
        if indices_alto_orden:
            irregularity_val = np.sqrt(np.sum(A_active[indices_alto_orden]**2))
        else:
            irregularity_val = 0.0
        self.txt_irregularity.setText(f"{irregularity_val:.3f}")

        pv_val = 2.0 * np.sum(np.abs(A_active[1:])) if len(A_active) > 1 else 0.0
        self.txt_pv.setText(f"{pv_val:.3f}")

        if not self.txt_points.text():
            self.txt_points.setText("4513")

    def _exportar_zemax(self):
        from PySide6.QtWidgets import QFileDialog
        from lib.io import exportar_zemax
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Coeficientes a Zemax OpticStudio",
            "output/zemax_zernike.zrn",
            "Archivos Zemax (*.zrn *.txt)"
        )
        if filepath:
            res_tmp = self._crear_resultado_temporal()
            ok = exportar_zemax(res_tmp, filepath=filepath)
            if ok:
                QMessageBox.information(self, "Exportación Exitosa", f"Archivo Zemax OpticStudio guardado en:\n{filepath}")

    def _exportar_codev(self):
        from PySide6.QtWidgets import QFileDialog
        from lib.io import exportar_codev
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Coeficientes a CODE V",
            "output/codev_zernike.dat",
            "Archivos CODE V (*.dat *.txt)"
        )
        if filepath:
            res_tmp = self._crear_resultado_temporal()
            ok = exportar_codev(res_tmp, filepath=filepath)
            if ok:
                QMessageBox.information(self, "Exportación Exitosa", f"Archivo CODE V guardado en:\n{filepath}")

    def _exportar_reporte_html_dialog(self):
        from PySide6.QtWidgets import QFileDialog
        from lib.reportes import exportar_reporte_html
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Reporte Metrologico (HTML)",
            "output/reporte_metrologico_zemax.html",
            "Archivos HTML (*.html)"
        )
        if filepath:
            res_tmp = self._crear_resultado_temporal()
            ok = exportar_reporte_html(res_tmp, filepath, titulo="Reporte Metrologico (Modo Zemax OpticStudio)")
            if ok:
                QMessageBox.information(self, "Reporte HTML Generado", f"Reporte metrologico HTML generado con exito en:\n{filepath}")

    def _crear_resultado_temporal(self):
        from lib.zernike import ResultadoZernike
        N = int(self.txt_points.text()) if self.txt_points.text().isdigit() else 100
        x = np.linspace(-1, 1, N)
        y = np.linspace(-1, 1, N)
        return ResultadoZernike(
            U=np.array([]), V=[], D=np.array([]), F=None,
            B=np.array([]), C=np.array([]),
            A=self.coeficientes.copy(),
            W_fit=np.array([]), X=x, Y=y, W=np.array([])
        )
