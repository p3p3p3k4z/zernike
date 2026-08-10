"""
build_packages.py
=================
Script de automatización para generar paquetes de distribución Linux:
- Paquete Debian / Ubuntu (.deb) utilizando dpkg-deb.
- Paquete Fedora / RHEL (.rpm) mediante alien o fpm si están disponibles.
"""

import os
import sys
import shutil
import subprocess
import platform


VERSION = "1.0.0"
APP_NAME = "zernike-gui"
DEB_DIR_NAME = f"{APP_NAME}_{VERSION}_amd64"


def verificar_binario_base():
    """Comprueba que exista el ejecutable binario en dist/zernike-gui."""
    binario_path = os.path.join("dist", APP_NAME)
    if not os.path.exists(binario_path):
        print(f"ERROR: No se encontró el binario base en '{binario_path}'.")
        print("Ejecuta primero: uv run python build_executable.py")
        sys.exit(1)
    return os.path.abspath(binario_path)


def crear_paquete_deb():
    """Genera la estructura de directorios y empaqueta el archivo .deb mediante dpkg-deb."""
    print(f"\n--- Generando paquete Debian/Ubuntu (.deb) v{VERSION} ---")
    binario_abs = verificar_binario_base()
    deb_root = os.path.join("dist", DEB_DIR_NAME)

    if os.path.exists(deb_root):
        shutil.rmtree(deb_root, ignore_errors=True)

    # Estructura del paquete .deb
    debian_dir = os.path.join(deb_root, "DEBIAN")
    bin_dir = os.path.join(deb_root, "usr", "bin")
    apps_dir = os.path.join(deb_root, "usr", "share", "applications")
    icons_dir = os.path.join(deb_root, "usr", "share", "icons", "hicolor", "256x256", "apps")
    pixmaps_dir = os.path.join(deb_root, "usr", "share", "pixmaps")
    
    os.makedirs(debian_dir, exist_ok=True)
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(apps_dir, exist_ok=True)
    os.makedirs(icons_dir, exist_ok=True)
    os.makedirs(pixmaps_dir, exist_ok=True)

    # Copiar binario ejecutable
    target_bin = os.path.join(bin_dir, APP_NAME)
    shutil.copy2(binario_abs, target_bin)
    os.chmod(target_bin, 0o755)

    # Copiar icono gráfico desde assets/icon.png
    src_icon = os.path.abspath(os.path.join("assets", "icon.png"))
    if os.path.exists(src_icon):
        shutil.copy2(src_icon, os.path.join(icons_dir, f"{APP_NAME}.png"))
        shutil.copy2(src_icon, os.path.join(pixmaps_dir, f"{APP_NAME}.png"))
        print(f"Icono gráfico copiado a la estructura del paquete.")

    # Crear archivo DEBIAN/control
    control_content = f"""Package: {APP_NAME}
Version: {VERSION}
Section: science
Priority: optional
Architecture: amd64
Maintainer: Zernike Project <m4r10@zernike.org>
Description: Ajuste y Descomposición de Polinomios de Zernike (ISO 10110-5)
 Aplicación de escritorio metrológica para el cálculo de aberraciones ópticas,
 interferometría 2D (Takeda FFT) y mapas tridimensionales de error residual.
"""
    with open(os.path.join(debian_dir, "control"), "w", encoding="utf-8") as f:
        f.write(control_content)

    # Crear lanzador .desktop vinculando el icono zernike-gui
    desktop_content = f"""[Desktop Entry]
Name=Zernike Metrology GUI
Comment=Ajuste de Polinomios de Zernike e Interferometría 2D
Exec=/usr/bin/{APP_NAME}
Icon={APP_NAME}
Terminal=false
Type=Application
Categories=Science;Engineering;Physics;
"""
    with open(os.path.join(apps_dir, f"{APP_NAME}.desktop"), "w", encoding="utf-8") as f:
        f.write(desktop_content)

    # Construir paquete .deb con dpkg-deb
    output_deb = os.path.join("dist", f"{DEB_DIR_NAME}.deb")
    if os.path.exists(output_deb):
        os.remove(output_deb)

    try:
        subprocess.run(["dpkg-deb", "--build", deb_root, output_deb], check=True)
        print(f"ÉXITO: Paquete Debian generado en: {output_deb}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Advertencia: No se pudo ejecutar dpkg-deb automáticamente ({e}).")

    # Limpiar carpeta temporal del paquete
    shutil.rmtree(deb_root, ignore_errors=True)


def crear_paquete_rpm():
    """Genera paquete .rpm utilizando fpm o alien si están instalados en el sistema."""
    deb_path = os.path.join("dist", f"{DEB_DIR_NAME}.deb")
    output_rpm = os.path.join("dist", f"{APP_NAME}-{VERSION}-1.x86_64.rpm")

    if not os.path.exists(deb_path):
        print("Aviso: No se puede generar RPM porque falta el paquete .deb base.")
        return

    print(f"\n--- Generando paquete Fedora/RHEL (.rpm) ---")

    # Limpiar archivo RPM previo si existe
    if os.path.exists(output_rpm):
        try:
            os.remove(output_rpm)
        except OSError:
            pass

    # Intentar con fpm
    if shutil.which("fpm"):
        try:
            subprocess.run([
                "fpm", "-f", "-s", "deb", "-t", "rpm",
                "--package", output_rpm, deb_path
            ], check=True)
            print(f"ÉXITO: Paquete RPM generado en: {output_rpm}")
            return
        except subprocess.CalledProcessError as err:
            print(f"Error al ejecutar fpm: {err}")

    # Intentar con alien
    if shutil.which("alien"):
        try:
            deb_filename = f"{DEB_DIR_NAME}.deb"
            subprocess.run(["alien", "--to-rpm", deb_filename], cwd="dist", check=True)
            print("ÉXITO: Convertido a RPM mediante alien.")
            return
        except subprocess.CalledProcessError as err:
            print(f"Error al ejecutar alien: {err}")

    print(f"Info: Para generar el ejecutable .rpm en Fedora/RHEL, se utiliza la GitHub Action automatizada.")


if __name__ == "__main__":
    if platform.system() != "Linux":
        print("Este script empaqueta instaladores nativos para Linux (.deb, .rpm).")
        sys.exit(0)

    crear_paquete_deb()
    crear_paquete_rpm()
