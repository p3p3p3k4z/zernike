"""
tests/test_interferometria.py
==============================
Pruebas unitarias automatizadas para la librería puramente funcional de interferometria (lib/interferometria.py).
"""

import numpy as np
import pytest

from lib.interferometria import (
    cargar_y_normalizar_imagen, aplicar_mascara_circular,
    demodular_fase_fft2d, desenvolver_fase_2d,
    extraer_esqueleto_franjas, generar_interferograma_sintetico
)


def test_cargar_y_normalizar_imagen_array():
    arr = np.array([[10, 20], [30, 45]], dtype=np.float64)
    norm = cargar_y_normalizar_imagen(arr)
    assert norm.shape == (2, 2)
    assert norm.min() == 0.0
    assert norm.max() == 1.0


def test_aplicar_mascara_circular():
    matriz = np.ones((50, 50), dtype=np.float64)
    mascarada = aplicar_mascara_circular(matriz, radio_pct=0.8)
    assert mascarada.shape == (50, 50)
    assert mascarada[25, 25] == 1.0  # Centro dentro de la pupila
    assert mascarada[0, 0] == 0.0    # Esquina fuera de la pupila


def test_generar_interferograma_sintetico():
    img, X, Y, Z = generar_interferograma_sintetico(N=64, franjas_carrier=8)
    assert img.shape == (64, 64)
    assert X.shape == (64, 64)
    assert Y.shape == (64, 64)
    assert Z.shape == (64, 64)
    assert img.min() >= 0.0
    assert img.max() <= 1.0


def test_demodular_fase_fft2d_takeda():
    img, _, _, Z_teorico = generar_interferograma_sintetico(N=128, franjas_carrier=10)
    fase_enrollada, espectro_log, filtro = demodular_fase_fft2d(img, radio_filtro_pct=0.20)

    assert fase_enrollada.shape == (128, 128)
    assert espectro_log.shape == (128, 128)
    assert filtro.shape == (128, 128)
    assert fase_enrollada.min() >= -np.pi - 1e-5
    assert fase_enrollada.max() <= np.pi + 1e-5


def test_desenvolver_fase_2d():
    fase_wrap = np.array([[-3.0, -2.0], [2.0, 3.0]])
    fase_unwrapped = desenvolver_fase_2d(fase_wrap)
    assert fase_unwrapped.shape == (2, 2)


def test_extraer_esqueleto_franjas():
    img, _, _, _ = generar_interferograma_sintetico(N=64, franjas_carrier=6)
    X_pts, Y_pts, Z_pts = extraer_esqueleto_franjas(img, umbral_pct=0.5)

    assert len(X_pts) == len(Y_pts) == len(Z_pts)
    assert len(X_pts) > 0
