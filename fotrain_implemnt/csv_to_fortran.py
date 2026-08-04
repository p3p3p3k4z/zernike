import os
import sys
import glob

def select_csv_file():
    # Encontrar todos los csv en la carpeta actual y la carpeta padre
    csv_files = glob.glob('*.csv') + glob.glob('../*.csv')
    
    # Remover duplicados y resolver rutas
    csv_files = list(set([os.path.normpath(f) for f in csv_files]))
    
    if not csv_files:
        print("No se encontraron archivos CSV en este directorio o en el directorio padre.")
        sys.exit(1)
        
    print("Selecciona un archivo CSV para transformar:")
    for i, f in enumerate(csv_files):
        print(f"[{i+1}] {f}")
        
    while True:
        try:
            choice = int(input(f"Ingresa el número (1-{len(csv_files)}): "))
            if 1 <= choice <= len(csv_files):
                return csv_files[choice-1]
            else:
                print("Selección inválida.")
        except ValueError:
            print("Por favor ingresa un número válido.")

def main():
    # Si se pasa un argumento, usarlo; si no, mostrar menú interactivo
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
    else:
        input_csv = select_csv_file()
        
    if not os.path.exists(input_csv):
        print(f"El archivo {input_csv} no existe.")
        sys.exit(1)
        
    output_dat = "datos_entrada.dat"
    
    try:
        count = 0
        with open(input_csv, 'r') as infile, open(output_dat, 'w') as outfile:
            lines = infile.readlines()
            
            # Asumimos que la primer linea es header si contiene caracteres alfanuméricos
            start_idx = 1 if 'X' in lines[0].upper() or 'Y' in lines[0].upper() else 0
            
            for line in lines[start_idx:]:
                line = line.strip()
                if not line:
                    continue
                
                # Soportar CSV separado por comas
                parts = line.split(',')
                if len(parts) >= 3:
                    # Escribir X Y Z separados por espacio
                    outfile.write(f"{parts[0].strip()} {parts[1].strip()} {parts[2].strip()}\n")
                    count += 1
            
            # Añadir el centinela que espera el Fortran
            outfile.write("10000.0 0.0 0.0\n")
            
        print(f"¡Éxito! Se procesaron {count} puntos de datos del archivo {input_csv}.")
        print(f"Archivo generado y guardado como: {output_dat}")
        print("Ahora puedes ejecutar el programa Fortran e ingresar 'datos_entrada.dat'")
        
    except Exception as e:
        print(f"Error procesando el archivo: {e}")

if __name__ == "__main__":
    main()
