import pandas as pd
import numpy as np
import os
import builtins

_original_print = builtins.print
_log_file = None

def inicializar_logger(filename="python_output.txt"):
    """
    Inicializa un log que duplica la salida de print hacia un archivo.
    No utiliza programación orientada a objetos.
    """
    global _log_file
    _log_file = open(filename, "w", encoding="utf-8")
    
    def log_print(*args, **kwargs):
        _original_print(*args, **kwargs)
        if _log_file is not None and not kwargs.get('file'):
            _original_print(*args, **kwargs, file=_log_file)
            _log_file.flush()
            
    builtins.print = log_print

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
