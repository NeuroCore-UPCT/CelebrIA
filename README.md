# CelebrIA 

## Instalación y Uso

1. Instala las dependencias:
```
pip install -r requirements.txt
```

2. Ejecuta la aplicación:
```
python app.py
```

3. Abre tu navegador y ve a `http://localhost:5000`

## Cómo usar la aplicación

1. Haz clic en el botón "CAPTURAR" para tomar una foto con tu webcam.
2. Espera mientras la aplicación procesa la imagen y encuentra coincidencias.
3. Verás los resultados con los famosos a los que más te pareces.
4. Si se detectan múltiples caras en la imagen, puedes navegar entre ellas usando las flechas izquierda y derecha.
5. Para tomar otra foto, haz clic en el botón "TOMAR OTRA FOTO" en la parte inferior de la página de resultados.

### 📦 Descarga de Base de Datos de Famosos  
Para que la aplicación funcione correctamente, necesitas descargar el archivo con los embeddings faciales:  
🔗 [Enlace a la base de datos (Google Drive)](https://drive.google.com/file/d/1Pieb7qwPpTpMDkPGplzYEQEzr0CqXQTC/view?usp=sharing)  

Una vez descargado, guárdalo como `representations.pkl` en el directorio raíz del proyecto.

