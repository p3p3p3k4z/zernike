"""
lib/fortran_runner.py
=====================
Modulo ejecutor multiplataforma (Windows/Linux/macOS) para compilar
y ejecutar de forma aislada el nucleo de calculo de Zernike en Fortran.
"""

import os
import sys
import shutil
import subprocess
import numpy as np
from typing import Tuple, Optional
from lib.zernike import ResultadoZernike

DIR_FORTRAN_DEFAULT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fotrain_implemnt"))


def obtener_nombre_binario() -> str:
    """Retorna el nombre adecuado del ejecutable segun el sistema operativo."""
    return "zernike_app.exe" if sys.platform == "win32" else "zernike_app"


def verificar_gfortran() -> Optional[str]:
    """Verifica si gfortran esta disponible en el PATH del sistema operativo."""
    return shutil.which("gfortran")


def compilar_fortran(dir_fortran: str = DIR_FORTRAN_DEFAULT) -> Tuple[bool, str]:
    """
    Compila el archivo zernike_programa.f en un ejecutable binario local.
    """
    gfortran_path = verificar_gfortran()
    if not gfortran_path:
        msg_os = "En Windows instala MinGW/MSYS2 o gfortran." if sys.platform == "win32" else "Ejecuta: sudo apt install gfortran"
        return False, f"Compilador 'gfortran' no encontrado. {msg_os}"

    src_file = os.path.join(dir_fortran, "zernike_programa.f")
    bin_name = obtener_nombre_binario()
    bin_file = os.path.join(dir_fortran, bin_name)

    if not os.path.exists(src_file):
        return False, f"No se encontro el archivo fuente {src_file}"

    cmd = [gfortran_path, "-O3", "zernike_programa.f", "-o", bin_name]
    try:
        res = subprocess.run(cmd, cwd=dir_fortran, capture_output=True, text=True, check=True)
        return True, f"Compilacion exitosa: {bin_file}"
    except subprocess.CalledProcessError as e:
        return False, f"Error al compilar codigo Fortran:\n{e.stderr}"


def asegurar_binario_fortran(dir_fortran: str = DIR_FORTRAN_DEFAULT) -> Tuple[bool, str]:
    """
    Verifica que el binario exista; si no existe o esta desactualizado, lo compila.
    """
    bin_file = os.path.join(dir_fortran, obtener_nombre_binario())
    src_file = os.path.join(dir_fortran, "zernike_programa.f")

    if not os.path.exists(bin_file) or (os.path.exists(src_file) and os.path.getmtime(src_file) > os.path.getmtime(bin_file)):
        return compilar_fortran(dir_fortran)

    return True, "Binario Fortran listo."


def preparar_datos_entrada_dat(X: np.ndarray, Y: np.ndarray, W: np.ndarray, filepath: str):
    """
    Genera en memoria el archivo datos_entrada.dat con el centinela 10000.0.
    Reutiliza la abstraccion de datos de csv_to_fortran.py.
    """
    with open(filepath, 'w') as f:
        for x_val, y_val, w_val in zip(X, Y, W):
            f.write(f"{x_val:.8f} {y_val:.8f} {w_val:.8f}\n")
        f.write("10000.0 0.0 0.0\n")


def ejecutar_zernike_fortran(X: np.ndarray, Y: np.ndarray, W: np.ndarray, dir_fortran: str = DIR_FORTRAN_DEFAULT) -> ResultadoZernike:
    """
    Ejecuta el nucleo de Fortran de forma automatica y convierte la salida a ResultadoZernike.
    Soporta hasta 50,000 puntos de datos.
    """
    N = len(X)
    if N > 50000:
        raise ValueError(f"El motor Fortran admite un maximo de 50,000 puntos. Se recibieron {N} puntos.")

    ok, msg = asegurar_binario_fortran(dir_fortran)
    if not ok:
        raise RuntimeError(msg)

    dat_file = os.path.join(dir_fortran, "datos_entrada.dat")
    preparar_datos_entrada_dat(X, Y, W, dat_file)

    bin_name = obtener_nombre_binario()
    bin_path = os.path.join(dir_fortran, bin_name)

    # Invocar binario pasando datos_entrada.dat a stdin
    process = subprocess.Popen(
        [bin_path],
        cwd=dir_fortran,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate(input="datos_entrada.dat\n", timeout=15)

    if process.returncode != 0:
        raise RuntimeError(f"Error de ejecucion en el binario Fortran:\n{stderr}")

    # Parsear coeficientes A desde stdout
    A_list = []
    for line in stdout.splitlines():
        if line.strip().startswith("A_"):
            try:
                val_str = line.split("=")[1].strip()
                A_list.append(float(val_str))
            except (IndexError, ValueError):
                pass

    if len(A_list) < 15:
        raise RuntimeError("No se pudieron parsear los 15 coeficientes A del programa Fortran.")

    # Completar los coeficientes de 16 a 21 con 0.0 para mantener compatibilidad con L=21 (k=5)
    A_21 = np.zeros(21)
    A_21[:15] = np.array(A_list[:15])

    # Parsear INTER.DAT para obtener la reconstruccion W_fit y coordenadas procesadas
    inter_file = os.path.join(dir_fortran, "INTER.DAT")
    if not os.path.exists(inter_file):
        raise FileNotFoundError(f"No se creo el archivo de salida {inter_file}")

    fortran_rows = []
    with open(inter_file, 'r') as f:
        lines = f.readlines()
        for line in lines[2:]:
            parts = line.split()
            if len(parts) == 5:
                try:
                    fortran_rows.append([float(p) for p in parts])
                except ValueError:
                    pass

    arr = np.array(fortran_rows)
    if len(arr) == 0:
        raise RuntimeError("El archivo INTER.DAT esta vacio o corrompido.")

    X_proc = arr[:, 0]
    Y_proc = arr[:, 1]
    W_exp_proc = arr[:, 2]
    W_fit_proc = arr[:, 3]

    # Construir estructura inmutable de resultado
    resultado = ResultadoZernike(
        U=np.zeros((21, len(X_proc))),
        V=[],
        D=np.zeros((21, 21)),
        F=None,
        B=np.zeros(21),
        C=np.zeros((21, 21)),
        A=A_21,
        W_fit=W_fit_proc,
        X=X_proc,
        Y=Y_proc,
        W=W_exp_proc
    )

    return resultado
