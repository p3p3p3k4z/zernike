import os
import sys
import argparse
import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Configurar el entorno para importar los modulos del proyecto padre
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from train_srgan import SRGANGenerator
from lib.zernike import polinomios_zernike, ajuste_completo

def preprocess_image(image_path, size=32):
    # La conversion a 'L' garantiza que trabajamos exclusivamente con la matriz de intensidad
    img = Image.open(image_path).convert('L')
    img_np = np.array(img)
    
    # 1. Deteccion de Bounding Box
    # Ignoramos los pixeles muy oscuros (ruido de fondo) para encontrar el interferograma
    umbral = 15
    y_coords, x_coords = np.where(img_np > umbral)
    
    if len(x_coords) == 0 or len(y_coords) == 0:
        # Fallback de seguridad por si la imagen es completamente negra
        left, top, right, bottom = 0, 0, img.width, img.height
    else:
        # Extremos del contenido real
        min_x, max_x = x_coords.min(), x_coords.max()
        min_y, max_y = y_coords.min(), y_coords.max()
        
        # 2. Forzamos un Cuadrado Perfecto
        # Para no distorsionar el circulo en una elipse, usamos la dimension mayor
        ancho_detectado = max_x - min_x
        alto_detectado = max_y - min_y
        lado_cuadrado = max(ancho_detectado, alto_detectado)
        
        # Encontramos el centro del contenido
        centro_x = (min_x + max_x) // 2
        centro_y = (min_y + max_y) // 2
        
        # Calculamos los margenes ideales
        left = centro_x - (lado_cuadrado // 2)
        top = centro_y - (lado_cuadrado // 2)
        right = left + lado_cuadrado
        bottom = top + lado_cuadrado

    # Pillow automaticamente rellena con negro si los margenes salen de los limites de la foto original
    img_cropped = img.crop((left, top, right, bottom))
    
    # La interpolacion LANCZOS minimiza los artefactos de aliasing al reducir drasticamente la resolucion
    img_resized = img_cropped.resize((size, size), Image.Resampling.LANCZOS)
    
    # Transformamos el espacio de color [0, 255] al dominio matematico [-1, 1] 
    # requerido por la arquitectura de la red generativa
    img_array = np.array(img_resized, dtype=np.float32)
    img_array = (img_array / 255.0) * 2 - 1
    
    tensor = torch.tensor(img_array).unsqueeze(0).unsqueeze(0)
    return tensor, img_cropped

def postprocess_array(img_array):
    # Proyecta datos del dominio matematico [-1, 1] al estandar visual de 8 bits [0, 255]
    img_array = np.clip(img_array, -1, 1)
    img_array = ((img_array + 1) / 2.0) * 255.0
    return img_array.astype(np.uint8)

def apply_zernike_correction(sr_array):
    # Genera la malla espacial normalizada para la reconstruccion polinomial
    res = sr_array.shape[0]
    x, y = np.meshgrid(np.linspace(-1, 1, res), np.linspace(-1, 1, res))
    x_flat, y_flat = x.flatten(), y.flatten()
    
    # El ajuste de Zernike es fisicamente valido unicamente dentro de la pupila circular
    mask = (x_flat**2 + y_flat**2) <= 1.0
    X_valid = x_flat[mask]
    Y_valid = y_flat[mask]
    W_valid = sr_array.flatten()[mask]
    
    # Ajuste por minimos cuadrados (Gram-Schmidt) para extraer la superficie libre de ruido
    polinomios = polinomios_zernike()
    resultados = ajuste_completo(X_valid, Y_valid, W_valid, polinomios, k=5)
    W_fit_valid = resultados.W_fit
    
    # Reconstruccion del mapa bidimensional aplicando cero fuera del area pupilar
    W_fit_2d = np.zeros(res * res)
    W_fit_2d[mask] = W_fit_valid
    
    return W_fit_2d.reshape((res, res))

def main():
    parser = argparse.ArgumentParser(description="Inferencia SR-GAN y reconstruccion Zernike")
    parser.add_argument("imagen", type=str, help="Ruta de la imagen original a procesar")
    parser.add_argument("--weights", type=str, default=os.path.join(os.path.dirname(__file__), 'generator_epoch_100.pth'), help="Ruta al modelo entrenado")
    parser.add_argument("--preprocess-only", action="store_true", help="Solo recortar y visualizar la imagen sin cargar la red neuronal")
    args = parser.parse_args()

    if not os.path.exists(args.imagen):
        print(f"Error: No se encontro el archivo '{args.imagen}'.")
        return

    if args.preprocess_only:
        print(f"Modo preprocesamiento activado para: {args.imagen}")
        tensor, original_cropped = preprocess_image(args.imagen)
        
        out_dir = os.path.join(os.path.dirname(__file__), "resultados_sr")
        os.makedirs(out_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(args.imagen))[0]
        out_path = os.path.join(out_dir, f"{base_name}_solo_recorte.png")
        original_cropped.save(out_path)
        print(f"Recorte inteligente completado y guardado en:\n  -> {out_path}")
        print(f"Dimensiones del recorte: {original_cropped.size[0]}x{original_cropped.size[1]}")
        
        plt.imshow(original_cropped, cmap='gray')
        plt.title(f"Recorte Bounding Box ({original_cropped.size[0]}px)")
        plt.axis('off')
        plt.show()
        return

    if not os.path.exists(args.weights):
        print(f"Error: El modelo '{args.weights}' no existe.")
        print("Asegurate de generar los pesos ejecutando primero el script de entrenamiento.")
        return

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Acelerador de hardware detectado: {device}")
    
    # --- 1. Generacion SR-GAN ---
    model = SRGANGenerator().to(device)
    model.load_state_dict(torch.load(args.weights, map_location=device))
    model.eval()
    
    tensor, original_cropped = preprocess_image(args.imagen)
    tensor = tensor.to(device)
    
    with torch.no_grad():
        output_tensor = model(tensor)
        
    sr_array = output_tensor.squeeze().detach().cpu().numpy()
    
    # --- 2. Correccion Zernike ---
    # Procesamos la salida de alta resolucion para generar un modelo matematico idealizado
    zernike_array = apply_zernike_correction(sr_array)
    
    # --- 3. Postprocesamiento Visual ---
    sr_img_gray = postprocess_array(sr_array)
    zernike_img_gray = postprocess_array(zernike_array)
    
    # Sintetizamos los canales verdes mapeando la intensidad en el eje G de RGB
    zeros = np.zeros_like(sr_img_gray)
    sr_img_color = np.stack([zeros, sr_img_gray, zeros], axis=2)
    zernike_img_color = np.stack([zeros, zernike_img_gray, zeros], axis=2)
    
    # Estructura de directorios para salvaguardar los artefactos
    base_dir = os.path.dirname(__file__)
    out_dir_sr = os.path.join(base_dir, "resultados_sr", "aberracion_alta_res")
    out_dir_zernike = os.path.join(base_dir, "resultados_sr", "corregida_zernike")
    os.makedirs(out_dir_sr, exist_ok=True)
    os.makedirs(out_dir_zernike, exist_ok=True)
    
    filename = os.path.basename(args.imagen)
    base_name = os.path.splitext(filename)[0]
    
    Image.fromarray(sr_img_gray, mode='L').save(os.path.join(out_dir_sr, f"{base_name}_sr.png"))
    Image.fromarray(sr_img_color, mode='RGB').save(os.path.join(out_dir_sr, f"{base_name}_sr_verde.png"))
    Image.fromarray(zernike_img_gray, mode='L').save(os.path.join(out_dir_zernike, f"{base_name}_zernike.png"))
    Image.fromarray(zernike_img_color, mode='RGB').save(os.path.join(out_dir_zernike, f"{base_name}_zernike_verde.png"))
    print("Mapeo de superficies completado exitosamente.")

    # Despliegue interactivo de la comparativa
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    
    axes[0].imshow(original_cropped, cmap='gray')
    axes[0].set_title(f"Recorte Original ({original_cropped.size[0]}px)")
    axes[0].axis('off')

    axes[1].imshow(sr_img_gray, cmap='gray')
    axes[1].set_title("SR-GAN Aberracion (128px)")
    axes[1].axis('off')

    axes[2].imshow(zernike_img_gray, cmap='gray')
    axes[2].set_title("Zernike Corregida (128px)")
    axes[2].axis('off')

    axes[3].imshow(zernike_img_color)
    axes[3].set_title("Zernike Corregida Verde")
    axes[3].axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
