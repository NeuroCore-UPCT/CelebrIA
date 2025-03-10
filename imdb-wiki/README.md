# Buscador de Celebridades Similares 🌟

Este proyecto te permite encontrar celebridades que se parecen a ti utilizando reconocimiento facial y aprendizaje profundo.

## Requisitos Previos 📋

- Python 3.8 o superior
- Webcam (opcional, puedes usar fotos existentes)
- Aproximadamente 10GB de espacio libre en disco

## Configuración del Entorno Virtual 🛠️

1. Crear un entorno virtual:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Descarga de Datos Necesarios 📥

1. Descargar el archivo de embeddings (representaciones faciales):
   - Enlace: https://drive.google.com/file/d/1-iSebNCzniQ09pmz5vjrvedIBy-LBEs6/view?usp=sharing
   - Guardar como `representations.pkl` en el directorio del proyecto

2. Descargar el dataset IMDB-WIKI (versión "faces only"):
   - Visitar: https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/
   - Descargar "faces only" (aproximadamente 7GB)
   - Extraer en una carpeta llamada `imdb_data_set`

## Uso del Programa 🚀

### Modo Básico (usando webcam):
```bash
python celebrity2.py
```

### Opciones Disponibles:
```bash
python celebrity2.py --help

Argumentos:
  --pkl_path RUTA     Ruta al archivo de embeddings (default: representations.pkl)
  --imdb_path RUTA    Ruta al directorio de imágenes IMDB (default: imdb_data_set)
  --photo RUTA        Ruta a una foto existente (si no se usa webcam)
  --webcam           Usar webcam para capturar foto
  --matches NÚMERO    Número de celebridades a mostrar (default: 3)
  --gender GÉNERO     Filtrar por género (0/f/female o 1/m/male)
```

### Ejemplos de Uso:

1. Usar webcam y mostrar 5 coincidencias:
```bash
python celebrity2.py --matches 5
```

2. Usar una foto existente:
```bash
python celebrity2.py --photo mi_foto.jpg
```

3. Buscar solo celebridades femeninas:
```bash
python celebrity2.py --gender f
```

## Estructura de Archivos 📁

```
.
├── celebrity2.py          # Script principal
├── requirements.txt       # Dependencias del proyecto
├── representations.pkl    # Archivo de embeddings (descargar separadamente)
└── imdb_data_set/        # Directorio con imágenes de celebridades
```

## Solución de Problemas Comunes ⚠️

1. Error de OpenCV:
   - Asegúrate de tener una webcam conectada
   - Prueba con una foto existente usando --photo

2. Error de memoria:
   - El archivo de embeddings requiere aproximadamente 4GB de RAM
   - Cierra otras aplicaciones que consuman mucha memoria

3. Error al cargar representations.pkl:
   - Verifica que hayas descargado el archivo correcto
   - Asegúrate de que está en el mismo directorio que celebrity2.py

## Notas Importantes 📝

- La primera ejecución puede ser lenta mientras se cargan los modelos
- Las fotos deben tener un rostro claramente visible
- La calidad de las coincidencias depende de la iluminación y el ángulo de la foto
- Los resultados se guardan automáticamente como 'celebrity_lookalikes_result.jpg'

## Créditos 🙏

- Dataset IMDB-WIKI: https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/
- DeepFace framework
- VGGFace model

