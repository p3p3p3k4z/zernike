"""
gui/components/equation_input_widget.py
========================================
Componente UI reutilizable y desacoplado para la entrada de ecuaciones matemáticas Z(x,y),
presets rápidos y vinculación con el Gestor de Presets e Historial.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton
)
from PySide6.QtCore import Signal


class EquationInputWidget(QWidget):
    """
    Componente modular que encapsula un QLineEdit para ecuaciones Z(x,y),
    botones de acceso rápido a presets frecuentes y conexión con el Gestor de Presets.
    """
    textChanged = Signal(str)
    ecuacion_cambiada = Signal(str)

    def __init__(self, ecuacion_inicial: str = "3*x*y + 2*x", incluir_presets: bool = True, parent=None):
        super().__init__(parent)
        self.incluir_presets = incluir_presets
        self._construir_ui(ecuacion_inicial)

    def _construir_ui(self, ecuacion_inicial: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.lbl_titulo = QLabel("Ecuación Z(x,y):")
        layout.addWidget(self.lbl_titulo)

        self.input_ecuacion = QLineEdit(ecuacion_inicial)
        self.input_ecuacion.setToolTip("Introduce una función cartesiana o trigonométrica (ej. sin(x) + cos(y)).")
        self.input_ecuacion.textChanged.connect(self._al_cambiar_texto)
        layout.addWidget(self.input_ecuacion)

        if self.incluir_presets:
            lbl_presets = QLabel("Ecuaciones de prueba rápidas:")
            lbl_presets.setStyleSheet("font-size: 11px; color: #64748B;")
            layout.addWidget(lbl_presets)

            btn_gestor = QPushButton("Gestor de Presets e Historial...")
            btn_gestor.setObjectName("btn_preset")
            btn_gestor.setToolTip("Abre el administrador de presets ópticos, historial reciente y ecuaciones guardadas.")
            btn_gestor.clicked.connect(self._abrir_gestor_presets)
            layout.addWidget(btn_gestor)

            grid_presets = QGridLayout()
            btn_p1 = QPushButton("Astigmatismo (3xy)")
            btn_p1.setObjectName("btn_preset")
            btn_p1.clicked.connect(lambda: self.setText("3*x*y + 2*x"))

            btn_p2 = QPushButton("Onda (sin(x)+cos(y))")
            btn_p2.setObjectName("btn_preset")
            btn_p2.clicked.connect(lambda: self.setText("sin(x) + cos(y)"))

            btn_p3 = QPushButton("Desenfoque (x^2+y^2)")
            btn_p3.setObjectName("btn_preset")
            btn_p3.clicked.connect(lambda: self.setText("x^2 + y^2"))

            btn_p4 = QPushButton("3er Orden Complejo")
            btn_p4.setObjectName("btn_preset")
            btn_p4.clicked.connect(lambda: self.setText("-y - 1.5*y*y*y + 1.5*x*x*y + x*y*y - 0.33*x*x*x + 2*x*x + 2*y*y + 0.5*x - 1"))

            grid_presets.addWidget(btn_p1, 0, 0)
            grid_presets.addWidget(btn_p2, 0, 1)
            grid_presets.addWidget(btn_p3, 1, 0)
            grid_presets.addWidget(btn_p4, 1, 1)
            layout.addLayout(grid_presets)

    def text(self) -> str:
        return self.input_ecuacion.text()

    def setText(self, text: str):
        self.input_ecuacion.setText(text)

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self.lbl_titulo.setEnabled(enabled)
        self.input_ecuacion.setEnabled(enabled)

    def setStyleSheet(self, style: str):
        self.input_ecuacion.setStyleSheet(style)

    def _al_cambiar_texto(self, text: str):
        self.textChanged.emit(text)
        self.ecuacion_cambiada.emit(text)

    def _abrir_gestor_presets(self):
        from gui.components.preset_manager import PresetManagerDialog
        dlg = PresetManagerDialog(ecuacion_actual=self.text(), parent=self)
        dlg.ecuacion_seleccionada.connect(self.setText)
        dlg.exec()
