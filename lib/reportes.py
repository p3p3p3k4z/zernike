"""
Módulo de Generación de Reportes Metrológicos de Calidad Óptica en HTML5.
Basado en la Norma ISO 10110-5 / ANSI Z80.28.
Reutiliza las funciones de graficación idénticas a la GUI principal.
"""

import os
import io
import base64
import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para renderizado headless
import matplotlib.pyplot as plt

from lib.zernike import ResultadoZernike, INFORMACION_ZERNIKE_ISO, polinomios_zernike, evaluar_polinomios
from lib.visualizacion import (
    graficar_pupila,
    mapa_fase_3d,
    graficar_interferograma_sintetico,
    graficar_espectro_aberraciones,
    COLORES_GOLOSINA_21,
)


def _fig_to_base64(fig) -> str:
    """Convierte una figura de matplotlib o Figure de la GUI a cadena Base64 PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    plt.close(fig) if hasattr(fig, 'canvas') else None
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def _obtener_datos_completos(resultado: ResultadoZernike, grid_size: int = 100):
    """
    Reconstruye X, Y, W y W_fit en caso de que resultado provenga de ZemaxViewDialog
    o contenga datos planos/incompletos.
    """
    A = resultado.A
    if len(A) == 0:
        A = np.zeros(21)

    if len(resultado.X) > 0 and len(resultado.W_fit) > 0 and len(resultado.X) == len(resultado.W_fit):
        X = resultado.X
        Y = resultado.Y
        W_fit = resultado.W_fit
        W_exp = resultado.W if len(resultado.W) == len(X) else W_fit
    else:
        x_lin = np.linspace(-1.0, 1.0, grid_size)
        y_lin = np.linspace(-1.0, 1.0, grid_size)
        Xi, Yi = np.meshgrid(x_lin, y_lin)
        X = Xi.ravel()
        Y = Yi.ravel()
        pols = polinomios_zernike()[:len(A)]
        U = evaluar_polinomios(X, Y, pols)
        W_fit = U.T @ A
        W_exp = W_fit

    return X, Y, W_exp, W_fit


def _generar_graficas_reporte(resultado: ResultadoZernike) -> tuple[str, str, str, str]:
    """
    Reutiliza exactamente los mismos generadores gráficos de la GUI:
    1. Malla CCD & Pupila Circular (graficar_pupila)
    2. Error Residual 3D (mapa_fase_3d)
    3. Interferograma Sintético Reconstruido (graficar_interferograma_sintetico)
    4. Espectro de Aberraciones con Colores Golosina Vivos (_COL)
    """
    X, Y, W_exp, W_fit = _obtener_datos_completos(resultado)
    error_residual = W_exp - W_fit

    # -------------------------------------------------------------------------
    # Figura 1: Malla CCD & Pupila Circular Unitarias
    # -------------------------------------------------------------------------
    mascara_pupila = (X**2 + Y**2) <= 1.0
    fig1 = graficar_pupila(X, Y, mascara_pupila, R=1.0)
    b64_malla_ccd = _fig_to_base64(fig1)

    # -------------------------------------------------------------------------
    # Figura 2: Error Residual 3D (W_exp - W_fit)
    # -------------------------------------------------------------------------
    fig2 = mapa_fase_3d(X, Y, error_residual, title='Error Residual 3D (W_exp - W_fit)', cmap='viridis', n_grid=80)
    b64_error_residual = _fig_to_base64(fig2)

    # -------------------------------------------------------------------------
    # Figura 3: Interferograma Sintético Reconstruido (Idéntico a la GUI)
    # -------------------------------------------------------------------------
    fig3 = graficar_interferograma_sintetico(resultado.A, is_dark=False, N=256, franjas_carrier=12)
    b64_interferograma = _fig_to_base64(fig3)

    # -------------------------------------------------------------------------
    # Figura 4: Distribución de Aberraciones de Zernike (Colores Golosina Vivos)
    # -------------------------------------------------------------------------
    fig4 = graficar_espectro_aberraciones(resultado.A, is_dark=False)
    b64_espectro = _fig_to_base64(fig4)

    return b64_malla_ccd, b64_error_residual, b64_interferograma, b64_espectro


def generar_html_reporte(resultado: ResultadoZernike, titulo="Reporte Metrológico de Calidad Óptica") -> str:
    """Genera el código HTML5 completo utilizando 4 cifras significativas (precision=4.4f)."""
    A = resultado.A
    num_coef = len(A)

    # Métricas metrológicas expresadas con 4 cifras decimales
    rms_total = float(np.sqrt(np.sum(A[1:]**2))) if len(A) > 1 else 0.0
    power_defocus = float(A[4]) if len(A) >= 5 else 0.0
    
    indices_irreg = [i for i in range(len(A)) if i not in (0, 1, 2, 4)]
    irregularity = float(np.sqrt(np.sum(A[indices_irreg]**2))) if indices_irreg else 0.0
    
    pv_estimado = float(2.0 * np.sum(np.abs(A[1:]))) if len(A) > 1 else 0.0
    puntos_eval = len(resultado.X) if len(resultado.X) > 0 else (len(resultado.U) if len(resultado.U) > 0 else 10000)

    seidel_rms = float(np.sqrt(np.sum(A[1:9]**2))) if len(A) >= 9 else (float(np.sqrt(np.sum(A[1:]**2))) if len(A) > 1 else 0.0)
    high_order_rms = float(np.sqrt(np.sum(A[9:]**2))) if len(A) > 9 else 0.0

    b64_malla_ccd, b64_error_residual, b64_interferograma, b64_espectro = _generar_graficas_reporte(resultado)
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Filas de la tabla con 4 cifras decimales y badges temáticos golosina
    filas_tabla = []
    for r in range(1, num_coef + 1):
        if r <= len(INFORMACION_ZERNIKE_ISO):
            info = INFORMACION_ZERNIKE_ISO[r - 1]
            n_val, m_val, nombre_val = info['n'], info['m'], info['nombre']
        else:
            n_val, m_val, nombre_val = 0, 0, f"Término Z_{r}"

        c_hex = COLORES_GOLOSINA_21[(r - 1) % len(COLORES_GOLOSINA_21)]
        coef_val = A[r - 1]
        filas_tabla.append(
            f"<tr>"
            f"<td style='text-align:center;'><span style='background-color:{c_hex}; color:#ffffff; padding:2px 7px; border-radius:4px; font-weight:bold; font-size:10px;'>Z<sub>{r}</sub></span></td>"
            f"<td style='text-align:center;'>(n={n_val}, m={m_val:2d})</td>"
            f"<td style='text-align:right; font-family:monospace; font-weight:bold;'>{coef_val:+.4f} λ</td>"
            f"<td>{nombre_val}</td>"
            f"</tr>"
        )
    html_filas_tabla = "\n".join(filas_tabla)

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo}</title>
    <style>
        @page {{ size: A4; margin: 12mm; }}
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #0f172a;
            background-color: #ffffff;
            margin: 0;
            padding: 15px;
            font-size: 11px;
            line-height: 1.4;
        }}
        .header {{
            border-bottom: 3px solid #1e3a8a;
            padding-bottom: 8px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header-title {{
            font-size: 18px;
            font-weight: bold;
            color: #1e3a8a;
            margin: 0;
        }}
        .header-subtitle {{
            font-size: 10px;
            color: #475569;
            margin-top: 3px;
        }}
        .meta-info {{
            text-align: right;
            font-size: 9px;
            color: #64748b;
        }}
        .section-title {{
            font-size: 13px;
            font-weight: bold;
            color: #1e3a8a;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 3px;
            margin-top: 16px;
            margin-bottom: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
            margin-bottom: 16px;
        }}
        .metric-card {{
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 5px;
            padding: 8px;
            text-align: center;
        }}
        .metric-label {{
            font-size: 9px;
            font-weight: bold;
            color: #475569;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 14px;
            font-weight: bold;
            color: #1e3a8a;
            margin-top: 3px;
        }}
        .img-grid-two {{
            display: flex;
            gap: 12px;
            justify-content: center;
            align-items: center;
            margin: 12px 0;
        }}
        .img-card {{
            flex: 1;
            text-align: center;
        }}
        .img-card img {{
            max-width: 100%;
            max-height: 240px;
            height: auto;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
            font-size: 10px;
        }}
        th {{
            background-color: #1e3a8a;
            color: #ffffff;
            font-weight: bold;
            padding: 5px;
            text-align: left;
        }}
        td {{
            padding: 4px 5px;
            border-bottom: 1px solid #e2e8f0;
        }}
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        .footer {{
            margin-top: 25px;
            border-top: 1px solid #cbd5e1;
            padding-top: 6px;
            font-size: 8px;
            color: #94a3b8;
            text-align: center;
        }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <div class="header-title">{titulo}</div>
            <div class="header-subtitle">Análisis Metrológico de Superficie Óptica — Norma ISO 10110-5 / ANSI Z80.28</div>
        </div>
        <div class="meta-info">
            <strong>Fecha:</strong> {fecha_hora}<br>
            <strong>Software:</strong> Proyecto Zernike v0.1.0<br>
            <strong>Pupila Normalizada:</strong> Disco Circular (ρ ≤ 1.0000)
        </div>
    </div>

    <div class="section-title">1. Resumen Metrológico de Calidad de Superficie (4 Cifras Signif.)</div>
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">RMS Global</div>
            <div class="metric-value">{rms_total:.4f} λ</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Peak-to-Valley (P-V)</div>
            <div class="metric-value">{pv_estimado:.4f} λ</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Power (Desenfoque A5)</div>
            <div class="metric-value">{power_defocus:.4f} λ</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Irregularidad</div>
            <div class="metric-value">{irregularity:.4f} λ</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Puntos Evaluados</div>
            <div class="metric-value">{puntos_eval}</div>
        </div>
    </div>

    <div class="section-title">2. Descomposición Aberracional de Seidel vs Alto Orden</div>
    <div style="display: flex; gap: 12px; margin-bottom: 12px;">
        <div style="flex: 1; background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 8px; border-radius: 5px;">
            <strong>Aberraciones Primarias de Seidel (3er Orden A2..A9):</strong><br>
            Error RMS = <strong>{seidel_rms:.4f} λ</strong>
        </div>
        <div style="flex: 1; background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 8px; border-radius: 5px;">
            <strong>Aberraciones de Alto Orden (5to+ Orden A10..A21):</strong><br>
            Error RMS = <strong>{high_order_rms:.4f} λ</strong>
        </div>
    </div>

    <div class="section-title">3. Gráficas Principales: Malla CCD y Error Residual 3D</div>
    <div class="img-grid-two">
        <div class="img-card">
            <img src="data:image/png;base64,{b64_malla_ccd}" alt="Malla CCD & Pupila">
        </div>
        <div class="img-card">
            <img src="data:image/png;base64,{b64_error_residual}" alt="Error Residual 3D">
        </div>
    </div>

    <div class="section-title">4. Interferograma Sintético Reconstruido e Espectro de Aberraciones</div>
    <div class="img-grid-two">
        <div class="img-card">
            <img src="data:image/png;base64,{b64_interferograma}" alt="Interferograma Sintético">
        </div>
        <div class="img-card">
            <img src="data:image/png;base64,{b64_espectro}" alt="Distribución de Coeficientes">
        </div>
    </div>

    <div class="section-title">5. Tabla Completa de los 21 Coeficientes de Zernike (ISO 10110-5)</div>
    <table>
        <thead>
            <tr>
                <th style="width: 12%; text-align:center;">Término</th>
                <th style="width: 15%; text-align:center;">Índice (n, m)</th>
                <th style="width: 25%; text-align:right;">Coeficiente (A_r)</th>
                <th style="width: 48%;">Descripción Física</th>
            </tr>
        </thead>
        <tbody>
            {html_filas_tabla}
        </tbody>
    </table>

    <div class="footer">
        Documento generado por la Suite Metrológica Proyecto Zernike (Norma ISO 10110-5). Todos los derechos reservados.
    </div>

</body>
</html>
"""
    return html_content


def exportar_reporte_html(resultado: ResultadoZernike, filepath_html: str, titulo="Reporte Metrológico de Calidad Óptica") -> bool:
    """Exporta el reporte en formato HTML5 autocontenido."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath_html)), exist_ok=True)
        html_code = generar_html_reporte(resultado, titulo=titulo)
        with open(filepath_html, 'w', encoding='utf-8') as f:
            f.write(html_code)
        return True
    except Exception as e:
        print(f"Error al generar reporte HTML: {e}")
        return False
