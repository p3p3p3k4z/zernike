"""
gui/worker.py
=============
Worker en segundo plano (QThread) para ejecutar los calculos matematicos 
pesados de Zernike sin bloquear el hilo principal de la interfaz grafica.
"""

import numpy as np
from PySide6.QtCore import QThread, Signal

from lib.zernike import polinomios_zernike, ajuste_completo
from lib.matriz import (
    generar_malla_ccd, centrar_coordenadas, filtrar_pupila,
    parsear_ecuacion_z, generar_datos_circulo, normalizar_vector
)
from lib.io import cargar_datos_csv


class ZernikeWorker(QThread):
    """
    Worker asíncrono que procesa el filtrado de pupila y la ortogonalización 
    de Gram-Schmidt en un hilo secundario.
    """
    progreso_actualizado = Signal(int, str)
    calculo_finalizado = Signal(object, object, object, object, object, object, object, object)
    calculo_error = Signal(str)

    def __init__(self, modo: int, eq_str: str = "", N: int = 100, M: int = 100,
                 diametro: float = 100.0, filepath: str = "", parent=None):
        super().__init__(parent)
        self.modo = modo
        self.eq_str = eq_str
        self.N = N
        self.M = M
        self.diametro = diametro
        self.filepath = filepath

    def run(self):
        try:
            self.progreso_actualizado.emit(20, "Generando malla de coordenadas y evaluando función...")
            polinomios = polinomios_zernike()
            k = 5

            if self.modo == 0:  # CCD Sensor
                if not self.eq_str:
                    raise ValueError("La ecuación Z(x,y) no puede estar vacía.")
                if self.N < 5 or self.M < 5:
                    raise ValueError("Las dimensiones Filas(N) y Columnas(M) deben ser mayores o iguales a 5.")
                if self.diametro <= 0:
                    raise ValueError("El diámetro de la pupila debe ser mayor a 0 píxeles.")

                func_z = parsear_ecuacion_z(self.eq_str)
                X_pix, Y_pix, Z_raw = generar_malla_ccd(self.N, self.M, func_z=func_z)
                X_c, Y_c = centrar_coordenadas(X_pix, Y_pix, self.N, self.M)
                datos_pupila = filtrar_pupila(X_c, Y_c, Z_raw, self.diametro)

                if datos_pupila['mascara'].sum() == 0:
                    raise ValueError(f"Ningún punto del sensor de {self.N}x{self.M} px quedó dentro de la pupila de diámetro {self.diametro}px.")

                if func_z is not None:
                    datos_pupila['Z_norm'] = func_z(datos_pupila['X_norm'], datos_pupila['Y_norm'])

                X_in, Y_in, W_in = datos_pupila['X_norm'], datos_pupila['Y_norm'], datos_pupila['Z_norm']
                X_raw_all, Y_raw_all, mask_all, R_pup = X_c, Y_c, datos_pupila['mascara'], datos_pupila['R']

            elif self.modo == 1:  # CSV Experimental
                if not self.filepath:
                    raise ValueError("Selecciona un archivo CSV existente antes de ejecutar.")

                X_raw, Y_raw, Z_raw = cargar_datos_csv(self.filepath)
                if X_raw is None:
                    raise ValueError("El archivo CSV debe contener los encabezados 'X', 'Y', 'Z'.")

                diametro_calc = 2.0 * np.sqrt(X_raw**2 + Y_raw**2).max()
                datos_pupila = filtrar_pupila(X_raw, Y_raw, Z_raw, diametro_calc)
                X_in, Y_in, W_in = datos_pupila['X_norm'], datos_pupila['Y_norm'], datos_pupila['Z_norm']
                X_raw_all, Y_raw_all, mask_all, R_pup = X_raw, Y_raw, datos_pupila['mascara'], datos_pupila['R']

            else:  # Circulo Sintetico
                X_in, Y_in, W_in = generar_datos_circulo(N=100, semilla=42)
                W_in = normalizar_vector(W_in)
                X_raw_all, Y_raw_all, mask_all, R_pup = X_in, Y_in, np.ones(len(X_in), dtype=bool), 1.0

            self.progreso_actualizado.emit(60, "Calculando base ortogonal mediante Gram-Schmidt...")

            resultados = ajuste_completo(X_in, Y_in, W_in, polinomios, k)

            self.progreso_actualizado.emit(90, "Finalizando procesamiento de matriz...")

            self.calculo_finalizado.emit(
                resultados, W_in, X_in, Y_in,
                X_raw_all, Y_raw_all, mask_all, R_pup
            )

        except Exception as e:
            self.calculo_error.emit(str(e))
