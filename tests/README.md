# Suite de Pruebas Unitarias (Tests Directory)

Este directorio contiene exclusivamente la **suite de pruebas unitarias automatizadas** para la librería de Polinomios Ortogonales de Zernike (ISO 10110-5).

---

## ¿Qué son las Pruebas Unitarias y para qué sirven?

En programación, una **Prueba Unitaria (Unit Test)** es un código automatizado que prueba de forma aislada una función específica del software.

### Beneficios principales:
1. **Prevención de Regresiones:** Garantizan que cualquier cambio futuro en la matemática o en las funciones no rompa lo que ya funcionaba.
2. **Documentación Ejecutable:** Sirven como ejemplos prácticos y reales de cómo invocar e interactuar con cada función del proyecto.
3. **Validación Instantánea:** Verifican la corrección matemática de todo el sistema en milisegundos sin depender de ejecutar `main.py` manualmente.

---

## Estructura Interna de una Prueba (Patron AAA)

Todas las pruebas de este directorio siguen el patrón estándar **Arrange - Act - Assert** (Preparar, Actuar, Afirmar):

```python
def test_ejemplo():
    # 1. ARRANGE (Preparar): Definimos las entradas de prueba conocidas.
    x, y = 3.0, 4.0
    
    # 2. ACT (Actuar): Ejecutamos la función a probar.
    resultado = parsear_ecuacion_z("sqrt(x^2 + y^2)")(x, y)
    
    # 3. ASSERT (Afirmar): Validamos que la respuesta real sea igual a la teórica (5.0).
    assert resultado == 5.0
```

Si el `assert` evalúa una condición **verdadera** (`True`), la prueba pasa. Si evalúa a **falsa** (`False`), `pytest` falla y reporta exactamente en qué archivo y línea ocurrió el error.

---

### Detalle de Casos de Prueba Incluidos:

#### `test_matriz.py`
- **`test_normalizar_vector`**: Verifica la escala de vectores al rango $[-1, 1]$ (requisito del círculo unitario).
- **`test_parsear_ecuacion_z_valid`**: Evalúa ecuaciones cartesianas, cuadráticas, trigonométricas (`sin`, `cos`) y la ecuación de 3er orden (`-y - 1.5*y^3 + 1.5*x^2*y + x*y^2 - 0.33*x^3 + 2*x^2 + 2*y^2 + 0.5*x - 1`).
- **`test_parsear_ecuacion_z_invalid`**: Comprueba la seguridad del parser bloqueando variables no permitidas (`z`) y funciones maliciosas.
- **`test_descomponer_aberraciones`**: Revisa la traducción de coeficientes $A_1 \dots A_{21}$ a magnitudes ópticas (Pistón, Tilt, Desenfoque, Astigmatismo, Aberración Esférica).
- **`test_filtrar_pupila_y_centrado`**: Valida el centrado de píxeles al origen óptico y el recorte circular.
- **`test_exportar_zemax_y_codev`**: Valida la generación correcta de archivos de coeficientes para Zemax OpticStudio (`.zrn`) y CODE V (`.dat`).

#### `test_zernike.py`
- **`test_polinomios_zernike_count`**: Comprueba que la base para grado $k=5$ cargue los 21 polinomios exactos.
- **`test_resultado_zernike_structure`**: Garantiza el doble acceso a los datos por propiedad (`res.A`) y por diccionario (`res['A']`).
- **`test_ajuste_completo_sintetico`**: Ejecuta Gram-Schmidt y valida que la base $V$ sea ortogonal ($\langle V_i, V_j \rangle = 0$) y cumpla las fórmulas ISO 10110-5.
- **`test_ajuste_completo_polinomio_complejo`**: Evalúa el ajuste sobre la superficie de 3er orden comprobando un error cuadrático medio casi cero ($\text{RMS} < 10^{-5}$).

---

## comandos para Ejecutar las Pruebas

Para ejecutar **todas** las pruebas del directorio:
```bash
uv run pytest
```

Para ejecutar con **detalle completo** (modo detallado):
```bash
uv run pytest -v
```

Para ejecutar **un solo archivo** de prueba especifico:
```bash
uv run pytest tests/test_matriz.py
```

---

## ¿Como añadir un nuevo Test?

Para agregar una nueva prueba en el futuro:
1. Abre el archivo de prueba correspondiente (o crea uno nuevo `test_mi_modulo.py`).
2. Crea una función cuyo nombre empiece obligatoriamente por `test_` (ej. `def test_nueva_funcionalidad():`).
3. Usa la instrucción `assert` para verificar tus resultados.
4. Vuelve a ejecutar `uv run pytest`.
