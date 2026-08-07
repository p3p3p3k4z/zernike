# Reglas y Estándares del Workspace: Proyecto Zernike

Este archivo define las reglas globales y estándares de ingeniería para la interacción con los agentes de IA en el proyecto Zernike.

---

## 1. Normas Metrológicas y Físicas
- **ISO 10110-5 / ANSI Z80.28**: La ordenación e índice de los Polinomios de Zernike debe respetar estrictamente la convención internacional ISO 10110-5.
- **Demodulación Takeda 2D**: Toda operación de extracción de fase 2D debe fundamentarse en la Transformada de Fourier 2D (Takeda et al., 1982) y en la eliminación de discontinuidades de $2\pi$ (*phase unwrapping*).
- **Pupila Circular Unitaria**: Los cálculos de ajuste de Zernike se evalúan únicamente en el disco de pupila normalizado ($\rho = \sqrt{x^2+y^2} \le 1.0$).

---

## 2. Principios de Arquitectura y Código
- **Separación de Responsabilidades (SOLID)**: Mantener desacoplados los módulos de cómputo puramente matemáticos (`lib/`), los componentes visuales (`gui/components/`), los trabajadores asíncronos (`gui/worker.py`) y las ventanas de control (`gui/main_window.py`).
- **Compatibilidad Dual Python/Fortran**: Preservar la sincronía entre el motor numérico en Python (NumPy) y el motor nativo acelerado en Fortran (`fotrain_implemnt/`).
- **Gestión de Memoria y Rendimiento**: Evitar cálculos innecesarios en la interfaz gráfica PySide6 y utilizar llamadas asíncronas de dibujo con `draw_idle()`.

---

## 3. Estándar Estricto de Documentación y Comentarios
- **Comentarios Limpios y Pedagógicos**: Todo comentario o docstring agregado al código debe ser redactado con claridad pedagógica e intención explicativa.
- **Sin Emojis ni Símbolos Informales**: Queda estrictamente prohibido el uso de emojis o caracteres informales en docstrings, comentarios de código y mensajes de log. La documentación debe ser limpia, elegante y profesional.
