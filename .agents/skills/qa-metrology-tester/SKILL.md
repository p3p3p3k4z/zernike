---
name: qa-metrology-tester
description: Agente QA & Metrología de Pruebas para automatizar la verificación de ortogonalidad, pruebas de regresión en pytest y validación numérica cruzada entre Python y Fortran.
---

# Skill: Agente QA & Metrología de Pruebas (QA Metrology Tester)

Este skill se encarga de asegurar la precisión numérica, la cobertura de pruebas unitarias y la estabilidad de la aplicación frente a regresiones.

## Responsabilidades de Control de Calidad

1. **Verificación de Ortogonalidad Matemática**:
   - Pruebas automatizadas de ortogonalidad de la matriz de Zernike en `tests/test_zernike.py`.
   - Evaluación del error cuadrático medio (RMSE) y desviación estándar del frente de onda reconstruido $W_{\text{fit}}$.

2. **Validación Cruzada Python vs. Fortran**:
   - Comprobación en `tests/test_fortran.py` de la coincidencia numérica exacta entre la descomposición SVD/QR en NumPy y Gram-Schmidt en Fortran.

3. **Pruebas de Interfaz y Utilidades**:
   - Pruebas de renderizado y eventos de la GUI PySide6 en `tests/test_gui.py`.
   - Pruebas para el motor de interferometría 2D (Takeda FFT, Unwrapping, Esqueleto) en `tests/test_interferometria.py`.

4. **Protocolo de Validación**:
   - Ejecución completa de la suite de pruebas unitarias mediante:
     ```bash
     uv run pytest -v
     ```
   - Garantizar un resultado del 100% de pruebas aprobadas en cada cambio de código.
