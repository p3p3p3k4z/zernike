# Cómo Funciona la Simulación de Datos Ópticos (CCD)

Para entender cómo la computadora genera los puntos 3D (las coordenadas $X$, $Y$ y $Z$) sin enredarnos en lenguajes de programación, vamos a pensar en **la cámara de tu teléfono celular**.

**La Analogía:** 
Imagina que el sensor que está dentro de tu teléfono es un papel cuadriculado rectangular (donde cada cuadrito es un pixel). Arriba de ese papel, hay un tubo redondo (la lente de la cámara). Cuando tomas una foto, la luz pasa por el tubo redondo y dibuja un círculo iluminado sobre tu papel cuadriculado. Como el papel es cuadrado y la luz es redonda, las esquinas del papel siempre quedan a oscuras.

Nuestro sistema simula exactamente ese mismo fenómeno físico en tres pasos muy simples:

---

## 1. El Papel Cuadriculado (La Cuadrícula Inicial)
Todo empieza creando el "papel" donde va a caer la luz. Si tú dices que quieres una resolución de 20x20, el sistema dibuja una cuadrícula con 400 cuadritos. 

Pero para poder hacer matemáticas, necesitamos saber exactamente **dónde está el centro del papel**.
El algoritmo calcula el punto medio exacto de la cuadrícula y lo bautiza como el origen $(0,0)$. 
A partir de ahí, numera los cuadritos hacia la izquierda, derecha, arriba y abajo. La distancia entre un cuadrito y su vecino es siempre exactamente igual a 1. 

Con esto, ya tenemos nuestro papel cuadriculado construido y perfectamente centrado.

---

## 2. El Tubo Redondo (El Recorte de la Lente)
Ahora tenemos nuestro papel cuadrado, pero recuerda que el tubo de la lente de la cámara es redondo.

Tú le dices al programa: *"Mi lente tiene un diámetro de 10"*. 
El algoritmo saca su compás imaginario, pone la punta en el centro $(0,0)$ de tu papel y dibuja un círculo con ese tamaño. 
Como si fuera con unas tijeras, el sistema recorta el papel siguiendo esa línea redonda. Todos los cuadritos de las esquinas (los que se quedaron a oscuras) se tiran a la basura, y nos quedamos solo con los cuadritos que sí se iluminaron.

---

## 3. La Regla Universal (El Círculo de Zernike)
Llegamos al paso final. Las fórmulas ópticas que inventó Zernike son universales, pero tienen una regla de oro estricta: **el análisis solo funciona dentro de un círculo matemático cuyo borde valga exactamente 1**. A esta regla no le importa si tu lente medía centímetros, metros o kilómetros en la vida real.

Para obedecer esta ley matemática, el programa toma el círculo de papel que recortamos en el paso anterior y lo "encoge" (divide sus medidas entre el tamaño original del radio) para que encaje perfectamente en un molde universal donde el borde es siempre igual a $1$.

Es justo encima de este círculo "estándar y universal" donde el programa calcula la altura de tu ecuación de luz (la coordenada $Z$). Al hacer esto, garantizamos que tus mediciones sean totalmente puras, correctas y nunca se vean afectadas por los megapíxeles o la resolución inicial de tu cámara.
