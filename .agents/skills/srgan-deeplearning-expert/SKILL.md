---
name: srgan-deeplearning-expert
description: Agente Especialista en Deep Learning & SR-GAN para auditar, entrenar e iterar redes neuronales generativas de super-resolución de frentes de onda en PyTorch.
---

# Skill: Agente Especialista en Deep Learning & SR-GAN (SR-GAN Expert)

Este skill se enfoca en el desarrollo, entrenamiento, evaluación e inferencia de modelos de aprendizaje profundo dentro de la carpeta `SRGAN/`.

## Áreas de Especialización

1. **Generación de Datasets Sintéticos (`train_srgan.py`)**:
   - Construcción de pares de datos en `WavefrontDataset` pasando combinaciones aleatorias de Polinomios de Zernike en baja resolución ($32 \times 32$ px) y alta resolución ($128 \times 128$ px).
   - Inyección de ruido gaussiano para simular sensores CCD degradados.

2. **Arquitectura Convolucional Residual (`SRGANGenerator` & `SRGANDiscriminator`)**:
   - Diseño e inspección de bloques residuales con activaciones `PReLU` y `BatchNorm2d`.
   - Función de pérdida adversaria (Adversarial Loss + Perceptual Content Loss).

3. **Inferencia y Postprocesamiento (`inference.py`)**:
   - Escalamiento de imágenes mediante la red entrenada (`generator_epoch_100.pth`).
   - Aplicación de corrección polinomial de Zernike sobre la matriz de alta resolución resultante.
