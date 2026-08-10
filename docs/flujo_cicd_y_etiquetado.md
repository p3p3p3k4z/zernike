# Guía de Automatización CI/CD, Empaquetado y Versionado Semántico (Git Tags)

Este documento detalla la arquitectura de integración continua (CI/CD), el proceso de empaquetado de ejecutables e instaladores nativos (`.exe`, `.deb`, `.rpm`) y la importancia fundamental de las **etiquetas de Git (Git Tags)** en el ciclo de vida del software.

---

## 1. Arquitectura del Flujo de Trabajo CI/CD

El proyecto utiliza **GitHub Actions** ([`.github/workflows/build_executables.yml`](../.github/workflows/build_executables.yml)) para automatizar la compilación y distribución de paquetes binarios precompilados de la interfaz gráfica Zernike GUI.

### Matriz de Compilación Paralela

El workflow ejecuta dos máquinas virtuales en paralelo:

1. **`ubuntu-latest` (Linux)**:
   - Sincroniza el entorno de dependencias utilizando `uv`.
   - Compila el binario ejecutable standalone para Linux mediante PyInstaller (`dist/zernike-gui`).
   - Construye el paquete Debian/Ubuntu (`.deb`) utilizando `dpkg-deb`.
   - Construye el paquete Fedora/RHEL (`.rpm`) mediante `alien`.

2. **`windows-latest` (Windows)**:
   - Sincroniza el entorno con `uv`.
   - Compila el ejecutable nativo portátil de Windows (`dist/zernike-gui.exe`).

### Publicación de Releases

Al finalizar ambas ejecuciones de compilación, el trabajo de publicación (`release`) agrupa los artefactos binarios y los adjunta automáticamente a la sección pública de **GitHub Releases**.

---

## 2. Importancia Fundamental del Etiquetado de Versiones (Git Tags)

El etiquetado de versiones mediante **Git Tags** es un estándar fundamental en la ingeniería de software y cumple los siguientes roles en este repositorio:

### A. Disparador Oficial de Publicación (*Release Trigger*)
El flujo de CI/CD está configurado para publicar automáticamente una nueva Release únicamente cuando se detecta la subida de una etiqueta que siga la convención de versión (por ejemplo, `v1.0.0`, `v1.1.0`). Los pushes regulares a ramas de desarrollo no sobreescriben publicaciones oficiales.

### B. Trazabilidad e Inmutabilidad
Un Git Tag asocia de forma inmutable una versión pública (`v1.0.0`) con la marca temporal y el hash exacto del código fuente (*commit hash*). Esto garantiza la auditabilidad científica y metrológica de los binarios distribuidos.

### C. Versionado Semántico (SemVer)
Se sigue el estándar internacional **SemVer** (`MAJOR.MINOR.PATCH`):
* **MAJOR** (ej. `v2.0.0`): Cambios estructurales incompatibles en las APIs o algoritmos base.
* **MINOR** (ej. `v1.1.0`): Incorporación de nuevas funcionalidades retrocompatibles (ej. nuevos tipos de análisis o soporte de exportación).
* **PATCH** (ej. `v1.0.1`): Corrección de errores de código (*bugfixes*), parches de estabilidad gráfica o documentación.

---

## 3. Guía Paso a Paso para Publicar una Nueva Versión

Para publicar formalmente una nueva versión ejecutable con sus instaladores `.exe`, `.deb` y `.rpm` en GitHub Releases:

### Paso 1: Confirmar y subir los cambios a la rama principal
```bash
git add .
git commit -m "feat: mejoras de estabilidad y nuevos instaladores"
git push origin main
```

### Paso 2: Crear la etiqueta semántica de versión
```bash
git tag -a v1.0.1 -m "Release v1.0.1: Corrección de estabilidad y nuevos paquetes"
```

### Paso 3: Subir la etiqueta a GitHub para disparar el CI/CD
```bash
git push origin v1.0.1
```

*(En aproximadamente 3 minutos, el flujo de GitHub Actions completará la compilación y la nueva Release estará disponible públicamente para su descarga).*
