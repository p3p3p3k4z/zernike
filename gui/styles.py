"""
gui/styles.py
=============
Modulo de gestion de estilos CSS y temas visuales (Claro y Tema Nord Oscuro para Linux Terminal) 
para la interfaz de Zernike.
Incluye soporte completo y uniforme para QMenuBar, QMenu, QTableWidget, QDialog, QMessageBox y tarjetas de estado.
"""

import matplotlib.pyplot as plt


def obtener_estilo_tema(tema="claro") -> str:
    """Devuelve la hoja de estilo CSS segun el tema seleccionado ('claro' u 'oscuro' - Nord Theme)."""
    if tema == "claro":
        return """
            QMainWindow, QDialog, QMessageBox {
                background-color: #F8FAFC;
                color: #0F172A;
            }

            QWidget {
                color: #0F172A;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QLabel, QMessageBox QLabel {
                color: #0F172A;
                font-weight: 500;
            }
            QTextEdit {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QMenuBar {
                background-color: #FFFFFF;
                color: #0F172A;
                border-bottom: 1px solid #CBD5E1;
                font-size: 13px;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #0F172A;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #F1F5F9;
                color: #1E3A8A;
                border-radius: 4px;
            }
            QMenu {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                background-color: transparent;
                color: #0F172A;
                padding: 6px 24px 6px 10px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
            }
            QMenu::separator {
                height: 1px;
                background-color: #CBD5E1;
                margin: 4px 0px;
            }
            QGroupBox {
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                margin-top: 14px;
                font-weight: 700;
                font-size: 13px;
                color: #1E3A8A;
                background-color: #FFFFFF;
                padding: 16px 10px 10px 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 8px;
                background-color: #EFF6FF;
                border: 1px solid #DBEAFE;
                border-radius: 4px;
                color: #1E3A8A;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #94A3B8;
                border-radius: 6px;
                padding: 6px 10px;
                color: #0F172A;
                font-size: 13px;
                selection-background-color: #2563EB;
                selection-color: #FFFFFF;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #2563EB;
                background-color: #F8FAFC;
            }
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                font-weight: 600;
                font-size: 13px;
                border-radius: 6px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton#btn_preset {
                background-color: #F1F5F9;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                font-weight: 600;
                padding: 5px 8px;
                font-size: 11px;
            }
            QPushButton#btn_preset:hover {
                background-color: #DBEAFE;
                color: #1E3A8A;
                border-color: #93C5FD;
            }
            QTabWidget::pane {
                border: 1px solid #CBD5E1;
                background-color: #FFFFFF;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #E2E8F0;
                color: #334155;
                padding: 9px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 3px;
                font-weight: 600;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #1E3A8A;
                font-weight: 700;
                border-top: 3px solid #2563EB;
            }
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                gridline-color: #CBD5E1;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                font-size: 12px;
                selection-background-color: #DBEAFE;
                selection-color: #1E3A8A;
            }
            QTableWidget::item {
                background-color: #FFFFFF;
                color: #0F172A;
            }
            QTableWidget::item:alternate {
                background-color: #F8FAFC;
                color: #0F172A;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E3A8A;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                color: #1E3A8A;
                padding: 7px;
                border: 1px solid #CBD5E1;
                font-weight: 700;
                font-size: 12px;
            }
            QCheckBox {
                color: #0F172A;
                font-weight: 500;
            }
            QStatusBar {
                background-color: #F1F5F9;
                color: #334155;
                border-top: 1px solid #CBD5E1;
                font-weight: 500;
            }
            QToolTip {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #475569;
                padding: 5px 8px;
                border-radius: 4px;
                font-size: 12px;
            }
        """
    else:
        # Tema Oscuro Nord (Nord Theme Palette: Nord0..Nord15)
        return """
            QMainWindow, QDialog, QMessageBox {
                background-color: #2E3440;
                color: #ECEFF4;
            }

            QWidget {
                color: #ECEFF4;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QLabel, QMessageBox QLabel {
                color: #ECEFF4;
                font-weight: 500;
            }
            QTextEdit {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QMenuBar {
                background-color: #2E3440;
                color: #ECEFF4;
                border-bottom: 1px solid #4C566A;
                font-size: 13px;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #ECEFF4;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #3B4252;
                color: #88C0D0;
                border-radius: 4px;
            }
            QMenu {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                background-color: transparent;
                color: #ECEFF4;
                padding: 6px 24px 6px 10px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #5E81AC;
                color: #ECEFF4;
            }
            QMenu::separator {
                height: 1px;
                background-color: #4C566A;
                margin: 4px 0px;
            }
            QGroupBox {
                border: 1px solid #4C566A;
                border-radius: 8px;
                margin-top: 14px;
                font-weight: 700;
                font-size: 13px;
                color: #88C0D0;
                background-color: #3B4252;
                padding: 16px 10px 10px 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 8px;
                background-color: #2E3440;
                border: 1px solid #4C566A;
                border-radius: 4px;
                color: #88C0D0;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #2E3440;
                border: 1px solid #4C566A;
                border-radius: 6px;
                padding: 6px 10px;
                color: #ECEFF4;
                font-size: 13px;
                selection-background-color: #5E81AC;
                selection-color: #ECEFF4;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #88C0D0;
                background-color: #3B4252;
            }
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                font-weight: 600;
                font-size: 13px;
                border-radius: 6px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #81A1C1;
                color: #2E3440;
            }
            QPushButton:pressed {
                background-color: #4C566A;
                color: #ECEFF4;
            }
            QPushButton#btn_preset {
                background-color: #434C5E;
                color: #E5E9F0;
                border: 1px solid #4C566A;
                font-weight: 600;
                padding: 5px 8px;
                font-size: 11px;
            }
            QPushButton#btn_preset:hover {
                background-color: #5E81AC;
                color: #ECEFF4;
                border-color: #88C0D0;
            }
            QTabWidget::pane {
                border: 1px solid #4C566A;
                background-color: #3B4252;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2E3440;
                color: #D8DEE9;
                padding: 9px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 3px;
                font-weight: 600;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #3B4252;
                color: #88C0D0;
                font-weight: 700;
                border-top: 3px solid #88C0D0;
            }
            QTableWidget {
                background-color: #3B4252;
                alternate-background-color: #2E3440;
                gridline-color: #4C566A;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                font-size: 12px;
                selection-background-color: #434C5E;
                selection-color: #88C0D0;
            }
            QTableWidget::item {
                background-color: #3B4252;
                color: #ECEFF4;
            }
            QTableWidget::item:alternate {
                background-color: #2E3440;
                color: #ECEFF4;
            }
            QTableWidget::item:selected {
                background-color: #434C5E;
                color: #88C0D0;
            }
            QHeaderView::section {
                background-color: #2E3440;
                color: #88C0D0;
                padding: 7px;
                border: 1px solid #4C566A;
                font-weight: 700;
                font-size: 12px;
            }
            QCheckBox {
                color: #ECEFF4;
                font-weight: 500;
            }
            QStatusBar {
                background-color: #2E3440;
                color: #D8DEE9;
                border-top: 1px solid #4C566A;
                font-weight: 500;
            }
            QToolTip {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #88C0D0;
                padding: 5px 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                selection-background-color: #5E81AC;
                selection-color: #ECEFF4;
                outline: 0;
            }
            QFileDialog, QFileDialog QWidget {
                background-color: #2E3440;
                color: #ECEFF4;
            }
            QFileDialog QListView, QFileDialog QTreeView, QFileDialog QTextEdit {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
            }
            QFileDialog QHeaderView::section {
                background-color: #2E3440;
                color: #88C0D0;
            }
            QListView, QTreeView {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
            }
            QScrollBar:vertical {
                background-color: #2E3440;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #4C566A;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5E81AC;
            }
            QScrollBar:horizontal {
                background-color: #2E3440;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #4C566A;
                min-width: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #5E81AC;
            }
        """



def aplicar_estilo_rms_card(card_rms, lbl_titulo, lbl_rms, lbl_desc, tema="claro"):
    """Actualiza la apariencia visual de la tarjeta de resultado RMS segun el tema."""
    if tema == "claro":
        card_rms.setStyleSheet("background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 6px; padding: 10px;")
        lbl_titulo.setStyleSheet("font-size: 12px; font-weight: bold; color: #1E40AF;")
        lbl_rms.setStyleSheet("font-size: 14px; font-weight: bold; color: #1D4ED8;")
        lbl_desc.setStyleSheet("font-size: 11px; color: #475569;")
    else:
        card_rms.setStyleSheet("background-color: #3B4252; border: 1px solid #4C566A; border-radius: 6px; padding: 10px;")
        lbl_titulo.setStyleSheet("font-size: 12px; font-weight: bold; color: #88C0D0;")
        lbl_rms.setStyleSheet("font-size: 14px; font-weight: bold; color: #81A1C1;")
        lbl_desc.setStyleSheet("font-size: 11px; color: #D8DEE9;")


def obtener_paleta_tema(tema="claro") -> dict:
    """Devuelve un diccionario centralizado con la paleta de colores y tokens visuales del tema."""
    if tema == "oscuro":
        return {
            "bg": "#2E3440",
            "fg": "#ECEFF4",
            "card_bg": "#3B4252",
            "border": "#4C566A",
            "header_bg": "#2E3440",
            "header_fg": "#88C0D0",
            "input_bg": "#2E3440",
            "input_fg": "#ECEFF4",
            "empty_bg": "#2E3440",
            "empty_border": "#4C566A",
            "accent": "#88C0D0",
            "accent_secondary": "#81A1C1",
            "code_bg": "#2E3440",
            "code_color": "#88C0D0",
            "hr_color": "#4C566A",
            "body_color": "#D8DEE9",
            "h2_color": "#88C0D0",
            "h3_color": "#81A1C1",
        }
    return {
        "bg": "#F8FAFC",
        "fg": "#0F172A",
        "card_bg": "#FFFFFF",
        "border": "#CBD5E1",
        "header_bg": "#EFF6FF",
        "header_fg": "#1E3A8A",
        "input_bg": "#FFFFFF",
        "input_fg": "#0F172A",
        "empty_bg": "#F8FAFC",
        "empty_border": "#CBD5E1",
        "accent": "#1E3A8A",
        "accent_secondary": "#1D4ED8",
        "code_bg": "#F1F5F9",
        "code_color": "#1E3A8A",
        "hr_color": "#CBD5E1",
        "body_color": "#0F172A",
        "h2_color": "#1E3A8A",
        "h3_color": "#1E40AF",
    }
