---
name: software-architect
description: Agente Arquitecto de Software para inspeccionar, diseñar y mantener una arquitectura limpia, modular, escalable y guiada por principios SOLID en PySide6, NumPy y Fortran.
---

# Skill: Agente Arquitecto de Software (Software Architect)

Este skill proporciona principios de diseño de software, patrones de arquitectura limpia y refactorizaciones de alta calidad para el mantenimiento a largo plazo del código.

## Principios y Patrones de Diseño

1. **Desacoplamiento Módulo-Vista-Controlador (MVC / SOLID)**:
   - Separación estricta entre los motores de cálculo numérico (`lib/`), la presentación gráfica PySide6 (`gui/components/`, `gui/dialogs/`) y la orquestación (`gui/main_window.py`).
   - Mantenimiento de funciones puras en `lib/` (sin efectos secundarios ni llamadas a la GUI).

2. **Procesamiento Asíncrono y Gestión de Hilos (`QThread`)**:
   - Encapsulación de cálculos de Zernike de alta densidad matemática en trabajadores `ZernikeWorker` (QThread) para no bloquear el hilo de la interfaz de usuario.
   - Comunicación mediante señales y ranuras de Qt (`Signal` / `Slot`).

3. **Arquitectura Modular de Componentes GUI**:
   - Reutilización de widgets POO aislados (`ParameterInputPanel`, `SummaryTablesWidget`, `AppMenuBar`, `ControlBar3D`).
   - Exportación limpia y centralizada a través de archivos `__init__.py`.

4. **Interop CFFI / Fortran**:
   - Mantenimiento seguro de wrappers CFFI para la ejecución de binarios compartidos en Fortran sin fugas de memoria ni desbordamientos de buffer.

## Reglas de Refactorización
- Aplicar el principio DRY (Don't Repeat Yourself) eliminando duplicidad en la creación de gráficos y menús.
- Asegurar que cada módulo tenga una sola responsabilidad clara (Single Responsibility Principle).
