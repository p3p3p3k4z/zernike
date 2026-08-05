"""
gui/components/preset_manager.py
=================================
Modulo de gestion de presets de ecuaciones opticas e historial persistente de simulaciones.
Almacena presets predefinidos, historial reciente y configuraciones personalizadas del usuario en JSON.
"""

import os
import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal


PRESETS_PREDEFINIDOS = [
    {
        "nombre": "Inclinacion / Plano",
        "ecuacion": "2*x + 3*y",
        "descripcion": "Pendiente lineal en X e Y (Tilt)"
    },
    {
        "nombre": "Desenfoque / Esferica (2do Orden)",
        "ecuacion": "x**2 + y**2",
        "descripcion": "Superficie parabolica simetrica (Defocus)"
    },
    {
        "nombre": "Astigmatismo Rectangular",
        "ecuacion": "x**2 - y**2",
        "descripcion": "Curvatura cilindrica cruzada en ejes X/Y"
    },
    {
        "nombre": "Coma / Aberracion Asimetrica",
        "ecuacion": "3*x*y + 2*x",
        "descripcion": "Aberracion comatica con pendiente asimetrica"
    },
    {
        "nombre": "Trefoil (Aberracion Triangular)",
        "ecuacion": "x**3 - 3*x*y**2",
        "descripcion": "Aberracion de 3er orden con simetria tripolar"
    },
    {
        "nombre": "Esferica (4to Orden)",
        "ecuacion": "(x**2 + y**2)**2",
        "descripcion": "Aberracion esferica de alto orden"
    },
    {
        "nombre": "Superficie Compleja (3er Orden)",
        "ecuacion": "-y - 1.5*y**3 + 1.5*x**2*y + x*y**2 - 0.33*x**3 + 2*x**2 + 2*y**2 + 0.5*x - 1",
        "descripcion": "Superficie polinomica mixta de prueba"
    }
]


class PresetStorage:
    """
    Clase para leer y escribir el historial y presets del usuario en un archivo JSON.
    """
    def __init__(self, filepath=None):
        if filepath is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
            os.makedirs(config_dir, exist_ok=True)
            self.filepath = os.path.join(config_dir, "preset_history.json")
        else:
            self.filepath = filepath

        self.data = self._cargar_datos()

    def _cargar_datos(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"historial": [], "personalizados": []}

    def guardar_datos(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def agregar_historial(self, ecuacion: str):
        ecuacion = ecuacion.strip()
        if not ecuacion:
            return
        hist = self.data.get("historial", [])
        if ecuacion in hist:
            hist.remove(ecuacion)
        hist.insert(0, ecuacion)
        self.data["historial"] = hist[:15]
        self.guardar_datos()

    def agregar_personalizado(self, nombre: str, ecuacion: str):
        nombre = nombre.strip()
        ecuacion = ecuacion.strip()
        if not nombre or not ecuacion:
            return False

        pers = self.data.get("personalizados", [])
        for item in pers:
            if item["nombre"].lower() == nombre.lower():
                item["ecuacion"] = ecuacion
                self.guardar_datos()
                return True

        pers.append({"nombre": nombre, "ecuacion": ecuacion})
        self.data["personalizados"] = pers
        self.guardar_datos()
        return True


class PresetManagerDialog(QDialog):
    """
    Cuadro de dialogo interactivo para seleccionar presets opticos,
    explorar el historial reciente y guardar ecuaciones personalizadas.
    """
    ecuacion_seleccionada = Signal(str)

    def __init__(self, ecuacion_actual="", parent=None):
        super().__init__(parent)
        self.ecuacion_actual = ecuacion_actual
        self.storage = PresetStorage()

        self.setWindowTitle("Gestor de Presets e Historial de Ecuaciones Opticas")
        self.resize(650, 480)

        if parent is not None and hasattr(parent, 'styleSheet'):
            self.setStyleSheet(parent.styleSheet())

        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.tabs = QTabWidget()

        # Tab 1: Presets Opticos Predefinidos
        tab_presets = QWidget()
        layout_p = QVBoxLayout(tab_presets)
        self.list_presets = QListWidget()
        for p in PRESETS_PREDEFINIDOS:
            item_text = f"{p['nombre']}  ->  {p['ecuacion']}\n    Desc: {p['descripcion']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, p['ecuacion'])
            self.list_presets.addItem(item)
        layout_p.addWidget(self.list_presets)
        self.tabs.addTab(tab_presets, "Presets Opticos")

        # Tab 2: Historial Reciente
        tab_historial = QWidget()
        layout_h = QVBoxLayout(tab_historial)
        self.list_historial = QListWidget()
        hist_data = self.storage.data.get("historial", [])
        if not hist_data:
            self.list_historial.addItem("No hay ecuaciones en el historial reciente.")
        else:
            for eq in hist_data:
                item = QListWidgetItem(eq)
                item.setData(Qt.UserRole, eq)
                self.list_historial.addItem(item)
        layout_h.addWidget(self.list_historial)
        self.tabs.addTab(tab_historial, "Historial Reciente")

        # Tab 3: Presets Personalizados y Guardado
        tab_pers = QWidget()
        layout_pers = QVBoxLayout(tab_pers)

        layout_form = QHBoxLayout()
        layout_form.addWidget(QLabel("Nombre del Preset:"))
        self.input_nombre_pers = QLineEdit()
        self.input_nombre_pers.setPlaceholderText("Ej. Espejo Primario M1")
        layout_form.addWidget(self.input_nombre_pers)

        layout_pers.addLayout(layout_form)

        layout_eq = QHBoxLayout()
        layout_eq.addWidget(QLabel("Ecuacion Z(x,y):"))
        self.input_eq_pers = QLineEdit(self.ecuacion_actual)
        layout_eq.addWidget(self.input_eq_pers)
        layout_pers.addLayout(layout_eq)

        btn_guardar = QPushButton("Guardar Preset Personalizado")
        btn_guardar.clicked.connect(self._guardar_personalizado)
        layout_pers.addWidget(btn_guardar)

        layout_pers.addWidget(QLabel("Lista de Presets Personalizados:"))
        self.list_personalizados = QListWidget()
        self._cargar_lista_personalizados()
        layout_pers.addWidget(self.list_personalizados)

        self.tabs.addTab(tab_pers, "Personalizados")
        layout.addWidget(self.tabs)

        # Botones Inferiores de Accion
        layout_btn = QHBoxLayout()
        btn_cargar = QPushButton("Cargar Ecuacion Seleccionada")
        btn_cargar.setStyleSheet("font-weight: bold;")
        btn_cargar.clicked.connect(self._cargar_seleccion)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)

        layout_btn.addStretch()
        layout_btn.addWidget(btn_cargar)
        layout_btn.addWidget(btn_cancelar)
        layout.addLayout(layout_btn)

    def _cargar_lista_personalizados(self):
        self.list_personalizados.clear()
        pers = self.storage.data.get("personalizados", [])
        if not pers:
            self.list_personalizados.addItem("No hay presets personalizados guardados.")
        else:
            for p in pers:
                item_text = f"{p['nombre']}  ->  {p['ecuacion']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, p['ecuacion'])
                self.list_personalizados.addItem(item)

    def _guardar_personalizado(self):
        nombre = self.input_nombre_pers.text().strip()
        ecuacion = self.input_eq_pers.text().strip()
        if not nombre or not ecuacion:
            QMessageBox.warning(self, "Campos Incompletos", "Por favor ingresa un nombre y una ecuacion valida.")
            return

        ok = self.storage.agregar_personalizado(nombre, ecuacion)
        if ok:
            QMessageBox.information(self, "Preset Guardado", f"Se ha guardado el preset '{nombre}' correctamente.")
            self.input_nombre_pers.clear()
            self._cargar_lista_personalizados()

    def _cargar_seleccion(self):
        idx = self.tabs.currentIndex()
        eq_final = None

        if idx == 0:
            item = self.list_presets.currentItem()
            if item:
                eq_final = item.data(Qt.UserRole)
        elif idx == 1:
            item = self.list_historial.currentItem()
            if item:
                eq_final = item.data(Qt.UserRole)
        elif idx == 2:
            item = self.list_personalizados.currentItem()
            if item:
                eq_final = item.data(Qt.UserRole)
            elif self.input_eq_pers.text().strip():
                eq_final = self.input_eq_pers.text().strip()

        if eq_final:
            self.ecuacion_seleccionada.emit(eq_final)
            self.accept()
        else:
            QMessageBox.warning(self, "Sin Seleccion", "Por favor selecciona una ecuacion de la lista.")
