import pandas as pd
import numpy as np
import os
import logging

logger = logging.getLogger("zernike")

def _asegurar_directorio(filepath: str):
    """Crea la estructura de carpetas contenedora si filepath contiene una ruta de directorio."""
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)


def inicializar_logger(filename="output/zernike_app.log"):
    """
    Inicializa el sistema de logging estándar de Python, configurando
    la salida tanto a consola como a un archivo en la carpeta output/,
    sin sobrescribir builtins.print globalmente.
    """
    logger.setLevel(logging.INFO)
    
    # Evitar duplicar handlers si se llama multiples veces
    if logger.hasHandlers():
        logger.handlers.clear()

    # Handler para consola
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    
    # Handler para archivo
    _asegurar_directorio(filename)
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
        _asegurar_directorio(filepath)
        df_export = pd.DataFrame({
            'X': X,
            'Y': Y,
            'Z_exp': Z_exp,
            'Z_fit': Z_fit,
            'Error': error
        })
        df_export.to_csv(filepath, index=False)
        print(f"  Resultados exportados a: {filepath}")
    except (OSError, ValueError, KeyError) as e:
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
    except (OSError, ValueError, KeyError, pd.errors.EmptyDataError) as e:
        print(f"  Error al leer el CSV: {e}")
        return None, None, None

def exportar_datos_iniciales_csv(X, Y, Z, filepath='output/datos_iniciales.csv'):
    """
    Exporta los datos (X, Y, Z) iniciales generados a un archivo CSV.
    """
    try:
        _asegurar_directorio(filepath)
        df_export = pd.DataFrame({
            'X': X,
            'Y': Y,
            'Z': Z
        })
        df_export.to_csv(filepath, index=False)
        print(f"  Datos iniciales exportados a: {filepath}")
    except (OSError, ValueError, KeyError) as e:
        print(f"  No se pudo exportar los datos iniciales a CSV: {e}")



from lib.zernike import INFORMACION_ZERNIKE_ISO

_ZERNIKE_METADATA_ISO = [(info['n'], info['m'], info['nombre']) for info in INFORMACION_ZERNIKE_ISO]


def exportar_zemax(A, R_pupila=1.0, longitud_onda=0.6328, filepath='output/zemax_zernike.zrn'):
    """
    Exporta el vector de coeficientes de Zernike A en el formato nativo de Zemax OpticStudio (.zrn / .txt).

    Parametros
    ----------
    A             : ndarray (L,) o ResultadoZernike -- Coeficientes de Zernike (ISO 10110-5)
    R_pupila      : float                             -- Radio de la pupila de normalización en mm
    longitud_onda : float                             -- Longitud de onda de referencia en micras (ej. 0.6328 um)
    filepath      : str                               -- Ruta del archivo de salida (.zrn / .txt)
    """
    if hasattr(A, 'A'):
        A = A.A
    if isinstance(R_pupila, str):
        filepath = R_pupila
        R_pupila = 1.0

    try:
        _asegurar_directorio(filepath)
        L = len(A)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# ========================================================\n")
            f.write("# ZEMAX OpticStudio - Zernike Surface Coefficients File\n")
            f.write("# Norma: ISO 10110-5 / ANSI Z80.28\n")
            f.write("# ========================================================\n")
            f.write(f"PUPIL_RADIUS_MM      {R_pupila:.6f}\n")
            f.write(f"WAVELENGTH_UM        {longitud_onda:.6f}\n")
            f.write(f"NUM_COEFFICIENTS     {L}\n")
            f.write("# --------------------------------------------------------\n")
            f.write("# Index   n    m    Coefficient_A           Description\n")
            f.write("# --------------------------------------------------------\n")

            for r in range(L):
                if r < len(_ZERNIKE_METADATA_ISO):
                    n, m, desc = _ZERNIKE_METADATA_ISO[r]
                else:
                    n, m, desc = 0, 0, f"Orden Zernike Z_{r+1}"
                f.write(f"{r+1:5d}   {n:3d}  {m:4d}   {A[r]:+16.8e}   # {desc}\n")

        print(f"  Archivo Zemax OpticStudio exportado a: {filepath}")
        return True
    except Exception as e:
        print(f"  Error al exportar archivo Zemax: {e}")
        return False


def exportar_codev(A, R_pupila=1.0, filepath='output/codev_zernike.dat'):
    """
    Exporta el vector de coeficientes de Zernike A en el formato de datos de superficie de CODE V (.dat).

    Parametros
    ----------
    A        : ndarray (L,) o ResultadoZernike -- Coeficientes de Zernike (ISO 10110-5)
    R_pupila : float                             -- Radio de apertura / pupila de normalización
    filepath : str                               -- Ruta del archivo de salida (.dat / .txt)
    """
    if hasattr(A, 'A'):
        A = A.A
    if isinstance(R_pupila, str):
        filepath = R_pupila
        R_pupila = 1.0

    try:
        _asegurar_directorio(filepath)
        L = len(A)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("! CODE V Zernike Surface Data File\n")
            f.write(f"! Normalization Radius: {R_pupila:.6f}\n")
            f.write(f"NRAD {R_pupila:.6f}\n")
            f.write(f"ZFR {L}\n")

            for r in range(L):
                desc = _ZERNIKE_METADATA_ISO[r][2] if r < len(_ZERNIKE_METADATA_ISO) else f"Z_{r+1}"
                f.write(f"C{r+1:<3d} {A[r]:+18.10e} ! {desc}\n")

        print(f"  Archivo CODE V exportado a: {filepath}")
        return True
    except Exception as e:
        print(f"  Error al exportar archivo CODE V: {e}")
        return False


from lib.reportes import exportar_reporte_html



