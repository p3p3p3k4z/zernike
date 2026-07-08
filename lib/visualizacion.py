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
    """Genera la secuencia exacta de calculos del algoritmo."""
    events = []
    
    # 1. Evaluar U
    for r in range(L):
        events.append({'action': 'add', 'r': r, 'var': 'U', 'deps': [], 'title': f'Base Zernike U_{r}'})
        
    # 2. Gram-Schmidt (V y D intercalados)
    events.append({'action': 'add', 'r': 0, 'var': 'V', 'deps': [('U', 0)], 'title': 'Gram-Schmidt: V_0 = U_0'})
    for r in range(1, L):
        deps_D = [('U', r)] + [('V', p) for p in range(r)]
        events.append({'action': 'add', 'r': r, 'var': 'D', 'deps': deps_D, 'title': f'Gram-Schmidt: D_{r} (Proyeccion)'})
        deps_V = [('U', r), ('D', r)] + [('V', p) for p in range(r)]
        events.append({'action': 'add', 'r': r, 'var': 'V', 'deps': deps_V, 'title': f'Gram-Schmidt: V_{r} (Ortogonalizacion)'})
        
    # 3. Pesos ortogonales B
    for r in range(L):
        events.append({'action': 'add', 'r': r, 'var': 'B', 'deps': [('V', r)], 'title': f'Pesos B_{r} = <W, V_{r}> / F_{r}'})
        
    # 4. Matriz de traduccion C
    events.append({'action': 'add', 'r': 0, 'var': 'C', 'deps': [], 'title': 'Traduccion C_0'})
    for r in range(1, L):
        deps_C = [('D', r)] + [('C', p) for p in range(r)]
        events.append({'action': 'add', 'r': r, 'var': 'C', 'deps': deps_C, 'title': f'Traduccion Recursiva C_{r}'})
        
    # 5. Coeficientes Zernike A (Sustitucion hacia atras)
    events.append({'action': 'add', 'r': L-1, 'var': 'A', 'deps': [('B', L-1)], 'title': f'Coef. ISO A_{L-1}'})
    for r in range(L-2, -1, -1):
        deps_A = [('B', r)] + [('C', i) for i in range(r+1, L)]
        events.append({'action': 'add', 'r': r, 'var': 'A', 'deps': deps_A, 'title': f'Coef. ISO A_{r}'})
        
    return events


def graficar_flujo_zernike(resultados, intervalo_ms=180, repetir=True):
    """
    Animacion de superposicion de capas de color.
    Incluye flechas de saltos hacia atras/adelante apuntando exactamente
    a la variable (capa) de la cual depende.
    """
    L = len(resultados['B'])
    n_fases = len(_VARS)
    capa_h = 1.0

    plt.style.use('default')
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

    ax.scatter(
        X_c[~mascara], Y_c[~mascara],
        c=_COL['U'], s=14, alpha=0.55, linewidths=0,
        label=f'Fuera  ({(~mascara).sum()})',
    )
    ax.scatter(
        X_c[mascara], Y_c[mascara],
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
    ax.legend(fontsize=9, frameon=True)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.25)

    plt.tight_layout()
    return fig
