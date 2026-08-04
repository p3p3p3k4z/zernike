"""
===============================================================================
MÓDULO DE PRUEBAS UNITARIAS: lib.matriz
===============================================================================
Este archivo contiene pruebas automatizadas para verificar el correcto funcionamiento 
de las funciones matemáticas y auxiliares definidas en `lib/matriz.py`.

¿Qué es una prueba unitaria?
-----------------------------
Una prueba unitaria es una funcion de código que aísla un componente pequeño de 
nuestro software (funcion) y comprueba autoaáticamente que, dada una entrada conocida 
(inputs), la funcion devuelva la salida exacta esperada (output).

Estructura típica de un test:
1. Preparación (Arrange): Definimos datos de prueba conocidos.
2. Ejecución (Act): Invocamos la funcion que queremos evaluar.
3. Afirmación (Assert): Usamos la palabra reservada `assert` para validar que la 
   respuesta real sea exactamente igual a la respuesta teorica.
===============================================================================
"""

import pytest
import numpy as np
from lib.matriz import (
    normalizar_vector,
    parsear_ecuacion_z,
    descomponer_aberraciones,
    filtrar_pupila,
    centrar_coordenadas,
)


def test_normalizar_vector():
    """
    OBJETIVO: Probar la funcion
 `normalizar_vector(datos)`.
    
    ¿QUÉ DEBE HACER? 
    Tomar un vector numerico y dividirlo entre su máximo valor absoluto,
    de tal forma que todos los elementos queden en el rango [-1, 1].

    ¿POR QUÉ ES IMPORTANTE?
    Los polinomios de Zernike (ISO 10110-5) están definidos únicamente dentro del 
    círculo unitario de radio 1. Si los datos no están normalizados a [-1, 1], 
    el algoritmo falla.
    """
    # 1. Caso Normal: Vector con valores positivos, negativos y ceros
    v_entrada = np.array([2.0, -4.0, 1.0, 0.0]) # El valor absoluto máximo es |-4.0| = 4.0
    v_obtenido = normalizar_vector(v_entrada)
    
    # Comprobamos que el máximo absoluto del resultado sea exactamente 1.0
    assert np.max(np.abs(v_obtenido)) == 1.0
    
    # Comprobamos que cada elemento haya sido dividido por 4.0: [2/4, -4/4, 1/4, 0/4]
    v_esperado = np.array([0.5, -1.0, 0.25, 0.0])
    assert np.allclose(v_obtenido, v_esperado)

    # 2. Caso Límite: Vector de ceros (no debe causar división por cero)
    v_ceros = np.zeros(5)
    assert np.array_equal(normalizar_vector(v_ceros), v_ceros)


def test_parsear_ecuacion_z_valid():
    """
    OBJETIVO: Probar `parsear_ecuacion_z(expr_str)` con entradas matemáticas VÁLIDAS.
    
    ¿QUÉ DEBE HACER?
    Convertir una cadena de texto (ej. "3*x*y + 2*x") en una funcion
 ejecutable 
    de Python utilizando el evaluador seguro AST.

    ¿CÓMO LO PROBAMOS?
    Pasamos distintas ecuaciones escritas en texto, las convertimos a funciones 
    y evaluamos en puntos (x, y) específicos comparando contra el resultado exacto.
    """
    # 1. Ecuación polinómica simple: "3*x*y + 2*x"
    func1 = parsear_ecuacion_z("3*x*y + 2*x")
    # Para (x=1.0, y=2.0) -> 3*(1)*(2) + 2*(1) = 6 + 2 = 8
    assert func1(1.0, 2.0) == 8.0

    # 2. Ecuación trigonométrica: "sin(x) + cos(y)"
    func2 = parsear_ecuacion_z("sin(x) + cos(y)")
    # Para (x=0.0, y=0.0) -> sin(0) + cos(0) = 0 + 1 = 1
    assert np.isclose(func2(0.0, 0.0), 1.0)

    # 3. Raíz cuadrada y potencias: "sqrt(x^2 + y^2)"
    func3 = parsear_ecuacion_z("sqrt(x^2 + y^2)")
    # Para (x=3.0, y=4.0) -> sqrt(9 + 16) = sqrt(25) = 5
    assert np.isclose(func3(3.0, 4.0), 5.0)

    # 4. Resta de cuadrados: "y**2 - x**2"
    func4 = parsear_ecuacion_z("y**2 - x**2")
    # Para (x=2.0, y=3.0) -> 3^2 - 2^2 = 9 - 4 = 5
    assert np.isclose(func4(2.0, 3.0), 5.0)

    # 5. Producto bilineal: "2*x*y"
    func5 = parsear_ecuacion_z("2*x*y")
    # Para (x=3.0, y=4.0) -> 2 * 3 * 4 = 24
    assert np.isclose(func5(3.0, 4.0), 24.0)

    # 6. Polinomio de 3er orden complejo pedido por el usuario
    expr6 = "-y - 1.5*y*y*y + 1.5*x*x*y + x*y*y - 0.33*x*x*x + 2*x*x + 2*y*y + 0.5*x - 1"
    func6 = parsear_ecuacion_z(expr6)
    x_test, y_test = 0.5, -0.5
    resultado_teorico = -y_test - 1.5*y_test**3 + 1.5*x_test**2*y_test + x_test*y_test**2 - 0.33*x_test**3 + 2*x_test**2 + 2*y_test**2 + 0.5*x_test - 1
    assert np.isclose(func6(x_test, y_test), resultado_teorico)


def test_parsear_ecuacion_z_invalid():
    """
    OBJETIVO: Probar el sistema de SEGURIDAD de `parsear_ecuacion_z(expr_str)`.
    
    ¿QUÉ DEBE HACER?
    Rechazar activamente expresiones mal formadas, variables desconocidas o 
    intentos de inyección de código peligroso, lanzando excepciones `ValueError`.
    """
    # Ecuación vacía o con espacios -> Debe retornar None
    assert parsear_ecuacion_z("   ") is None

    # Error de sintaxis (operador doble sin sentido " + * ")
    with pytest.raises(ValueError):
        parsear_ecuacion_z("3 * x + * y")

    # Intento de usar variable no autorizada 'z' (solo se permiten 'x' e 'y')
    with pytest.raises(ValueError):
        func = parsear_ecuacion_z("x + y + z")
        func(1, 1)

    # Intento de ataque/inyección de funcion
    # no autorizada ('eval' u 'os.system')
    with pytest.raises(ValueError):
        func = parsear_ecuacion_z("eval('1+1')")
        func(1, 1)


def test_descomponer_aberraciones():
    """
    OBJETIVO: Probar la funcion
 `descomponer_aberraciones(A)`.
    
    ¿QUÉ DEBE HACER?
    Tomar el vector de coeficientes de Zernike A = [A1, A2, ..., A21] y 
    mapear los índices específicos a los nombres de las aberraciones ópticas.
    
    Índices clave:
    - A[0]: Piston
    - A[1], A[2]: Tilt X, Tilt Y
    - A[4]: Desenfoque (Defocus)
    - A[5]: Astigmatismo 0°
    - A[12]: Aberración Esférica de 3er orden
    """
    # Creamos un vector de 21 coeficientes en cero
    A = np.zeros(21)
    A[0] = 0.5   # Piston = 0.5
    A[1] = 1.0   # Tilt X = 1.0
    A[2] = -1.0  # Tilt Y = -1.0  -> Tilt Total = sqrt(1^2 + (-1)^2) = sqrt(2) ≈ 1.414
    A[4] = 0.75  # Defocus = 0.75
    A[5] = 0.3   # Astigmatismo 0° = 0.3
    A[12] = 0.1  # Esférica = 0.1

    # Invocamos la descomposicion
    aberraciones = descomponer_aberraciones(A)

    # Validamos que los campos del diccionario contengan los valores exactos asignados
    assert aberraciones['Piston'] == 0.5
    assert aberraciones['Tilt_X'] == 1.0
    assert aberraciones['Tilt_Y'] == -1.0
    assert np.isclose(aberraciones['Tilt_Total'], np.sqrt(2.0))
    assert aberraciones['Defocus'] == 0.75
    assert aberraciones['Astigmatismo_0'] == 0.3
    assert aberraciones['Esferica_3er_orden'] == 0.1


def test_filtrar_pupila_y_centrado():
    """
    OBJETIVO: Probar el centrado de coordenadas y el filtro de pupila circular.
    
    ¿QUÉ DEBE HACER?
    1. `centrar_coordenadas`: Mover el origen (0,0) del sensor CCD a su centro geométrico.
    2. `filtrar_pupila`: Conservar solo los puntos dentro del radio de la pupila 
       y normalizar sus coordenadas a [-1, 1].
    """
    # 1. Crear una malla sintética de 10x10 píxeles
    N, M = 10, 10
    X_pix, Y_pix = np.meshgrid(np.arange(M), np.arange(N))
    X_flat, Y_flat = X_pix.flatten(), Y_pix.flatten()
    Z_flat = X_flat + Y_flat

    # 2. Centrar coordenadas al origen óptico
    X_c, Y_c = centrar_coordenadas(X_flat, Y_flat, N, M)
    
    # El promedio de coordenadas centradas en un sensor simétrico debe ser exactamente 0.0
    assert np.isclose(np.mean(X_c), 0.0)
    assert np.isclose(np.mean(Y_c), 0.0)

    # 3. Filtrar con una pupila de diámetro = 6.0 px (Radio = 3.0 px)
    datos_pupila = filtrar_pupila(X_c, Y_c, Z_flat, diametro=6.0)
    
    assert datos_pupila['R'] == 3.0
    # Todos los puntos dentro de la pupila normalizados deben ser <= 1.0 en módulo
    assert np.all(np.abs(datos_pupila['X_norm']) <= 1.0)
    assert np.all(np.abs(datos_pupila['Y_norm']) <= 1.0)
