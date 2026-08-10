"""
build_executable.py
===================
Script de automatizacion para empaquetar Zernike GUI en un ejecutable standalone
utilizando PyInstaller y gestor de entornos uv.
"""

import sys
import os
import shutil
import platform
import PyInstaller.__main__


def limpiar_directorios_previos():
    """Elimina carpetas temporales de compilacion del ejecutable actual."""
    if os.path.exists('build_app'):
        print("Limpiando directorio de trabajo temporal: build_app")
        shutil.rmtree('build_app', ignore_errors=True)

    # Eliminar binarios zernike-gui previos en dist si existen
    for archivo in ['zernike-gui', 'zernike-gui.exe']:
        ruta_archivo = os.path.join('dist', archivo)
        if os.path.exists(ruta_archivo):
            print(f"Eliminando ejecutable previo: {ruta_archivo}")
            try:
                os.remove(ruta_archivo)
            except OSError as error:
                print(f"Advertencia al eliminar {ruta_archivo}: {error}")


def compilar_ejecutable():
    """Ejecuta PyInstaller con el archivo spec de configuracion."""
    spec_path = os.path.abspath('zernike_gui.spec')
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"No se encontro el archivo de especificacion: {spec_path}")

    print("Iniciando empaquetado de Zernike GUI con PyInstaller...")
    limpiar_directorios_previos()

    PyInstaller.__main__.run([
        spec_path,
        '--workpath=build_app',
        '--distpath=dist',
        '--clean',
        '--noconfirm',
    ])

    # Verificacion del binario generado
    sistema = platform.system()
    nombre_ejecutable = 'zernike-gui.exe' if sistema == 'Windows' else 'zernike-gui'
    ejecutable_path = os.path.join('dist', nombre_ejecutable)

    if os.path.exists(ejecutable_path):
        tamano_mb = os.path.getsize(ejecutable_path) / (1024 * 1024)
        print(f"\n==========================================")
        print(f"COMPILACION EXITOSA")
        print(f"Sistema Operativo: {sistema}")
        print(f"Ejecutable generado: {ejecutable_path}")
        print(f"Tamaño final: {tamano_mb:.2f} MB")
        print(f"==========================================\n")
    else:
        raise RuntimeError(f"Error: El ejecutable no fue encontrado en {ejecutable_path}")


if __name__ == '__main__':
    compilar_ejecutable()
