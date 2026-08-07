---
name: code-documenter
description: Agente Documentador de Código y Contexto para generar explicaciones pedagógicas, mapas de arquitectura y docstrings profesionales, limpios y estrictamente libres de emojis o caracteres especiales.
---

# Skill: Agente Documentador de Código y Contexto (Code Documenter)

Este skill se enfoca en la generación de documentación técnica de alta calidad, clara, pedagógica y estructurada para facilitar la navegación y comprensión del proyecto.

## Reglas de Documentación Estricta

1. **Estilo Pedagógico e Informativo**:
   - Explicar las razones matemáticas e ingenieriles detrás del código de manera clara para investigadores, estudiantes y desarrolladores.
   - Detallar los argumentos, tipos de datos y estructuras de retorno en estilo NumPy / Google Docstrings.

2. **Prohibición de Emojis y Caracteres Especiales Informales**:
   - Queda totalmente prohibido usar emojis o caracteres informales en docstrings, comentarios de línea, archivos de texto o guías internas.
   - El formato debe ser estrictamente limpio, profesional y académico.

3. **Mantenimiento del Contexto del Proyecto**:
   - Actualización de los diagramas de arquitectura en `README.md` y `docs/teoria_interferometria.md`.
   - Documentación clara de los flujos de ejecución en CLI (`main.py`) y GUI (`gui_app.py`).

## Ejemplo de Docstring Estándar
```python
def calcular_coeficientes_zernike(X: np.ndarray, Y: np.ndarray, W: np.ndarray) -> np.ndarray:
    """
    Calcula los coeficientes de deformacion de frente de onda A utilizando
    la base ortogonal de polinomios de Zernike (ISO 10110-5).

    Parametros:
        X (np.ndarray): Coordenadas X normalizadas [-1.0, 1.0] en la pupila.
        Y (np.ndarray): Coordenadas Y normalizadas [-1.0, 1.0] en la pupila.
        W (np.ndarray): Deformacion de la superficie o frente de onda OPD.

    Retorna:
        np.ndarray: Vector de coeficientes de aberracion A de longitud 21.
    """
```
