# IMDB WIKI 16K

### Crear el entorno
```
python -m venv venv
```

### Activar el entorno
```
.\venv\Scripts\activate
```

### Instalación de Dependencias

2. Instalar las dependencias del proyecto:
```bash
pip install -r requirements.txt
```


1. Descargar el archivo de embeddings (representaciones faciales):
   - Enlace: https://drive.google.com/file/d/1-iSebNCzniQ09pmz5vjrvedIBy-LBEs6/view?usp=sharing
   - Guardar como `representations.pkl` en el directorio del proyecto

2. Descargar el dataset IMDB-WIKI (versión "faces only"):
   - Visitar: https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/
   - Descargar "faces only" (aproximadamente 7GB)
   - Extraer en una carpeta llamada `imdb_data_set`

## Uso del Programa 

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

## Estructura de Archivos 

```
.
├── celebrity2.py          # Script principal
├── requirements.txt       # Dependencias del proyecto
├── representations.pkl    # Archivo de embeddings (descargar separadamente)
└── imdb_data_set/        # Directorio con imágenes de celebridades
```




