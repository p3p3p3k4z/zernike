"""
=============================================================================
FLUJO DE EJECUCIÓN (Fortran vs Python)
=============================================================================
Sigue estos pasos en la terminal para ejecutar todo el flujo de Zernike
y comparar matemáticamente ambos programas:

1. Ejecutar el pipeline de Python (Genera los datos filtrados):
   $ cd ..  (Raíz del proyecto)
   $ python main.py
   (El script exportará output/datos_filtrados_fortran.csv)

2. Convertir los datos a formato Fortran:
   $ cd fotrain_implemnt
   $ python csv_to_fortran.py ../output/datos_filtrados_fortran.csv
   (Se generará el archivo datos_entrada.dat)

3. Ejecutar el binario de Fortran:
   $ ./zernike_app
   (Ingresa 'datos_entrada.dat' cuando lo pregunte. Generará INTER.DAT)

4. Comparar los resultados:
   $ python comparar_resultados.py
   (Verificará que la correlación sea 1.0000)
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    print("Iniciando comparación 1:1 entre Fortran y Python (Malla Filtrada)...")

    # 1. Leer datos de Fortran (INTER.DAT)
    fortran_data = []
    try:
        with open('INTER.DAT', 'r') as f:
            lines = f.readlines()
            for line in lines[2:]:
                parts = line.split()
                if len(parts) == 5:
                    try:
                        fortran_data.append([float(p) for p in parts])
                    except ValueError:
                        pass
    except FileNotFoundError:
        print("Error: No se encontró INTER.DAT.")
        return

    df_fortran = pd.DataFrame(fortran_data, columns=['X_f', 'Y_f', 'W_exp_f', 'W_fit_f', 'Error_f'])
    
    # 2. Leer datos de Python (zernike_resultados.csv)
    try:
        df_python = pd.read_csv('../output/zernike_resultados.csv')
    except FileNotFoundError:
        print("Error: No se encontró ../output/zernike_resultados.csv")
        return

    print(f"Puntos leídos -> Fortran procesó: {len(df_fortran)}, Python procesó: {len(df_python)}")

    if len(df_fortran) != len(df_python):
        print("Aviso: Las cantidades de puntos difieren. Usando los primeros N comunes para comparar.")
    
    N_comun = min(len(df_fortran), len(df_python))
    df_f = df_fortran.head(N_comun).copy()
    df_p = df_python.head(N_comun).copy()

    # 3. Análisis de correlación
    corr_exp = np.corrcoef(df_f['W_exp_f'], df_p['Z_exp'])[0, 1]
    corr_fit = np.corrcoef(df_f['W_fit_f'], df_p['Z_fit'])[0, 1]

    # Factor de escala (la mediana de la relación entre los Z_fit para ver si están a diferente escala)
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = df_f['W_fit_f'] / df_p['Z_fit']
        factor_escala = np.nanmedian(ratio)

    print(f"\n--- Resultados de Correlación (1.0 es igualdad perfecta) ---")
    print(f"Correlación Datos Experimentales (Z Original): {corr_exp:.6f}")
    print(f"Correlación Datos Ajustados (Curva Zernike): {corr_fit:.6f}")
    print(f"Factor de escala (Fortran / Python): {factor_escala:.4f}")

    # 4. Generación de Gráficas
    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    plt.scatter(df_f['W_exp_f'], df_p['Z_exp'], alpha=0.6, color='blue', edgecolor='k')
    plt.title(f'Datos Exp: Fortran vs Python\nCorrelación: {corr_exp:.4f}')
    plt.xlabel('Z Original Fortran (W_exp_f)')
    plt.ylabel('Z Original Python (Z_exp)')
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.subplot(1, 2, 2)
    plt.scatter(df_f['W_fit_f'], df_p['Z_fit'], alpha=0.6, color='red', edgecolor='k')
    plt.title(f'Ajuste Zernike: Fortran vs Python\nCorrelación: {corr_fit:.4f}')
    plt.xlabel('Z Ajustado Fortran (W_fit_f)')
    plt.ylabel('Z Ajustado Python (Z_fit)')
    plt.grid(True, linestyle='--', alpha=0.7)

    if factor_escala > 0 and not np.isnan(factor_escala) and np.isfinite(factor_escala):
        plt.figtext(0.5, 0.01, f"Relación de escala (Fortran / Python): {factor_escala:.4f}", ha="center", fontsize=11, color="black")

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    output_img = 'comparacion_resultados.png'
    plt.savefig(output_img, dpi=300)
    print(f"\nGráfica de análisis generada exitosamente: {output_img}")

if __name__ == '__main__':
    main()
