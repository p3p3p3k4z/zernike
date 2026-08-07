"""
lib/interferometria.py
======================
Libreria matematica pura basada en Programacion Funcional (FP)
para el procesamiento digital de interferogramas y la extraccion de fase 2D.

Implementa:
- Demodulacion de fase mediante Transformada de Fourier 2D (Metodo de Takeda et al., 1982).
- Desenvolvimiento de fase 2D (2D Phase Unwrapping).
- Extraccion de crestas y esqueleto de franjas de interferencia.
- Generacion funcional de interferogramas sinteticos.
"""

from typing import Union, Tuple, Callable
import numpy as np
from PIL import Image


def cargar_y_normalizar_imagen(fuente: Union[str, np.ndarray]) -> np.ndarray:
    """
    Funcion pura que carga una imagen (o matriz) y la convierte a escala de grises
    normalizada en el rango flotante [0.0, 1.0].
    """
    if isinstance(fuente, str):
        img_pil = Image.open(fuente).convert('L')
        matriz = np.array(img_pil, dtype=np.float64)
    elif isinstance(fuente, np.ndarray):
        matriz = fuente.astype(np.float64)
        if matriz.ndim == 3:
            # Convertir RGB/RGBA a escala de grises mediante pesos de luminancia ITU-R BT.601
            matriz = 0.2989 * matriz[:, :, 0] + 0.5870 * matriz[:, :, 1] + 0.1140 * matriz[:, :, 2]
    else:
        raise TypeError("La fuente debe ser una ruta de archivo (str) o un numpy.ndarray.")

    v_min, v_max = matriz.min(), matriz.max()
    if v_max > v_min:
        return (matriz - v_min) / (v_max - v_min)
    return np.zeros_like(matriz)


def aplicar_mascara_circular(matriz: np.ndarray, radio_pct: float = 0.95) -> np.ndarray:
    """
    Funcion pura que aplica una mascara circular unitaria a una matriz 2D.
    Puntos fuera de la pupila se establecen en 0.0.
    """
    filas, cols = matriz.shape
    cy, cx = filas / 2.0, cols / 2.0
    r_max = (min(filas, cols) / 2.0) * radio_pct

    y, x = np.ogrid[:filas, :cols]
    dist_sq = (x - cx)**2 + (y - cy)**2
    mascara = dist_sq <= r_max**2

    return np.where(mascara, matriz, 0.0)


def recortar_y_limpiar_interferograma(matriz_img: np.ndarray, umbral_fondo: float = 0.06, margen_px: int = 4) -> Tuple[np.ndarray, dict]:
    """
    Funcion pura que detecta el Bounding Box del interferograma ignorando el fondo oscuro,
    recorta un cuadrado perfecto centrado y aplica una mascara circular de limpieza.

    Retorna:
    - matriz_recortada: Matriz 2D recortada y con fondo oscuro limpiado a 0.0.
    - metadata: Diccionario con coordenadas de recorte (min_x, max_x, min_y, max_y, centro_x, centro_y, radio).
    """
    y_coords, x_coords = np.where(matriz_img > umbral_fondo)

    filas, cols = matriz_img.shape
    if len(x_coords) == 0 or len(y_coords) == 0:
        min_x, max_x, min_y, max_y = 0, cols, 0, filas
    else:
        min_x, max_x = max(0, x_coords.min() - margen_px), min(cols, x_coords.max() + margen_px)
        min_y, max_y = max(0, y_coords.min() - margen_px), min(filas, y_coords.max() + margen_px)

    ancho = max_x - min_x
    alto = max_y - min_y
    lado = max(ancho, alto)

    cx = (min_x + max_x) // 2
    cy = (min_y + max_y) // 2

    top = max(0, cy - lado // 2)
    bottom = min(filas, top + lado)
    left = max(0, cx - lado // 2)
    right = min(cols, left + lado)

    matriz_crop = matriz_img[top:bottom, left:right]

    # Aplicar mascara circular para eliminar bordes oscuros fuera de la pupila
    c_filas, c_cols = matriz_crop.shape
    r_max = min(c_filas, c_cols) / 2.0
    y_g, x_g = np.ogrid[:c_filas, :c_cols]
    mask_circulo = ((x_g - c_cols/2.0)**2 + (y_g - c_filas/2.0)**2) <= (r_max * 0.98)**2

    matriz_limpia = np.where(mask_circulo, matriz_crop, 0.0)

    metadata = {
        'left': left, 'right': right, 'top': top, 'bottom': bottom,
        'cx': cx, 'cy': cy, 'radius': r_max
    }

    return matriz_limpia, metadata


def extraer_puntos_pupila_circular(fase_unwrapped: np.ndarray, matriz_img: np.ndarray = None, radio_pct: float = 0.96) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Funcion pura que extrae las coordenadas normalizadas (X, Y) y la fase (Z)
    estrictamente DENTRO del disco circular del interferograma.

    Filtra cualquier punto que caiga fuera del circulo unitario o que corresponda
    al fondo oscuro (intensidad <= 0.01 o NaN en fase).

    Retorna:
    - X_validos: array 1D de coordenadas X en [-1, 1] dentro de la pupila circular.
    - Y_validos: array 1D de coordenadas Y en [-1, 1] dentro de la pupila circular.
    - Z_validos: array 1D de valores de fase (Z) correspondientes.
    - mask_circular_2d: matriz booleana 2D de la pupila circular exacta.
    """
    filas, cols = fase_unwrapped.shape
    y_px = np.arange(filas)
    x_px = np.arange(cols)
    xx_px, yy_px = np.meshgrid(x_px, y_px)

    # Determinar centro y radio de la pupila circular real
    if matriz_img is not None and np.any(matriz_img > 0.02):
        y_valid, x_valid = np.where(matriz_img > 0.02)
        cx = (x_valid.min() + x_valid.max()) / 2.0
        cy = (y_valid.min() + y_valid.max()) / 2.0
        r_pupil = (min(x_valid.max() - x_valid.min(), y_valid.max() - y_valid.min()) / 2.0) * radio_pct
    else:
        cx = cols / 2.0
        cy = filas / 2.0
        r_pupil = (min(filas, cols) / 2.0) * radio_pct

    if r_pupil <= 0:
        r_pupil = min(filas, cols) / 2.0

    # Coordenadas normalizadas respecto a la pupila circular detectada
    xx_norm = (xx_px - cx) / r_pupil
    yy_norm = (yy_px - cy) / r_pupil

    # Mascara estrictamente CIRCULAR
    dist_sq = xx_norm**2 + yy_norm**2
    mask_circular = (dist_sq <= 1.0) & (~np.isnan(fase_unwrapped))

    if matriz_img is not None:
        mask_circular = mask_circular & (matriz_img > 0.01)

    X_valid = xx_norm[mask_circular]
    Y_valid = yy_norm[mask_circular]
    Z_valid = fase_unwrapped[mask_circular]

    return X_valid, Y_valid, Z_valid, mask_circular




def demodular_fase_fft2d(matriz_img: np.ndarray, radio_filtro_pct: float = 0.15) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Demodula la fase 2D de un interferograma usando el metodo de Fourier (Takeda et al., 1982).

    Retorna:
    - fase_enrollada: Matriz 2D de fase en el rango [-pi, +pi].
    - espectro_magnitud: Espectro 2D de frecuencia desplazado (logaritmico).
    - mascara_filtro: Mascara del filtro pase-banda aplicado en el espectro.
    """
    filas, cols = matriz_img.shape

    # 1. Transformada de Fourier 2D y desplazamiento del origen al centro
    fft_raw = np.fft.fft2(matriz_img)
    fft_shift = np.fft.fftshift(fft_raw)
    espectro_abs = np.abs(fft_shift)

    # 2. Localizar el pico espectral carrier (+f_x, +f_y) excluyendo el centro DC
    cy, cx = filas // 2, cols // 2
    r_dc = int(min(filas, cols) * 0.05)

    y_grid, x_grid = np.ogrid[:filas, :cols]
    mask_excluir_dc = ((x_grid - cx)**2 + (y_grid - cy)**2) <= r_dc**2

    espectro_sin_dc = np.copy(espectro_abs)
    espectro_sin_dc[mask_excluir_dc] = 0.0

    # Buscar coordenadas del pico maximo
    peak_y, peak_x = np.unravel_index(np.argmax(espectro_sin_dc), espectro_sin_dc.shape)

    # 3. Construir filtro pase-banda Gaussiano alrededor del pico detectado
    radio_filtro = min(filas, cols) * radio_filtro_pct
    dist_pico_sq = (x_grid - peak_x)**2 + (y_grid - peak_y)**2
    filtro_gaussiano = np.exp(-dist_pico_sq / (2.0 * (radio_filtro**2)))

    espectro_filtrado = fft_shift * filtro_gaussiano

    # 4. Desplazar el pico filtrado al centro DC (eliminacion de frecuencia portadora)
    shift_y = cy - peak_y
    shift_x = cx - peak_x
    espectro_centrado = np.roll(np.roll(espectro_filtrado, shift_y, axis=0), shift_x, axis=1)

    # 5. Transformada Inversa 2D de Fourier
    ifft_shift = np.fft.ifftshift(espectro_centrado)
    campo_complejo = np.fft.ifft2(ifft_shift)

    # 6. Extraer fase enrollada en [-pi, +pi]
    fase_enrollada = np.angle(campo_complejo)
    espectro_log = np.log1p(espectro_abs)

    return fase_enrollada, espectro_log, filtro_gaussiano


def desenvolver_fase_2d(fase_enrollada: np.ndarray) -> np.ndarray:
    """
    Funcion pura que realiza el desenvolvimiento continuo de fase en 2D (Phase Unwrapping)
    integrando las diferencias de fase sin saltos de 2*pi.
    """
    fase_desenvolviendo = np.copy(fase_enrollada)

    # Desenvolver fila por fila
    diff_filas = np.diff(fase_desenvolviendo, axis=1)
    saltos_filas = np.round(diff_filas / (2.0 * np.pi)) * (2.0 * np.pi)
    fase_desenvolviendo[:, 1:] -= np.cumsum(saltos_filas, axis=1)

    # Desenvolver columna por columna
    diff_cols = np.diff(fase_desenvolviendo, axis=0)
    saltos_cols = np.round(diff_cols / (2.0 * np.pi)) * (2.0 * np.pi)
    fase_desenvolviendo[1:, :] -= np.cumsum(saltos_cols, axis=0)

    return fase_desenvolviendo


def extraer_esqueleto_franjas(matriz_img: np.ndarray, umbral_pct: float = 0.5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Extrae los puntos discretos de las crestas de intensidad (esqueleto de franjas).

    Retorna:
    - X_pts: Coordenadas X en el rango [-1, 1]
    - Y_pts: Coordenadas Y en el rango [-1, 1]
    - Z_pts: Valores de elevación asignados por franja
    """
    filas, cols = matriz_img.shape
    y_coords = np.linspace(-1.0, 1.0, filas)
    x_coords = np.linspace(-1.0, 1.0, cols)
    xx, yy = np.meshgrid(x_coords, y_coords)

    # Binarizar por umbral adaptativo
    umbral = matriz_img.min() + (matriz_img.max() - matriz_img.min()) * umbral_pct
    binaria = matriz_img > umbral

    # Mascara circular de la pupila
    mask_pupila = (xx**2 + yy**2) <= 1.0
    binaria_pupila = binaria & mask_pupila

    # Extraer crestas locales por derivacion discreta
    derivada = np.abs(np.gradient(binaria_pupila.astype(float), axis=1))
    puntos_crestas = derivada > 0.4

    X_pts = xx[puntos_crestas]
    Y_pts = yy[puntos_crestas]
    Z_pts = matriz_img[puntos_crestas]

    return X_pts, Y_pts, Z_pts


def generar_interferograma_sintetico(func_z: Callable[[np.ndarray, np.ndarray], np.ndarray] = None,
                                      N: int = 256, franjas_carrier: int = 12) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Genera una imagen sintetica de un interferograma optico con frecuencia portadora
    y fase dada por func_z(x, y).

    Retorna:
    - interferograma: Matriz 2D de intensidad [0, 1]
    - X_grid: Malla X [-1, 1]
    - Y_grid: Malla Y [-1, 1]
    - Z_fase_teorica: Fase teorica evaluada
    """
    x = np.linspace(-1.0, 1.0, N)
    y = np.linspace(-1.0, 1.0, N)
    X_grid, Y_grid = np.meshgrid(x, y)

    if func_z is not None:
        Z_fase_teorica = func_z(X_grid, Y_grid)
    else:
        # Aberracion por defecto: Defocus + Astigmatismo (3*x*y + 2*x)
        Z_fase_teorica = 3.0 * X_grid * Y_grid + 2.0 * X_grid

    # Generar patron de interferencia con frecuencia portadora espacial (Tilt X)
    fase_total = Z_fase_teorica + (2.0 * np.pi * franjas_carrier * X_grid)
    interferograma = 0.5 + 0.5 * np.cos(fase_total)

    # Aplicar pupila circular
    interferograma = aplicar_mascara_circular(interferograma, radio_pct=0.95)

    return interferograma, X_grid, Y_grid, Z_fase_teorica


def sintetizar_interferograma_desde_zernike(A_coefs: np.ndarray, N: int = 256, franjas_carrier: int = 12, escala_opd: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Sintetiza un interferograma óptico realista 2D a partir del vector de coeficientes
    de Zernike A (ISO 10110-5) ajustados.

    Modelado óptico físico:
    I(x,y) = a(x,y) + b(x,y) * cos( 2*pi * escala_opd * W_fit(x,y) + 2*pi * (fx*X + fy*Y) )

    Retorna:
    - interferograma: Matriz 2D de intensidad [0, 1]
    - X_grid: Malla X [-1, 1]
    - Y_grid: Malla Y [-1, 1]
    - W_fit_2d: Mapa bidimensional del frente de onda ajustado
    """
    from lib.zernike import polinomios_zernike, evaluar_polinomios, reconstruir_W

    x = np.linspace(-1.0, 1.0, N)
    y = np.linspace(-1.0, 1.0, N)
    X_grid, Y_grid = np.meshgrid(x, y)
    X_flat, Y_flat = X_grid.flatten(), Y_grid.flatten()

    polinomios = polinomios_zernike()
    U = evaluar_polinomios(X_flat, Y_flat, polinomios)

    L = U.shape[0]
    A_full = np.zeros(L)
    n_copy = min(len(A_coefs), L)
    A_full[:n_copy] = A_coefs[:n_copy]

    W_flat = reconstruir_W(A_full, U)
    W_fit_2d = W_flat.reshape((N, N))

    # Fase de deformación óptica real: phi = 2*pi * escala_opd * W_fit
    fase_optica = 2.0 * np.pi * escala_opd * W_fit_2d

    # Frecuencia portadora realista (inclinación principal en X e inclinación secundaria en Y)
    fx = franjas_carrier
    fy = franjas_carrier * 0.25
    fase_carrier = 2.0 * np.pi * (fx * X_grid + fy * Y_grid)

    fase_total = fase_optica + fase_carrier

    # Iluminación de fondo gaussiana a(x,y) y contraste b(x,y) de laboratorio óptico
    R2 = X_grid**2 + Y_grid**2
    a_fondo = 0.48 + 0.07 * np.exp(-1.5 * R2)
    b_contraste = 0.42

    interferograma = a_fondo + b_contraste * np.cos(fase_total)
    interferograma = np.clip(interferograma, 0.0, 1.0)

    # Máscara de pupila circular limpia con supresión de fondo exterior
    interferograma = aplicar_mascara_circular(interferograma, radio_pct=0.96)

    return interferograma, X_grid, Y_grid, W_fit_2d


