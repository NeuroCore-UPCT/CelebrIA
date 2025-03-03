# CelebIA

CelebIA es una aplicación interactiva que utiliza inteligencia artificial para analizar rostros en tiempo real y encontrar los tres famosos a los que más te pareces. Este proyecto ha sido desarrollado por la **Asociación de Estudiantes de IA de la UPCT** para el evento del **Día de las Paellas** de nuestra universidad.

## 📸 Características
- Captura de imagen a través de una webcam con un solo toque.
- Comparación facial basada en inteligencia artificial.
- Identificación de los tres famosos más similares utilizando una base de datos propia.
- Ejecución en local sin necesidad de conexión a internet.

## 🛠 Tecnologías Utilizadas
- **Lenguaje:** Python
- **Backend:** [DeepFace](https://github.com/serengil/deepface) para el análisis facial
- **Modelo de IA:** FaceNet para la extracción de embeddings faciales
- **Base de Datos:** Conjunto propio de imágenes de famosos

## ⚙️ Cómo Funciona
1. El usuario presiona el botón táctil para tomar una foto con la webcam.
2. La imagen capturada se procesa y se extraen sus embeddings faciales con **FaceNet**.
3. Se comparan los embeddings con la base de datos de famosos mediante diferencia euclidiana.
4. Se seleccionan y muestran en pantalla los tres famosos con menor diferencia.

## 🚀 Instalación y Ejecución
### 1️⃣ Prerrequisitos
Asegúrate de tener **Python 3.8+** instalado junto con las siguientes dependencias:
```sh
pip install deepface opencv-python numpy
```

### 2️⃣ Ejecución
Clona este repositorio y ejecuta el script principal:
```sh
git clone https://github.com/ivan-rf22/Actividad_Paelllas.git
cd CelebIA
python main.py
```

## 🎓 Créditos
Este proyecto ha sido desarrollado por la **Asociación de Estudiantes de IA de la UPCT**.