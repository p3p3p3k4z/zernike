"""
lib/visualizacion.py
====================
Animacion del flujo recursivo de Zernike.

Una sola barra por polinomio r=0..L-1. Conforme avanza el algoritmo
se van superponiendo capas de color sobre la misma barra, pero en el
orden EXACTO en que el algoritmo calcula las variables, ilustrando
las dependencias reales (ej. V_r depende de U_r, D_r y V_{p<r}).
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
from matplotlib.figure import Figure

_VARS = ['U', 'V', 'D', 'B', 'C', 'A']

_COL = {
    'U': '#FF4757',
    'V': '#2ED573',
    'D': '#FFA502',
    'B': '#1E90FF',
    'C': '#E040FB',
    'A': '#FFDD00',
}

def generar_eventos(L):
    """Genera la secuencia exacta de cálculo de la base recursiva de polinomios de Zernike (U, V, D, B)."""
    events = []
    
    # 1. Evaluar Base Zernike U
    for r in range(L):
        events.append({'action': 'add', 'r': r, 'var': 'U', 'deps': [], 'title': f'Base Zernike U_{r+1}'})
        
    # 2. Ortogonalización Gram-Schmidt (V y D intercalados)
    events.append({'action': 'add', 'r': 0, 'var': 'V', 'deps': [('U', 0)], 'title': 'Gram-Schmidt: V_1 = U_1'})
    for r in range(1, L):
        deps_D = [('U', r)] + [('V', p) for p in range(r)]
        events.append({'action': 'add', 'r': r, 'var': 'D', 'deps': deps_D, 'title': f'Gram-Schmidt: D_{r+1} (Proyección Ortogonal)'})
        deps_V = [('U', r), ('D', r)] + [('V', p) for p in range(r)]
        events.append({'action': 'add', 'r': r, 'var': 'V', 'deps': deps_V, 'title': f'Gram-Schmidt: V_{r+1} (Polinomio Ortogonal)'})
        
    # 3. Pesos de Ajuste B
    for r in range(L):
        events.append({'action': 'add', 'r': r, 'var': 'B', 'deps': [('V', r)], 'title': f'Amplitud de Ajuste B_{r+1} = <W, V_{r+1}> / F_{r+1}'})
        
    return events


def graficar_flujo_zernike(resultados, intervalo_ms=180, repetir=False):
    """
    Animacion de superposicion de capas de color.
    Incluye flechas de saltos hacia atras/adelante apuntando exactamente
    a la variable (capa) de la cual depende.
    """
    L = len(resultados.B)
    n_fases = len(_VARS)
    capa_h = 1.0

    fig, ax = plt.subplots(figsize=(18, 6.5))

    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.tick_params(colors='#555555', length=0, labelsize=9)

    ax.set_title('Polinomios de Zernike', fontsize=17,
                 fontweight='bold', color='#1A1A1A', pad=14)
    ax.set_xlim(-0.7, L - 0.3)
    ax.set_ylim(0, n_fases * capa_h + 3.5)
    ax.set_xticks(np.arange(L))
    ax.set_xticklabels([f'r{i+1}' for i in range(L)], fontsize=8.5, color='#666666')

    patches = [mpatches.Patch(color=_COL[v], label=v) for v in _VARS]
    ax.legend(handles=patches, loc='upper right', frameon=False,
              fontsize=12, ncol=n_fases, handlelength=1.3)

    ind_var = ax.text(
        0.01, 0.95, '', transform=ax.transAxes,
        fontsize=14, fontweight='bold', va='top', ha='left',
    )

    bases = np.zeros(L)
    events = generar_eventos(L)
    total_frames = len(events) + 12

    estado = {'flechas': [], 'layer_heights': {}}

    def _actualizar(frame):
        for flecha in estado['flechas']:
            flecha.remove()
        estado['flechas'].clear()

        if frame >= len(events):
            return [ind_var]

        ev = events[frame]
        r = ev['r']
        var = ev['var']
        color = _COL[var]

        # 1. Dibujar la nueva capa sobre la barra r
        bottom_y = bases[r]
        ax.bar(
            r, capa_h, bottom=bottom_y,
            width=0.72,
            color=color,
            edgecolor='white',
            linewidth=0.5,
        )
        bases[r] += capa_h
        
        # Guardar la altura del centro de esta capa para que las flechas apunten aqui
        centro_y = bottom_y + capa_h / 2.0
        estado['layer_heights'][(r, var)] = centro_y

        # 2. Dibujar flechas de dependencia matematica
        x_origen = r
        y_origen = centro_y

        for dep_var, dep_r in ev['deps']:
            if (dep_r, dep_var) in estado['layer_heights']:
                x_destino = dep_r
                y_destino = estado['layer_heights'][(dep_r, dep_var)]
                
                distancia = x_destino - x_origen
                if distancia == 0:
                    curvatura = 0.5
                else:
                    curvatura = 0.1 + abs(distancia) * 0.05
                    if distancia > 0:
                        curvatura = -curvatura
                
                flecha = ax.annotate(
                    '',
                    xy=(x_destino, y_destino),
                    xytext=(x_origen, y_origen),
                    arrowprops=dict(
                        arrowstyle='->',
                        color=color,
                        linewidth=1.3,
                        alpha=0.6,
                        connectionstyle=f"arc3,rad={curvatura}"
                    )
                )
                estado['flechas'].append(flecha)

        ind_var.set_text(ev['title'])
        ind_var.set_color(color)
        return [ind_var]

    anim = animation.FuncAnimation(
        fig,
        _actualizar,
        frames=total_frames,
        interval=intervalo_ms,
        blit=False,
        repeat=repetir,
    )

    plt.tight_layout()
    return fig, anim


def graficar_distribucion_ccd(
    X_c: np.ndarray,
    Y_c: np.ndarray,
) -> plt.Figure:
    """
    Plano cartesiano simple con todos los puntos de los 4 cuadrantes
    antes de aplicar el filtro de la pupila.

    Parametros
    ----------
    X_c, Y_c : ndarray -- coordenadas de todos los puntos
    """
    fig, ax = plt.subplots(figsize=(6, 6))

    ax.scatter(X_c, Y_c, c=_COL['B'], s=14, alpha=0.75, linewidths=0)

    ax.axhline(0, color='#AAAAAA', linewidth=0.8, linestyle='--')
    ax.axvline(0, color='#AAAAAA', linewidth=0.8, linestyle='--')

    ax.set_title('Distribucion de puntos — 4 Cuadrantes', fontsize=12)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.25)

    plt.tight_layout()
    return fig


def graficar_pupila(
    X_c: np.ndarray,
    Y_c: np.ndarray,
    mascara: np.ndarray,
    R: float,
) -> plt.Figure:
    """
    Plano cartesiano con puntos coloreados segun si caen dentro (verde)
    o fuera (rojo) de la pupila, con el circulo de la pupila dibujado.

    Parametros
    ----------
    X_c, Y_c : ndarray      -- coordenadas de todos los puntos
    mascara  : ndarray bool -- True si el punto esta dentro de la pupila
    R        : float        -- radio de la pupila
    """
    fig, ax = plt.subplots(figsize=(6, 6))

    n_tot = len(X_c)
    if n_tot > 6000:
        # Muestreo representativo para rendering 2D ultrarrápido
        idx_render = np.random.choice(n_tot, size=6000, replace=False)
        X_sub, Y_sub, mask_sub = X_c[idx_render], Y_c[idx_render], mascara[idx_render]
    else:
        X_sub, Y_sub, mask_sub = X_c, Y_c, mascara

    ax.scatter(
        X_sub[~mask_sub], Y_sub[~mask_sub],
        c=_COL['U'], s=14, alpha=0.55, linewidths=0,
        label=f'Fuera  ({(~mascara).sum()})',
    )
    ax.scatter(
        X_sub[mask_sub], Y_sub[mask_sub],
        c=_COL['V'], s=14, alpha=0.85, linewidths=0,
        label=f'Dentro ({mascara.sum()})',
    )

    circulo = plt.Circle(
        (0, 0), R,
        color=_COL['D'], fill=False, linewidth=2.0,
        label=f'Pupila  R={R:.1f}',
    )
    ax.add_patch(circulo)

    ax.axhline(0, color='#AAAAAA', linewidth=0.8, linestyle='--')
    ax.axvline(0, color='#AAAAAA', linewidth=0.8, linestyle='--')

    ax.set_title(f'Filtrado por pupila  (R = {R:.1f})', fontsize=12)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend(loc='upper right', fontsize=9, frameon=True)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.25)

    plt.tight_layout()
    return fig


def _filtro_gaussiano_2d(Zi: np.ndarray, sigma: float) -> np.ndarray:
    """Aplica suavizado gaussiano 2D usando scipy si esta disponible, o NumPy puro como fallback."""
    if sigma <= 0.0:
        return Zi
    try:
        from scipy.ndimage import gaussian_filter
        Zi_zero = np.nan_to_num(Zi, nan=0.0)
        return gaussian_filter(Zi_zero, sigma=sigma, mode='nearest')
    except ImportError:
        radius = int(np.ceil(3 * sigma))
        if radius < 1:
            radius = 1
        x = np.arange(-radius, radius + 1)
        kernel_1d = np.exp(-0.5 * (x / sigma) ** 2)
        kernel_1d /= kernel_1d.sum()

        Zi_zero = np.nan_to_num(Zi, nan=0.0)
        out = np.apply_along_axis(lambda m: np.convolve(m, kernel_1d, mode='same'), axis=1, arr=Zi_zero)
        out = np.apply_along_axis(lambda m: np.convolve(m, kernel_1d, mode='same'), axis=0, arr=out)
        return out


def mapa_fase_3d(X_c, Y_c, Z_diff, title='Error Residual 3D', cmap='viridis', z_scale=1.0, wireframe=False, show_grid=True, n_grid=80, sigma=0.0):
    """
    Genera una representación gráfica tridimensional continua del mapa de fase o error residual (Z_exp - Z_fit) mediante interpolación en grilla regular y filtrado gaussiano opcional.
    Se usa Figure() directamente para no registrar la figura en el gestor de pyplot (Gcf),
    evitando la aparicion de una ventana nativa vacia (FigureManagerQT) en ejecutables Windows.
    El figsize no se fija aqui: MplCanvasWidget.set_figure() ajusta la figura
    al tamanio real del canvas tras el ciclo de layout de Qt.

    Parametros
    ----------
    X_c, Y_c : np.ndarray
        Coordenadas de la pupila.
    Z_diff : np.ndarray
        Valores de altura / amplitud del error residual.
    title : str
        Titulo del grafico.
    cmap : str
        Mapa de colores (colormap).
    z_scale : float
        Escala manual del eje vertical Z.
    wireframe : bool
        Si es True, renderiza como malla de alambre.
    show_grid : bool
        Si es True, muestra la cuadricula de los ejes 3D.
    n_grid : int
        Resolucion de la grilla regular de interpolacion (n_grid x n_grid).
    sigma : float
        Nivel de suavizado gaussiano (0.0 = sin suavizado).
    """
    fig = Figure()
    ax = fig.add_subplot(111, projection='3d')

    Z_scaled = Z_diff * z_scale

    # 1. Generar grilla cartesiana regular en el disco unitario [-1, 1]
    xi = np.linspace(-1.0, 1.0, n_grid)
    yi = np.linspace(-1.0, 1.0, n_grid)
    Xi, Yi = np.meshgrid(xi, yi)

    # 2. Interpolar datos dispersos a la grilla regular (scipy cubic o matplotlib tri fallback)
    Zi = None
    try:
        from scipy.interpolate import griddata
        Zi = griddata((X_c, Y_c), Z_scaled, (Xi, Yi), method='cubic')
    except (ImportError, Exception):
        pass

    if Zi is None or np.all(np.isnan(Zi)):
        try:
            import matplotlib.tri as tri
            triang = tri.Triangulation(X_c, Y_c)
            interpolator = tri.LinearTriInterpolator(triang, Z_scaled)
            Zi = interpolator(Xi, Yi)
        except Exception:
            pass

    if Zi is None or np.all(np.isnan(Zi)):
        try:
            from scipy.interpolate import griddata
            Zi = griddata((X_c, Y_c), Z_scaled, (Xi, Yi), method='nearest')
        except (ImportError, Exception):
            pass

    if Zi is None or np.all(np.isnan(Zi)):
        Zi = np.zeros_like(Xi)

    # 3. Aplicar mascara de pupila circular unitaria (rho <= 1.0)
    mascara_pupila = (Xi**2 + Yi**2) > 1.0
    Zi[mascara_pupila] = np.nan

    # 4. Aplicar filtro de suavizado gaussiano opcional
    if sigma > 0.0:
        Zi_smooth = _filtro_gaussiano_2d(Zi, sigma)
        Zi_smooth[mascara_pupila] = np.nan
        Zi = Zi_smooth

    # 5. Renderizar superficie continua o malla de alambre
    if wireframe:
        surf = ax.plot_wireframe(Xi, Yi, Zi, rstride=2, cstride=2, cmap=cmap, linewidth=0.6, alpha=0.9)
    else:
        surf = ax.plot_surface(Xi, Yi, Zi, cmap=cmap, linewidth=0, antialiased=True, alpha=0.85, rstride=1, cstride=1)

    fig.colorbar(surf, shrink=0.5, aspect=10, pad=0.1, label='Magnitud Z')

    ax.set_title(title)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Amplitud Z')
    ax.grid(show_grid)

    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig


# =============================================================================
# FUNCIONES DE VISUALIZACION PARA LAS 4 ETAPAS DE INTERFEROMETRIA
# =============================================================================

def graficar_interferograma_original(matriz_img: np.ndarray, is_dark: bool = False) -> Figure:
    """
    Etapa 1: Grafica la imagen original del interferograma en escala de grises.
    Usa Figure() directamente para evitar la creacion de ventanas nativas en ejecutables Windows.
    """
    bg_color = '#2E3440' if is_dark else '#FFFFFF'
    text_color = '#ECEFF4' if is_dark else '#0F172A'

    fig = Figure(figsize=(6, 5), facecolor=bg_color)
    ax = fig.add_subplot(111, facecolor=bg_color)
    im = ax.imshow(matriz_img, cmap='gray', origin='lower', extent=[-1, 1, -1, 1])
    ax.set_title("Etapa 1: Interferograma Original", fontsize=11, fontweight='bold', color=text_color)
    ax.set_xlabel("X (normalizado)", color=text_color)
    ax.set_ylabel("Y (normalizado)", color=text_color)
    ax.tick_params(colors=text_color)

    cb = fig.colorbar(im, ax=ax)
    cb.ax.tick_params(colors=text_color)
    fig.tight_layout()
    return fig


def graficar_espectro_fft2d(espectro_log: np.ndarray, mascara_filtro: np.ndarray, is_dark: bool = False) -> Figure:
    """
    Etapa 2: Grafica el espectro de frecuencias 2D en escala logaritmica con la mascara del filtro.
    Usa Figure() directamente para evitar la creacion de ventanas nativas en ejecutables Windows.
    """
    bg_color = '#2E3440' if is_dark else '#FFFFFF'
    text_color = '#ECEFF4' if is_dark else '#0F172A'

    fig = Figure(figsize=(6, 5), facecolor=bg_color)
    ax = fig.add_subplot(111, facecolor=bg_color)
    im = ax.imshow(espectro_log, cmap='magma', origin='lower')
    if mascara_filtro is not None:
        ax.contour(mascara_filtro, levels=[0.5], colors='cyan', linewidths=1.8)
    ax.set_title("Etapa 2: Espectro FFT 2D y Filtro Pase-Banda", fontsize=11, fontweight='bold', color=text_color)
    ax.tick_params(colors=text_color)

    cb = fig.colorbar(im, ax=ax)
    cb.ax.tick_params(colors=text_color)
    fig.tight_layout()
    return fig


def graficar_fase_enrollada(fase_enrollada: np.ndarray, is_dark: bool = False) -> Figure:
    """
    Etapa 3: Grafica la fase enrollada (wrapped phase) en el intervalo [-pi, +pi].
    Usa Figure() directamente para evitar la creacion de ventanas nativas en ejecutables Windows.
    """
    bg_color = '#2E3440' if is_dark else '#FFFFFF'
    text_color = '#ECEFF4' if is_dark else '#0F172A'

    fig = Figure(figsize=(6, 5), facecolor=bg_color)
    ax = fig.add_subplot(111, facecolor=bg_color)
    im = ax.imshow(fase_enrollada, cmap='twilight', origin='lower', extent=[-1, 1, -1, 1])
    ax.set_title("Etapa 3: Fase Enrollada [-pi, +pi]", fontsize=11, fontweight='bold', color=text_color)
    ax.set_xlabel("X", color=text_color)
    ax.set_ylabel("Y", color=text_color)
    ax.tick_params(colors=text_color)

    cb = fig.colorbar(im, ax=ax)
    cb.ax.tick_params(colors=text_color)
    fig.tight_layout()
    return fig


def graficar_fase_continua_y_puntos(fase_continua: np.ndarray, X_pts: np.ndarray = None, Y_pts: np.ndarray = None, is_dark: bool = False) -> Figure:
    """
    Etapa 4: Grafica el mapa de fase continuo (OPD) con la superposicion de los puntos extraidos.
    Usa Figure() directamente para evitar la creacion de ventanas nativas en ejecutables Windows.
    """
    bg_color = '#2E3440' if is_dark else '#FFFFFF'
    text_color = '#ECEFF4' if is_dark else '#0F172A'

    fig = Figure(figsize=(6, 5), facecolor=bg_color)
    ax = fig.add_subplot(111, facecolor=bg_color)
    im = ax.imshow(fase_continua, cmap='viridis', origin='lower', extent=[-1, 1, -1, 1])

    if X_pts is not None and len(X_pts) > 0:
        idx_sample = np.random.choice(len(X_pts), size=min(1200, len(X_pts)), replace=False)
        ax.scatter(X_pts[idx_sample], Y_pts[idx_sample], s=3, c='cyan', alpha=0.6, label=f'Puntos Extraidos ({len(X_pts)})')
        leg = ax.legend(loc='upper right', fontsize=8)
        if leg:
            leg.get_frame().set_facecolor(bg_color)
            for text in leg.get_texts():
                text.set_color(text_color)

    ax.set_title("Etapa 4: Fase Desenvolviendo & Puntos Extraidos", fontsize=11, fontweight='bold', color=text_color)
    ax.set_xlabel("X", color=text_color)
    ax.set_ylabel("Y", color=text_color)
    ax.tick_params(colors=text_color)

    cb = fig.colorbar(im, ax=ax)
    cb.ax.tick_params(colors=text_color)
    fig.tight_layout()
    return fig


def graficar_interferograma_sintetico(A_coefs: np.ndarray, is_dark: bool = False, N: int = 256, franjas_carrier: int = 12) -> Figure:
    """
    Sintetiza y grafica la imagen 2D del interferograma a partir de los coeficientes A de Zernike.
    Usa Figure() directamente para evitar la creacion de ventanas nativas en ejecutables Windows.
    """
    from lib.interferometria import sintetizar_interferograma_desde_zernike

    interferograma, X_grid, Y_grid, W_fit_2d = sintetizar_interferograma_desde_zernike(
        A_coefs=A_coefs, N=N, franjas_carrier=franjas_carrier
    )

    bg_color = '#1e1e2e' if is_dark else '#ffffff'
    text_color = '#ffffff' if is_dark else '#000000'

    fig = Figure(figsize=(6, 5), facecolor=bg_color)
    ax = fig.add_subplot(111, facecolor=bg_color)

    im = ax.imshow(interferograma, cmap='gray', extent=[-1, 1, -1, 1], origin='lower')
    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.ax.yaxis.set_tick_params(color=text_color)
    for label in cbar.ax.get_yticklabels():
        label.set_color(text_color)
    cbar.set_label('Intensidad Norm. I(x,y)', color=text_color)

    ax.set_title("Interferograma Sintetico Reconstruido (Zernike)", color=text_color, fontsize=11, fontweight='bold')
    ax.set_xlabel("X (pupila normalizada)", color=text_color)
    ax.set_ylabel("Y (pupila normalizada)", color=text_color)
    ax.tick_params(colors=text_color)
    for spine in ax.spines.values():
        spine.set_color(text_color)

    fig.tight_layout()
    return fig


def mapa_zernike_2d(
    X_c: np.ndarray,
    Y_c: np.ndarray,
    Z_poly: np.ndarray,
    title: str = 'Polinomio de Zernike 2D',
    cmap: str = 'gray',
    modo_render: str = 'interferograma',
    n_franjas: float = 2.0,
    show_contours: bool = False,
    show_grid: bool = True,
    n_grid: int = 160
) -> Figure:
    """
    Genera la representación gráfica bidimensional de un Polinomio de Zernike.
    Soporta dos modos:
      - 'interferograma': Modulación por coseno I(x,y) = (1 + cos(2π * n_franjas * Z))/2 (Patrón de Franjas de Interferencia).
      - 'fase' / 'elevacion': Elevación continua de la fase Z(x,y).
    """
    fig = Figure()
    ax = fig.add_subplot(111)

    xi = np.linspace(-1.0, 1.0, n_grid)
    yi = np.linspace(-1.0, 1.0, n_grid)
    Xi, Yi = np.meshgrid(xi, yi)

    Zi = None
    try:
        from scipy.interpolate import griddata
        Zi = griddata((X_c, Y_c), Z_poly, (Xi, Yi), method='cubic')
    except (ImportError, Exception):
        pass

    if Zi is None or np.all(np.isnan(Zi)):
        try:
            import matplotlib.tri as tri
            triang = tri.Triangulation(X_c, Y_c)
            interpolator = tri.LinearTriInterpolator(triang, Z_poly)
            Zi = interpolator(Xi, Yi)
        except Exception:
            pass

    if Zi is None or np.all(np.isnan(Zi)):
        Zi = np.zeros_like(Xi)

    mascara_pupila = (Xi**2 + Yi**2) > 1.0
    Zi[mascara_pupila] = np.nan

    if modo_render.lower() in ('interferograma', 'franjas'):
        # Modulación cosenoidal de interferometría sintética I = (1 + cos(2π * N * Z)) / 2
        Zi_plot = 0.5 + 0.5 * np.cos(2.0 * np.pi * n_franjas * Zi)
        cbar_label = 'Intensidad Norm. I(x,y)'
    else:
        Zi_plot = Zi
        cbar_label = 'Fase Z(x,y)'

    im = ax.imshow(Zi_plot, cmap=cmap, extent=[-1, 1, -1, 1], origin='lower')
    if show_contours:
        try:
            color_contorno = 'red' if cmap in ('gray', 'binary', 'gist_gray') else 'black'
            ax.contour(Xi, Yi, Zi, levels=10, colors=color_contorno, alpha=0.5, linewidths=0.8)
        except Exception:
            pass

    fig.colorbar(im, ax=ax, shrink=0.85, label=cbar_label)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xlabel('X (normalizado)')
    ax.set_ylabel('Y (normalizado)')
    if show_grid:
        ax.grid(True, alpha=0.3)
    else:
        ax.grid(False)

    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig


# Paleta de 21 Colores Golosina Vivos, Distintivos y Únicos para Z_1..Z_21
COLORES_GOLOSINA_21 = [
    '#FF4757',  # Z1: Rojo Coral Golosina
    '#FF7F50',  # Z2: Coral Cálido
    '#FFA502',  # Z3: Naranja Caramelo
    '#FFD700',  # Z4: Amarillo Oro Vivo
    '#FFDD00',  # Z5: Amarillo Limón Vivo
    '#A3CB38',  # Z6: Verde Manzana Candy
    '#2ED573',  # Z7: Verde Menta Golosina
    '#00D2D3',  # Z8: Turquesa Neón
    '#1E90FF',  # Z9: Azul Eléctrico Golosina
    '#3742FA',  # Z10: Azul Uva Neón
    '#5F27CD',  # Z11: Púrpura Golosina
    '#8E44AD',  # Z12: Morado Ciruela
    '#E040FB',  # Z13: Magenta Golosina Vivo
    '#FF007F',  # Z14: Fucsia Chicle
    '#FF1E56',  # Z15: Rojo Frambuesa
    '#FF6B6B',  # Z16: Rojo Sandía Candy
    '#FF9FF3',  # Z17: Rosa Chicle Pastel
    '#00E676',  # Z18: Verde Esmeralda Neón
    '#00B894',  # Z19: Verde Menta Neón
    '#00CEC9',  # Z20: Cian Pastel Golosina
    '#74B9FF',  # Z21: Azul Cielo Candy
]


def graficar_espectro_aberraciones(
    A_coefs: np.ndarray,
    is_dark: bool = False,
    title: str = "Distribución de Aberraciones por Coeficiente de Zernike (ISO 10110-5)",
    annotate_values: bool = False
) -> Figure:
    """
    Genera la gráfica de espectro de aberraciones de Zernike en barras de 21 colores golosina.
    Usa Figure() directamente para evitar la creación de ventanas nativas vacías en ejecutables.
    """
    num_coef = len(A_coefs)
    indices = np.arange(1, num_coef + 1)

    bg_color = '#1e293b' if is_dark else '#ffffff'
    text_color = '#f8fafc' if is_dark else '#0f172a'
    title_color = '#93c5fd' if is_dark else '#1e3a8a'
    grid_color = '#475569' if is_dark else '#cbd5e1'

    fig = Figure(figsize=(8.5, 3.8), facecolor=bg_color)
    ax = fig.add_subplot(111, facecolor=bg_color)

    colores_barras = [COLORES_GOLOSINA_21[(r - 1) % len(COLORES_GOLOSINA_21)] for r in indices]
    bars = ax.bar(indices, A_coefs, color=colores_barras, edgecolor=grid_color, linewidth=0.9, alpha=0.9)
    ax.axhline(0, color=grid_color, linewidth=1, linestyle='--')

    ax.set_title(title, fontsize=10, fontweight='bold', color=title_color)
    ax.set_xlabel("Índice de Zernike (r)", fontsize=9, fontweight='bold', color=text_color)
    ax.set_ylabel("Coeficiente A_r [λ]", fontsize=9, fontweight='bold', color=text_color)
    ax.set_xticks(indices)
    ax.set_xticklabels([f"Z_{r}" for r in indices], rotation=45, fontsize=7, fontweight='bold', color=text_color)
    ax.tick_params(colors=text_color)
    ax.grid(True, linestyle=':', alpha=0.5, color=grid_color)

    if annotate_values:
        for bar, val in zip(bars, A_coefs):
            height = bar.get_height()
            va = 'bottom' if height >= 0 else 'top'
            y_pos = height + (0.003 if height >= 0 else -0.003)
            ax.annotate(
                f'{val:+.4f}',
                xy=(bar.get_x() + bar.get_width() / 2, y_pos),
                xytext=(0, 0),
                textcoords="offset points",
                ha='center', va=va,
                fontsize=7, fontweight='bold', color=text_color
            )

    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig





