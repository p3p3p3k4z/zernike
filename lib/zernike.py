"""
lib/zernike.py
==============
Motor matemático del algoritmo de ajuste de superficies ópticas con
polinomios ortogonales de Zernike (ISO 10110-5, grado k=5, L=21).

Flujo:
  Datos (X,Y,W) -> U -> (V, D, F) -> B -> C -> A -> W_fit

Referencia: Malacara, D. (1990). Optical Shop Testing.
"""

import numpy as np


def polinomios_zernike():
    """
    Retorna una lista de 21 funciones lambda que representan los
    polinomios de Zernike en forma monomial hasta grado 5
    """
    return [
        lambda x, y: np.ones_like(x),                                                # r=1  piston
        lambda x, y: x,                                                               # r=2  tilt x
        lambda x, y: y,                                                               # r=3  tilt y
        lambda x, y: 2*x*y,                                                           # r=4  astig 45
        lambda x, y: -1 + 2*y**2 + 2*x**2,                                            # r=5  defocus
        lambda x, y: y**2 - x**2,                                                     # r=6  astig 0
        lambda x, y: 3*x*y**2 - x**3,                                                 # r=7  coma x
        lambda x, y: -2*x + 3*x*y**2 + 3*x**3,                                        # r=8  coma y
        lambda x, y: -2*y + 3*y**3 + 3*x**2*y,                                        # r=9
        lambda x, y: y**3 - 3*x**2*y,                                                 # r=10
        lambda x, y: 4*y**3*x - 4*x**3*y,                                             # r=11
        lambda x, y: -6*x*y + 8*y**3*x + 8*x**3*y,                                    # r=12
        lambda x, y: 1 - 6*y**2 - 6*x**2 + 6*y**4 + 12*x**2*y**2 + 6*x**4,            # r=13
        lambda x, y: -3*y**2 + 3*x**2 + 4*y**4 - 4*x**4,                              # r=14
        lambda x, y: y**4 - 6*x**2*y**2 + x**4,                                       # r=15
        lambda x, y: 5*x*y**4 - 10*x**3*y**2 + x**5,                                  # r=16
        lambda x, y: -12*x*y**2 + 4*x**3 + 15*x*y**4 + 10*x**3*y**2 - 5*x**5,         # r=17
        lambda x, y: 3*x - 12*x*y**2 - 12*x**3 + 10*x*y**4 + 20*x**3*y**2 + 10*x**5, # r=18
        lambda x, y: 3*y - 12*y**3 - 12*x**2*y + 10*y**5 + 20*x**2*y**3 + 10*x**4*y, # r=19
        lambda x, y: -4*y**3 + 12*x**2*y + 5*y**5 - 10*x**2*y**3 - 15*x**4*y,         # r=20
        lambda x, y: y**5 - 10*x**2*y**3 + 5*x**4*y,                                   # r=21
    ]


def evaluar_polinomios(X, Y, polinomios):
    """
    Evalua la lista de polinomios de Zernike en los puntos (X, Y)
    y construye la matriz de diseno U de forma (L, N).

    Retorna U : ndarray (L, N)
    """
    L = len(polinomios)
    N = len(X)
    U = np.zeros((L, N))
    for r, func in enumerate(polinomios):
        U[r, :] = func(X, Y)
    return U


def construir_base_ortogonal(U):
    """
    Ortogonaliza la base de Zernike U mediante Gram-Schmidt discreto.

    Parametros
    ----------
    U : ndarray (L, N)

    Retorna
    -------
    V : list[ndarray]  -- L vectores ortogonales de tamano N
    D : ndarray (L, L) -- coeficientes D_{r,p} (triangular inferior)
    F : list[float]    -- normas al cuadrado de cada V_r
    """
    L, N = U.shape
    V = []
    F = []
    D = np.zeros((L, L))

    V0 = U[0, :].copy()
    V.append(V0)
    F.append(np.sum(V0**2))

    for r in range(1, L):
        Vr = U[r, :].copy()
        for p in range(r):
            Drp = -np.dot(U[r, :], V[p]) / F[p]
            D[r, p] = Drp
            Vr += Drp * V[p]
        V.append(Vr)
        F.append(np.sum(Vr**2))

    return V, D, F


def calcular_B(W_exp, V, F):
    """
    Proyecta la superficie experimental W_exp sobre la base
    ortogonal V para obtener los pesos B.

    Retorna B : ndarray (L,)
    """
    L = len(V)
    B = np.zeros(L)
    for p in range(L):
        B[p] = np.dot(W_exp, V[p]) / F[p]
    return B


def calcular_C(D, L):
    """
    Construye la matriz de traduccion C que convierte los pesos B
    (base ortogonal V) a los coeficientes A (base estandar U).

    Retorna C : ndarray (L, L)  triangular inferior con C[r,r]=1
    """
    C = np.eye(L)
    for r in range(1, L):
        for i in range(r):
            suma = 0.0
            for s in range(1, r - i + 1):
                suma += D[r, r - s] * C[r - s, i]
            C[r, i] = suma
    return C


def calcular_A(B, C, L):
    """
    Obtiene los coeficientes finales de Zernike A referidos a
    la base estandar U (norma ISO 10110-5).

    Retorna A : ndarray (L,)
    """
    A = np.zeros(L)
    A[L - 1] = B[L - 1]
    for r in range(L - 2, -1, -1):
        suma = 0.0
        for i in range(r + 1, L):
            suma += B[i] * C[i, r]
        A[r] = B[r] + suma
    return A


def reconstruir_W(A, U):
    """
    Reconstruye la superficie ajustada W_fit como combinacion
    lineal de los polinomios de Zernike pesados por A.

    Retorna W_fit : ndarray (N,)
    """
    return np.dot(A, U)


def ajuste_completo(X, Y, W, polinomios, k=5):
    """
    Ejecuta los 7 pasos del algoritmo de ajuste de Zernike.

    Parametros
    ----------
    X, Y       : ndarray (N,)   -- coordenadas ya normalizadas
    W          : ndarray (N,)   -- superficie medida
    polinomios : list[callable] -- lista de L lambdas de Zernike
    k          : int            -- grado maximo (fijo = 5 -> L = 21)

    Retorna dict con: U, V, D, F, B, C, A, W_fit, X, Y
    """
    L = (k + 1) * (k + 2) // 2  # 21 para k=5

    U = evaluar_polinomios(X, Y, polinomios)
    V, D, F = construir_base_ortogonal(U)
    B = calcular_B(W, V, F)
    C = calcular_C(D, L)
    A = calcular_A(B, C, L)
    W_fit = reconstruir_W(A, U)

    return {'U': U, 'V': V, 'D': D, 'F': F,
            'B': B, 'C': C, 'A': A,
            'W_fit': W_fit, 'X': X, 'Y': Y, 'W': W}


def verificar_ortogonalidad(V, tolerancia=1e-10):
    """
    Comprueba que todos los pares (V_i, V_j) con i != j sean
    mutuamente ortogonales. Retorna True si OK.
    """
    L = len(V)
    print("\n--- Verificacion de ortogonalidad de V ---")
    ok = True
    for i in range(L):
        for j in range(i + 1, L):
            prod = np.dot(V[i], V[j])
            if abs(prod) > tolerancia:
                print(f"  FALLA <V{i+1}, V{j+1}> = {prod:.2e}")
                ok = False
    if ok:
        print("  OK: todos los V son ortogonales.")
    return ok


def verificar_formulas(resultados):
    """
    Verifica la consistencia cruzada de todas las matrices y
    vectores con las ecuaciones de los articulos (Malacara 1990) y
    las notas del algoritmo.
    """
    D = resultados['D']
    C = resultados['C']
    B = resultados['B']
    A = resultados['A']
    U = resultados['U']
    V = resultados['V']
    F = resultados['F']
    W_exp = resultados.get('W')
    W_fit = resultados['W_fit']
    L = len(A)

    print("\n--- Verificacion de formulas ---")
    todas_ok = True

    # 1. F_r = sum(V_r^2)
    F_calc = [np.sum(v**2) for v in V]
    if np.allclose(F, F_calc, atol=1e-12):
        print("  OK: F_p = sum(V_p^2)")
    else:
        print("  FALLA: discrepancia en F_p.")
        todas_ok = False

    # 2. D_rp = -<U_r, V_p> / F_p
    D_calc = np.zeros((L, L))
    for r in range(1, L):
        for p in range(r):
            D_calc[r, p] = -np.dot(U[r], V[p]) / F[p]
    if np.allclose(D, D_calc, atol=1e-12):
        print("  OK: D_rp = -<U_r, V_p> / F_p")
    else:
        print("  FALLA: discrepancia en D_rp.")
        todas_ok = False

    # 3. V_r = U_r + sum_{p<r} D_rp V_p
    V_calc = []
    for r in range(L):
        vr_calc = U[r].copy()
        for p in range(r):
            vr_calc += D[r, p] * V[p]
        V_calc.append(vr_calc)
    if np.allclose(V, V_calc, atol=1e-12):
        print("  OK: V_r = U_r + sum D_rp V_p")
    else:
        print("  FALLA: discrepancia en la construccion de V_r.")
        todas_ok = False

    # 4. B_p = <W_exp, V_p> / F_p
    if W_exp is not None:
        B_calc = [np.dot(W_exp, V[p]) / F[p] for p in range(L)]
        if np.allclose(B, B_calc, atol=1e-12):
            print("  OK: B_p = <W_exp, V_p> / F_p")
        else:
            print("  FALLA: discrepancia en B_p.")
            todas_ok = False

    # 5. C desde D (Ec. 23)
    C_calc = np.eye(L)
    for r in range(1, L):
        for i in range(r):
            C_calc[r, i] = sum(D[r, r-s] * C_calc[r-s, i] for s in range(1, r - i + 1))
    if np.allclose(C, C_calc, atol=1e-12):
        print("  OK: C_ri = sum D_r,r-s C_r-s,i (Ec. 23)")
    else:
        print("  FALLA: discrepancia en C.")
        todas_ok = False

    # 6. V_r = U_r + sum_{i<r} C_ri U_i
    V_via_C = []
    for r in range(L):
        vr_c = U[r].copy()
        for i in range(r):
            vr_c += C[r, i] * U[i]
        V_via_C.append(vr_c)
    if np.allclose(V, V_via_C, atol=1e-12):
        print("  OK: V_r = U_r + sum C_ri U_i")
    else:
        print("  FALLA: discrepancia en V_r via C.")
        todas_ok = False

    # 7. A desde B y C (Ec. 26)
    A_calc = np.zeros(L)
    A_calc[L-1] = B[L-1]
    for r in range(L-2, -1, -1):
        A_calc[r] = B[r] + sum(B[i] * C[i, r] for i in range(r+1, L))
    if np.allclose(A, A_calc, atol=1e-12):
        print("  OK: A_r = B_r + sum B_i C_ir (Ec. 26)")
    else:
        print("  FALLA: discrepancia en A.")
        todas_ok = False

    # 8. W_fit = sum B_r V_r
    W_via_V = sum(B[r] * V[r] for r in range(L))
    if np.allclose(W_via_V, W_fit, atol=1e-12):
        print("  OK: W_fit = sum(B_r V_r)")
    else:
        print("  FALLA: discrepancia en W_fit via V.")
        todas_ok = False

    # 9. W_fit = sum A_r U_r
    W_via_U = sum(A[r] * U[r] for r in range(L))
    if np.allclose(W_via_U, W_fit, atol=1e-12):
        print("  OK: W_fit = sum(A_r U_r)")
    else:
        print("  FALLA: discrepancia en W_fit via U.")
        todas_ok = False

    if todas_ok:
        print("  ==> TODAS LAS FORMULAS SE CUMPLEN CORRECTAMENTE <==")
    else:
        print("  ==> ALGUNAS FORMULAS FALLARON <==")

