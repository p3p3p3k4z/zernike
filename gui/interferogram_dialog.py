"""
gui/interferogram_dialog.py
============================
Cuadro de diálogo interactivo en PySide6 para el procesamiento digital de interferogramas,
visualización del espectro de Fourier 2D, demodulación de fase y extracción de puntos para Zernike.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QDoubleSpinBox, QLabel, QFileDialog, QMessageBox, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal

from gui.canvas import MplCanvasWidget
from lib.interferometria import (
    cargar_y_normalizar_imagen, demodular_fase_fft2d,
    desenvolver_fase_2d, extraer_esqueleto_franjas,
    generar_interferograma_sintetico, aplicar_mascara_circular,
    recortar_y_limpiar_interferograma, extraer_puntos_pupila_circular
)


class InterferogramProcessorDialog(QDialog):
    """
    Diálogo interactivo para cargar interferogramas en imagen,
    visualizar el dominio espectral 2D (Takeda) y enviar los puntos (X, Y, Z) al panel principal.
    """
    puntos_extraidos_signal = Signal(object, object, object)  # Emite (X_in, Y_in, W_in)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesador de Interferogramas — Extracción de Fase (Takeda 2D / Esqueleto)")
        self.resize(1000, 700)

        if parent is not None and hasattr(parent, 'styleSheet'):
            self.setStyleSheet(parent.styleSheet())

        self.matriz_img = None
        self.X_extraido = None
        self.Y_extraido = None
        self.W_extraido = None

        self._construir_ui()
        self._generar_interferograma_sintetico()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 1. Barra de Herramientas y Controles
        grupo_controles = QGroupBox("Controles de Procesamiento de Interferograma")
        layout_controles = QHBoxLayout(grupo_controles)

        self.btn_cargar = QPushButton("Cargar Imagen (PNG, JPG)...")
        self.btn_cargar.clicked.connect(self._cargar_imagen_archivo)
        layout_controles.addWidget(self.btn_cargar)

        self.btn_sintetico = QPushButton("Generar Sintético")
        self.btn_sintetico.clicked.connect(self._generar_interferograma_sintetico)
        layout_controles.addWidget(self.btn_sintetico)

        layout_controles.addWidget(QLabel("Método:"))
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems([
            "Transformada de Fourier 2D (Takeda et al., 1982)",
            "Esqueleto de Franjas (Crestas de Intensidad)"
        ])
        self.combo_metodo.currentIndexChanged.connect(self._procesar_interferograma)
        layout_controles.addWidget(self.combo_metodo)

        layout_controles.addWidget(QLabel("Filtro Espectral:"))
        self.spin_filtro = QDoubleSpinBox()
        self.spin_filtro.setRange(0.05, 0.45)
        self.spin_filtro.setSingleStep(0.02)
        self.spin_filtro.setValue(0.15)
        self.spin_filtro.valueChanged.connect(self._procesar_interferograma)
        layout_controles.addWidget(self.spin_filtro)

        self.chk_autocrop = QCheckBox("Limpiar Fondo Oscuro & Recortar Pupila")
        self.chk_autocrop.setChecked(True)
        self.chk_autocrop.stateChanged.connect(self._procesar_interferograma)
        layout_controles.addWidget(self.chk_autocrop)

        layout.addWidget(grupo_controles)

        # 2. Canvas Matplotlib 2x2 para Visualizacion
        self.canvas = MplCanvasWidget(self)
        layout.addWidget(self.canvas, stretch=1)

        # 3. Barra Inferior de Estado e Importación
        layout_inferior = QHBoxLayout()

        self.lbl_info = QLabel("Estado: Listo para procesar.")
        self.lbl_info.setStyleSheet("font-weight: bold; font-size: 11px;")
        layout_inferior.addWidget(self.lbl_info)

        layout_inferior.addStretch()

        self.btn_importar = QPushButton("Enviar Puntos al Panel Principal")
        self.btn_importar.setStyleSheet("font-weight: bold; background-color: #2563EB; color: white; padding: 6px 14px;")
        self.btn_importar.clicked.connect(self._importar_puntos)
        layout_inferior.addWidget(self.btn_importar)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.accept)
        layout_inferior.addWidget(self.btn_cerrar)

        layout.addLayout(layout_inferior)

    def _cargar_imagen_archivo(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen de Interferograma", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        if filepath:
            try:
                self.matriz_img = cargar_y_normalizar_imagen(filepath)
                self._procesar_interferograma()
            except Exception as e:
                QMessageBox.critical(self, "Error de Carga", f"No se pudo cargar la imagen:\n{str(e)}")

    def _generar_interferograma_sintetico(self):
        img, _, _, _ = generar_interferograma_sintetico(N=200, franjas_carrier=10)
        self.matriz_img = img
        self._procesar_interferograma()

    def _procesar_interferograma(self):
        if self.matriz_img is None:
            return

        if self.chk_autocrop.isChecked():
            matriz_proc, _ = recortar_y_limpiar_interferograma(self.matriz_img, umbral_fondo=0.06)
        else:
            matriz_proc = self.matriz_img

        metodo_idx = self.combo_metodo.currentIndex()
        radio_filtro = self.spin_filtro.value()

        is_dark = (self.parent() is not None and getattr(self.parent(), 'tema_actual', 'claro') == 'oscuro')
        bg_color = '#2E3440' if is_dark else '#FFFFFF'
        text_color = '#ECEFF4' if is_dark else '#0F172A'

        # Crear figura directamente con Figure() para no registrarla en pyplot (Gcf),
        # evitando la aparicion de ventanas nativas vacias (FigureManagerQT) en Windows.
        fig = Figure(figsize=(9, 6), facecolor=bg_color)

        if metodo_idx == 0:  # Fourier 2D (Takeda)
            fase_enrollada, espectro_log, mascara_filtro = demodular_fase_fft2d(matriz_proc, radio_filtro)
            fase_continua = desenvolver_fase_2d(fase_enrollada)

            self.X_extraido, self.Y_extraido, self.W_extraido, _ = extraer_puntos_pupila_circular(
                fase_continua, matriz_proc, radio_pct=0.96
            )

            # Visualizacion 2x2
            ax1 = fig.add_subplot(221, facecolor=bg_color)
            im1 = ax1.imshow(matriz_proc, cmap='gray', origin='lower')
            ax1.set_title("1. Interferograma Limpiado", fontsize=10, fontweight='bold', color=text_color)
            ax1.tick_params(colors=text_color)
            cb1 = fig.colorbar(im1, ax=ax1)
            cb1.ax.tick_params(colors=text_color)

            ax2 = fig.add_subplot(222, facecolor=bg_color)
            im2 = ax2.imshow(espectro_log, cmap='magma', origin='lower')
            if mascara_filtro is not None:
                ax2.contour(mascara_filtro, levels=[0.5], colors='cyan', linewidths=1.5)
            ax2.set_title("2. Espectro FFT 2D & Filtro", fontsize=10, fontweight='bold', color=text_color)
            ax2.tick_params(colors=text_color)
            cb2 = fig.colorbar(im2, ax=ax2)
            cb2.ax.tick_params(colors=text_color)

            ax3 = fig.add_subplot(223, facecolor=bg_color)
            im3 = ax3.imshow(fase_enrollada, cmap='twilight', origin='lower')
            ax3.set_title("3. Fase Enrollada [-pi, +pi]", fontsize=10, fontweight='bold', color=text_color)
            ax3.tick_params(colors=text_color)
            cb3 = fig.colorbar(im3, ax=ax3)
            cb3.ax.tick_params(colors=text_color)

            ax4 = fig.add_subplot(224, facecolor=bg_color)
            im4 = ax4.imshow(fase_continua, cmap='viridis', origin='lower', extent=[-1, 1, -1, 1])
            if len(self.X_extraido) > 0:
                idx_sample = np.random.choice(len(self.X_extraido), size=min(1000, len(self.X_extraido)), replace=False)
                ax4.scatter(self.X_extraido[idx_sample], self.Y_extraido[idx_sample], s=2, c='cyan', alpha=0.5, label=f'Puntos ({len(self.X_extraido)})')
            ax4.set_title(f"4. Puntos Extraídos ({len(self.X_extraido)} pts)", fontsize=10, fontweight='bold', color=text_color)
            ax4.tick_params(colors=text_color)
            leg = ax4.legend(loc='upper right', fontsize=8)
            if leg:
                leg.get_frame().set_facecolor(bg_color)
                for text in leg.get_texts():
                    text.set_color(text_color)
            cb4 = fig.colorbar(im4, ax=ax4)
            cb4.ax.tick_params(colors=text_color)

        else:  # Esqueleto por crestas
            X_pts, Y_pts, Z_pts = extraer_esqueleto_franjas(matriz_proc, umbral_pct=0.5)
            self.X_extraido = X_pts
            self.Y_extraido = Y_pts
            self.W_extraido = Z_pts

            ax1 = fig.add_subplot(121, facecolor=bg_color)
            im1 = ax1.imshow(matriz_proc, cmap='gray', origin='lower')
            ax1.set_title("1. Interferograma Limpiado", fontsize=10, fontweight='bold', color=text_color)
            ax1.tick_params(colors=text_color)
            cb1 = fig.colorbar(im1, ax=ax1)
            cb1.ax.tick_params(colors=text_color)

            ax2 = fig.add_subplot(122, facecolor=bg_color)
            sc = ax2.scatter(X_pts, Y_pts, c=Z_pts, s=8, cmap='jet')
            ax2.set_title(f"2. Esqueleto ({len(X_pts)} Puntos Extraídos)", fontsize=10, fontweight='bold', color=text_color)
            ax2.set_xlim(-1, 1)
            ax2.set_ylim(-1, 1)
            ax2.set_aspect('equal')
            ax2.tick_params(colors=text_color)
            cb2 = fig.colorbar(sc, ax=ax2)
            cb2.ax.tick_params(colors=text_color)

        fig.tight_layout()
        self.canvas.set_figure(fig)

        self.lbl_info.setText(f"Puntos Extraídos: {len(self.X_extraido)} | Rango Fase: [{np.nanmin(self.W_extraido):.3f}, {np.nanmax(self.W_extraido):.3f}]")

        # Emitir señal de puntos actualizados automáticamente
        self.puntos_extraidos_signal.emit(self.X_extraido, self.Y_extraido, self.W_extraido)

    def _importar_puntos(self):
        if self.X_extraido is None or len(self.X_extraido) == 0:
            QMessageBox.warning(self, "Sin Puntos", "No hay puntos de fase extraídos para importar.")
            return

        self.puntos_extraidos_signal.emit(self.X_extraido, self.Y_extraido, self.W_extraido)
        QMessageBox.information(
            self,
            "Puntos Enviados",
            f"Se enviaron {len(self.X_extraido)} puntos al panel principal.\n\n"
            "Haz clic en 'EJECUTAR AJUSTE DE ZERNIKE (Ctrl+E)' en la ventana principal para realizar el cálculo."
        )
        self.accept()
