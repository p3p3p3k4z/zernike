"""
gui/components/summary_tables.py
================================
Componente reutilizable que encapsula las tablas de resultados:
- Tabla 1 (Arriba): Coeficientes ISO A1 .. A21 con descripcion optica
- Tabla 2 (Abajo): Descomposicion fisica de aberraciones (Seidel)
- Tarjeta inferior: Metrica de Calidad de Superficie (Error RMS)
"""

import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QSplitter,
    QMenu, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication, QKeySequence, QAction

from lib.matriz import descomponer_aberraciones
from gui.styles import aplicar_estilo_rms_card

_ZERNIKE_DESCRIPCIONES_ISO = [
    "Pistón", "Tilt X", "Tilt Y", "Astigmatismo 45°", "Defocus", "Astigmatismo 0°",
    "Trefoil X", "Coma X", "Coma Y", "Trefoil Y", "Tetrafoil X", "Astigmatismo 2° 45°",
    "Aberración Esférica 3er Ord", "Astigmatismo 2° 0°", "Tetrafoil Y", "Pentafoil X",
    "Trefoil 2° X", "Coma 2° X", "Coma 2° Y", "Trefoil 2° Y", "Pentafoil Y"
]


class CustomTableWidget(QTableWidget):
    """QTableWidget personalizado con soporte nativo para Ctrl+C."""
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copiar_seleccion()
            event.accept()
        else:
            super().keyPressEvent(event)

    def copiar_seleccion(self):
        ranges = self.selectedRanges()
        if not ranges:
            return
        r = ranges[0]
        filas = []
        for row in range(r.topRow(), r.bottomRow() + 1):
            cols = []
            for col in range(r.leftColumn(), r.rightColumn() + 1):
                item = self.item(row, col)
                cols.append(item.text() if item else "")
            filas.append("\t".join(cols))
        texto_copiado = "\n".join(filas)
        QGuiApplication.clipboard().setText(texto_copiado)


class SummaryTablesWidget(QWidget):
    """
    Widget con layout vertical desplegando las tablas de coeficientes Zernike, 
    aberraciones de Seidel y la tarjeta de error RMS.
    """
    notificacion_copia = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout_principal = QVBoxLayout(self)

        splitter_v = QSplitter(Qt.Vertical)

        # Tabla 1 (Arriba): Coeficientes ISO A
        grupo_tabla_a = QGroupBox("Coeficientes de Zernike ISO (A1 .. A21)")
        layout_a = QVBoxLayout(grupo_tabla_a)
        
        self.tabla_coef = CustomTableWidget(21, 3)
        self.tabla_coef.setHorizontalHeaderLabels(["Índice", "Coeficiente A", "Descripción Óptica"])
        self.tabla_coef.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_coef.setAlternatingRowColors(True)
        self._configurar_menu_contextual(self.tabla_coef, "Coeficientes de Zernike")
        layout_a.addWidget(self.tabla_coef)
        splitter_v.addWidget(grupo_tabla_a)

        # Tabla 2 (Abajo): Descomposición Aberracional Física + Tarjeta RMS
        grupo_tabla_ab = QGroupBox("Descomposición de Aberraciones Físicas (Seidel)")
        layout_ab = QVBoxLayout(grupo_tabla_ab)

        self.tabla_aberraciones = CustomTableWidget(13, 2)
        self.tabla_aberraciones.setHorizontalHeaderLabels(["Aberración Óptica", "Magnitud Calculada"])
        self.tabla_aberraciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_aberraciones.setAlternatingRowColors(True)
        self._configurar_menu_contextual(self.tabla_aberraciones, "Aberraciones de Seidel")
        layout_ab.addWidget(self.tabla_aberraciones)

        # Tarjeta de Estado del Error RMS
        self.card_rms = QFrame()
        layout_card = QHBoxLayout(self.card_rms)

        self.lbl_rms_titulo = QLabel("MÉTRICA DE CALIDAD DE SUPERFICIE:")
        self.lbl_rms = QLabel("Error RMS del Ajuste: ---")
        self.lbl_rms_desc = QLabel("(Desvío estándar de fase reconstruida vs real)")

        layout_card.addWidget(self.lbl_rms_titulo)
        layout_card.addWidget(self.lbl_rms)
        layout_card.addWidget(self.lbl_rms_desc)
        layout_card.addStretch()

        layout_ab.addWidget(self.card_rms)
        splitter_v.addWidget(grupo_tabla_ab)

        # Aplicar estilo inicial de la tarjeta RMS
        aplicar_estilo_rms_card(self.card_rms, self.lbl_rms_titulo, self.lbl_rms, self.lbl_rms_desc, tema="claro")

        # Proporcion vertical inicial
        splitter_v.setSizes([350, 300])
        layout_principal.addWidget(splitter_v)

    def _configurar_menu_contextual(self, tabla: QTableWidget, nombre_tabla: str):
        tabla.setContextMenuPolicy(Qt.CustomContextMenu)
        tabla.customContextMenuRequested.connect(
            lambda pos: self._mostrar_menu_contextual(pos, tabla, nombre_tabla)
        )

    def _mostrar_menu_contextual(self, pos, tabla: CustomTableWidget, nombre_tabla: str):
        menu = QMenu(self)

        action_copiar_sel = QAction("Copiar selección (Ctrl+C)", self)
        action_copiar_sel.triggered.connect(lambda: self._copiar_seleccion(tabla, nombre_tabla))
        menu.addAction(action_copiar_sel)

        action_copiar_todo = QAction("Copiar toda la tabla", self)
        action_copiar_todo.triggered.connect(lambda: self._copiar_toda_tabla(tabla, nombre_tabla))
        menu.addAction(action_copiar_todo)

        menu.exec(tabla.viewport().mapToGlobal(pos))

    def _copiar_seleccion(self, tabla: CustomTableWidget, nombre_tabla: str):
        tabla.copiar_seleccion()
        self.notificacion_copia.emit(f"Selección de {nombre_tabla} copiada al portapapeles.")

    def _copiar_toda_tabla(self, tabla: QTableWidget, nombre_tabla: str):
        headers = [tabla.horizontalHeaderItem(c).text() for c in range(tabla.columnCount())]
        filas = ["\t".join(headers)]
        for row in range(tabla.rowCount()):
            cols = []
            for col in range(tabla.columnCount()):
                item = tabla.item(row, col)
                cols.append(item.text() if item else "")
            filas.append("\t".join(cols))
        texto_completo = "\n".join(filas)
        QGuiApplication.clipboard().setText(texto_completo)
        self.notificacion_copia.emit(f"Tabla completa de {nombre_tabla} copiada al portapapeles.")

    def actualizar_datos(self, resultados, W_in):
        """Escribe los coeficientes y aberraciones calculadas en las tablas."""
        A = resultados.A

        # 1. Tabla de Coeficientes A
        for r in range(21):
            item_idx = QTableWidgetItem(f"A_{r+1:02d}")
            item_val = QTableWidgetItem(f"{A[r]:+.8f}")
            desc = _ZERNIKE_DESCRIPCIONES_ISO[r] if r < len(_ZERNIKE_DESCRIPCIONES_ISO) else f"Z_{r+1}"
            item_desc = QTableWidgetItem(desc)
            
            item_idx.setTextAlignment(Qt.AlignCenter)
            item_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.tabla_coef.setItem(r, 0, item_idx)
            self.tabla_coef.setItem(r, 1, item_val)
            self.tabla_coef.setItem(r, 2, item_desc)

        # 2. Tabla de Aberraciones Fisicas
        aberraciones = descomponer_aberraciones(A)
        row = 0
        for nombre, val in aberraciones.items():
            item_nom = QTableWidgetItem(nombre)
            item_val = QTableWidgetItem(f"{val:+.8f}")
            item_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            self.tabla_aberraciones.setItem(row, 0, item_nom)
            self.tabla_aberraciones.setItem(row, 1, item_val)
            row += 1

        # 3. Metrica de Error RMS
        error = W_in - resultados.W_fit
        rms = np.sqrt(np.mean(error**2))
        self.lbl_rms.setText(f"Error RMS del Ajuste: {rms:.4e}")

    def aplicar_tema(self, tema="claro"):
        """Actualiza el estilo visual de la tarjeta de RMS segun el tema."""
        aplicar_estilo_rms_card(self.card_rms, self.lbl_rms_titulo, self.lbl_rms, self.lbl_rms_desc, tema=tema)

