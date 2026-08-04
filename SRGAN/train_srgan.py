import os
import sys
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam

# Permitir la importacion del motor matematico nativo del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lib.zernike import polinomios_zernike, evaluar_polinomios, reconstruir_W

def generate_wavefront(coeffs, num_points=32):
    # Generamos la grilla espacial donde se evaluaran los polinomios
    x, y = np.meshgrid(np.linspace(-1, 1, num_points), np.linspace(-1, 1, num_points))
    x_flat, y_flat = x.flatten(), y.flatten()
    
    # Extraemos la base de polinomios y construimos la matriz de diseno U
    polinomios = polinomios_zernike()
    U = evaluar_polinomios(x_flat, y_flat, polinomios)
    
    # El modelo recibe 15 coeficientes, pero la libreria requiere 21 (grado 5)
    # Rellenamos los restantes con ceros para mantener compatibilidad
    A = np.zeros(21)
    A[:len(coeffs)] = coeffs
    
    # Reconstruimos la superficie evaluando la combinacion lineal
    values_flat = reconstruir_W(A, U)
    values = values_flat.reshape((num_points, num_points))
    
    # Mascaramos fuera del circulo unitario simulando la pupila optica
    radius = np.sqrt(x**2 + y**2)
    values[radius > 1] = 0.0

    # Escalar entre -1 y 1 es un requisito estandar para las redes GAN
    # ya que la capa final del generador utiliza una activacion Tanh
    val_min, val_max = np.nanmin(values), np.nanmax(values)
    if val_max != val_min:
        values = (values - val_min) / (val_max - val_min)
        values = 2 * values - 1
    else:
        values = np.zeros_like(values)

    return values

class WavefrontDataset(Dataset):
    def __init__(self, num_samples=1000, low_res=32, high_res=128, noise_level=0.01):
        self.num_samples = num_samples
        self.low_res = low_res
        self.high_res = high_res
        self.noise_level = noise_level

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        # Seleccion aleatoria de coeficientes de aberracion (modos 1 al 15)
        coeffs = np.random.uniform(-1, 1, size=15)

        # Mapeo de la superficie idealizada que servira como etiqueta perfecta (Ground Truth)
        high_res_map = generate_wavefront(coeffs, num_points=self.high_res)

        # Mapeo en baja resolucion al que inyectamos ruido gaussiano
        # Simula un interferograma crudo capturado por un sensor defectuoso o limitado
        low_res_map = generate_wavefront(coeffs, num_points=self.low_res)
        low_res_map += np.random.normal(0, self.noise_level, low_res_map.shape)

        return torch.tensor(low_res_map, dtype=torch.float32), torch.tensor(high_res_map, dtype=torch.float32)

class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super(ResidualBlock, self).__init__()
        # Un bloque residual permite entrenar redes mas profundas al aprender 
        # perturbaciones sobre la identidad en lugar de funciones completas
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
            nn.PReLU(),
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels)
        )

    def forward(self, x):
        # Aqui ocurre la magia residual: sumamos la entrada a la salida de la sub-red
        return x + self.block(x)

class SRGANGenerator(nn.Module):
    def __init__(self):
        super(SRGANGenerator, self).__init__()

        # Extractor de caracteristicas incial usando un kernel grande para
        # capturar patrones globales de interferencia desde la entrada de baja resolucion
        self.initial = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=9, stride=1, padding=4),
            nn.PReLU()
        )

        # 16 bloques consecutivos que refinan la informacion espacial y extraen 
        # caracteristicas complejas sin perder la topologia original (gracias al salto residual)
        self.residual_blocks = nn.Sequential(
            *[ResidualBlock(64) for _ in range(16)]
        )

        self.post_residual = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64)
        )

        # Fases de superresolucion sub-pixel. 
        # Cada sub-red duplica el tamano espacial usando convoluciones transpuestas
        # Pasando de 32x32 -> 64x64 -> 128x128
        self.upsample = nn.Sequential(
            nn.ConvTranspose2d(64, 64, kernel_size=4, stride=2, padding=1),
            nn.PReLU(),
            nn.ConvTranspose2d(64, 64, kernel_size=4, stride=2, padding=1),
            nn.PReLU()
        )

        # Fusion final en un solo canal garantizando salida en el dominio [-1, 1]
        self.final = nn.Sequential(
            nn.Conv2d(64, 1, kernel_size=9, stride=1, padding=4),
            nn.Tanh()
        )

    def forward(self, x):
        initial_features = self.initial(x)
        residual_output = self.residual_blocks(initial_features)
        post_residual = self.post_residual(residual_output)
        
        # El salto global preserva la topologia de baja frecuencia 
        # mientras los bloques residuales solo anaden los detalles de alta frecuencia
        combined = initial_features + post_residual
        
        upsampled = self.upsample(combined)
        output = self.final(upsampled)
        return output

class Discriminator(nn.Module):
    def __init__(self, high_res):
        super().__init__()
        # Red convolucional que actua como "critico de arte" determinando
        # si una imagen de 128x128 es generada sinteticamente o es matematicamente perfecta
        self.model = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Flatten(),
            nn.Linear(128 * (high_res // 2) * (high_res // 2), 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

def initialize_weights(model):
    for m in model.modules():
        if isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d):
            # Inicializacion recomendada para redes profundas con ReLU
            nn.init.kaiming_normal_(m.weight, nonlinearity='relu')
        elif isinstance(m, nn.BatchNorm2d):
            nn.init.constant_(m.weight, 1)
            nn.init.constant_(m.bias, 0)

def train_model(epochs=100, batch_size=64, num_samples=1000):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Dispositivo de hardware seleccionado:', device)

    dataset = WavefrontDataset(num_samples=num_samples)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    lr_generator = 2e-4
    lr_discriminator = 1e-5
    lambda_L1 = 100

    generator = SRGANGenerator().to(device)
    initialize_weights(generator)

    discriminator = Discriminator(high_res=128).to(device)
    initialize_weights(discriminator)

    # El generador compite contra el discriminador para mejorar su falsificacion
    gen_opt = Adam(generator.parameters(), lr=lr_generator)
    disc_opt = Adam(discriminator.parameters(), lr=lr_discriminator)
    
    # BCE penaliza clasificaciones falsas y MSE garantiza fidelidad pixel por pixel
    adversarial_loss = nn.BCELoss()
    pixel_loss = nn.MSELoss()

    generator.train()
    print(f"Iniciando el entrenamiento por {epochs} epocas...")

    for epoch in range(epochs):
        for i, (low_res, high_res) in enumerate(dataloader):
            low_res, high_res = low_res.to(device), high_res.to(device)

            # --- 1. Entrenamiento del Critico (Discriminador) ---
            disc_opt.zero_grad()
            fake_high_res = generator(low_res.unsqueeze(1))
            
            real_label = torch.ones((high_res.size(0), 1), device=device)
            fake_label = torch.zeros((high_res.size(0), 1), device=device)
            
            # Penalizamos la incapacidad de distinguir la verdad de la creacion
            real_loss = adversarial_loss(discriminator(high_res.unsqueeze(1)), real_label)
            fake_loss = adversarial_loss(discriminator(fake_high_res.detach()), fake_label)
            disc_loss = (real_loss + fake_loss) / 2
            
            disc_loss.backward()
            disc_opt.step()

            # --- 2. Entrenamiento del Creador (Generador) ---
            gen_opt.zero_grad()
            
            # Se castiga al generador si el discriminador detecta que la imagen no es real (adv_loss)
            adv_loss = adversarial_loss(discriminator(fake_high_res), real_label)
            # Y se castiga fuertemente si no respeta la forma del interferograma original (pix_loss)
            pix_loss = pixel_loss(fake_high_res, high_res.unsqueeze(1)) * lambda_L1
            
            gen_loss = adv_loss + pix_loss
            gen_loss.backward()
            gen_opt.step()

        # Reporte de progreso al final de la epoca
        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"Progreso [{epoch+1}/{epochs}] - Error Generador: {gen_loss:.4f}, Error Discriminador: {disc_loss:.4f}")

    # Guardamos el conocimiento aprendido para usarlo luego
    save_dir = os.path.dirname(os.path.abspath(__file__))
    gen_path = os.path.join(save_dir, 'generator_epoch_100.pth')
    disc_path = os.path.join(save_dir, 'discriminator_epoch_100.pth')
    torch.save(generator.state_dict(), gen_path)
    torch.save(discriminator.state_dict(), disc_path)
    print(f"Pesos guardados exitosamente en:\n  -> {gen_path}\n  -> {disc_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrenamiento del modelo SR-GAN")
    parser.add_argument("--epochs", type=int, default=100, help="Numero de veces que se repetira el entrenamiento (epocas)")
    args = parser.parse_args()
    
    train_model(epochs=args.epochs)
