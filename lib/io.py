import pandas as pd
import numpy as np
import os
import logging

logger = logging.getLogger("zernike")

def inicializar_logger(filename="python_output.txt"):
    """
    Inicializa el sistema de logging estándar de Python, configurando
    la salida tanto a consola como a un archivo, sin sobrescribir
    builtins.print globalmente.
    """
    logger.setLevel(logging.INFO)
    
    # Evitar duplicar handlers si se llama multiples veces
    if logger.hasHandlers():
        logger.handlers.clear()

    # Handler para consola
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    
    # Handler para archivo
    f_handler = logging.FileHandler(filename, mode="w", encoding="utf-8")
    f_handler.setLevel(logging.INFO)

    # Formato simple
    formatter = logging.Formatter('%(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    # Nota para el usuario sobre el cambio
    logger.info(f"--- Logger inicializado en archivo: {filename} ---")

def exportar_resultados_csv(X, Y, Z_exp, Z_fit, error, filepath='output/zernike_resultados.csv'):
    """
    Exporta los resultados del ajuste de Zernike a un archivo CSV.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df_export = pd.DataFrame({
            'X': X,
            'Y': Y,
            'Z_exp': Z_exp,
            'Z_fit': Z_fit,
            'Error': error
        })
        df_export.to_csv(filepath, index=False)
        print(f"  Resultados exportados a: {filepath}")
    except Exception as e:
        print(f"  No se pudo exportar a CSV: {e}")

def cargar_datos_csv(filepath):
    """
    Carga coordenadas X, Y, Z desde un archivo CSV.
    Retorna los arreglos numpy o (None, None, None) si falla.
    """
    try:
        df = pd.read_csv(filepath)
        if not all(col in df.columns for col in ['X', 'Y', 'Z']):
            print("  ERROR: El CSV debe contener las columnas 'X', 'Y', 'Z'.")
            return None, None, None
        return df['X'].values, df['Y'].values, df['Z'].values
    except Exception as e:
        print(f"  Error al leer el CSV: {e}")
        return None, None, None

def exportar_datos_iniciales_csv(X, Y, Z, filepath='output/datos_iniciales.csv'):
    """
    Exporta los datos (X, Y, Z) iniciales generados a un archivo CSV.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df_export = pd.DataFrame({
            'X': X,
            'Y': Y,
            'Z': Z
        })
        df_export.to_csv(filepath, index=False)
        print(f"  Datos iniciales exportados a: {filepath}")
    except Exception as e:
        print(f"  No se pudo exportar los datos iniciales a CSV: {e}")
