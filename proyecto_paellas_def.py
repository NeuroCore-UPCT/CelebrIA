from deepface import DeepFace
import numpy as np
from PIL import Image
import pandas as pd
import json
import cv2
import os
import shutil
import tkinter as tk

def detectar_personas(ruta_front):
    """
    Detecta las caras en una imagen y guarda cada cara detectada como una imagen separada.
    
    :param ruta_front: Ruta de la imagen donde se detectarán las caras.
    :return: Lista de rutas de las imágenes de las caras detectadas.
    """
    faces = DeepFace.extract_faces(ruta_front)  # Extraer caras de la imagen
    lista_rutas = []
    for i in range(len(faces)):
        face_array = faces[i]['face']  # Obtener el array de la cara detectada
        face_array = (face_array * 255).astype(np.uint8)  # Convertir a formato de imagen
        face_image = Image.fromarray(face_array)  # Convertir el array en una imagen PIL
        face_image.save(f"personas/foto{i}.jpg")  # Guardar la imagen
        lista_rutas.append(f"personas/foto{i}.jpg")  # Añadir la ruta a la lista

    return lista_rutas

def hacer_json(lista_personas, n, lista_ruta_famosos, lista_nombre_famosos, lista_parecidos):
    """
    Crea un archivo JSON con la información de las personas detectadas y sus coincidencias.
    
    :param lista_personas: Lista de rutas de las imágenes de las personas detectadas.
    :param n: Índice de la persona actual en la lista.
    :param lista_ruta_famosos: Lista de rutas de las imágenes de los famosos parecidos.
    :param lista_nombre_famosos: Lista de nombres de los famosos parecidos.
    :param lista_parecidos: Lista de porcentajes de similitud con los famosos.
    """
    if len(lista_personas) > 1:
        data = {
            "n_personas": len(lista_personas),  # Número de personas detectadas
            "persona": lista_personas[n],  # Ruta de la imagen de la persona actual
            "matches": []
        }
    elif len(lista_personas) == 1:
        data = {
            "n_personas": len(lista_personas),  # Número de personas detectadas
            "persona": "personas/foto.jpg",  # Ruta de la imagen de la persona
            "matches": []
        }
    for i in range(len(lista_nombre_famosos)):
        data["matches"].append({
                "name": lista_nombre_famosos[i],  # Nombre del famoso parecido
                "similarity": lista_parecidos[i],  # Porcentaje de similitud
                "image_data": lista_ruta_famosos[i]  # Ruta de la imagen del famoso
            })

    # Convertir el diccionario a formato JSON
    json_data = json.dumps(data, indent=4)

    # Escribir el JSON en un archivo
    with open(f"personas/json_persona{n+1}.json", "w") as json_file:
        json_file.write(json_data)

def sacar_nombre_ruta(lista_nombres):
    """
    Extrae los nombres de las rutas de las imágenes de los famosos.
    
    :param lista_nombres: Lista de rutas de las imágenes de los famosos.
    :return: Lista de nombres de los famosos.
    """
    nombres = []
    for i in range(len(lista_nombres)):
        cadena = lista_nombres[i]
        if cadena[8] == "@":
            nombre = cadena.split('/')[1].replace('.jpg', '')  # Extraer nombre si la ruta contiene '@'
        else:    
            nombre = cadena.split('/')[1].split('.')[0].replace('_', ' ')  # Extraer nombre y reemplazar '_' con espacios
        nombres.append(nombre)
    return nombres

def encontrar_3_mas_parecidos(ruta):
    """
    Encuentra las 3 imágenes más parecidas en la base de datos de caras.
    
    :param ruta: Ruta de la imagen de la persona a comparar.
    :return: Lista de rutas de las imágenes más parecidas y sus porcentajes de similitud.
    """
    search = DeepFace.find(img_path=ruta, db_path="face-db/", model_name="VGG-Face")  # Buscar coincidencias
    df = pd.concat(search, ignore_index=True) if search else pd.DataFrame()  # Crear un DataFrame con los resultados
    df_sorted = df.sort_values(by="distance", ascending=True)  # Ordenar por similitud (menor distancia primero)
    rutas_imagen = list(df_sorted['identity'][:3])  # Obtener las 3 rutas más parecidas
    porcentage_parecidos = list(round(((1 - df_sorted['distance'][:3]) * 100), 2))  # Calcular porcentajes de similitud
    return rutas_imagen, porcentage_parecidos

def capture_image(event, x, y, flags, param):
    global cap, original_path
    if event == cv2.EVENT_LBUTTONDOWN:
        ret, frame = cap.read()
        if ret:
            original_path = "personas/foto.jpg"
            cv2.imwrite(original_path, frame)
            print(f"✅ Imagen guardada en: {original_path}")
            cv2.destroyAllWindows()
            cap.release()
            procesar_imagen(original_path)

def procesar_imagen(original_path):
    lista_personas = detectar_personas(original_path)
    for i in range(len(lista_personas)):
        lista_ruta_famosos, lista_parecidos = encontrar_3_mas_parecidos(lista_personas[i])
        lista_nombre_famosos = sacar_nombre_ruta(lista_ruta_famosos)
        hacer_json(lista_personas, i, lista_ruta_famosos, lista_nombre_famosos, lista_parecidos)

def borrar_contenido_carpeta(carpeta):
    def borrar_archivos():
        """Función para borrar los archivos de la carpeta cuando se haga clic en el cuadrado"""
        if os.path.exists(carpeta) and os.path.isdir(carpeta):
            for archivo in os.listdir(carpeta):
                archivo_path = os.path.join(carpeta, archivo)
                try:
                    if os.path.isdir(archivo_path):
                        shutil.rmtree(archivo_path)  # Borrar subcarpeta
                    else:
                        os.remove(archivo_path)  # Borrar archivo
                except Exception as e:
                    print(f"No se pudo borrar {archivo_path}: {e}")
            print(f"Contenido de la carpeta '{carpeta}' ha sido borrado.")
        else:
            print(f"La carpeta {carpeta} no existe o no es una carpeta válida.")
        # Cerrar la ventana después de borrar los archivos
        root.destroy()

    # Crear la ventana
    root = tk.Tk()
    root.title("Borrar contenido de la carpeta")
    root.geometry("300x300")  # Tamaño de la ventana

    # Crear un lienzo donde dibujaremos el cuadrado
    canvas = tk.Canvas(root, width=300, height=300)
    canvas.pack()

    # Dibujar el cuadrado en el lienzo
    square = canvas.create_rectangle(100, 100, 200, 200, fill="blue", outline="black")

    # Función que se llama cuando se hace clic en el cuadrado
    def on_square_click(event):
        # Verificar si el clic fue dentro del cuadrado
        if 100 < event.x < 200 and 100 < event.y < 200:
            borrar_archivos()

    # Asociar la acción de hacer clic al cuadrado
    canvas.bind("<Button-1>", on_square_click)

    # Iniciar la interfaz gráfica
    root.mainloop()

def main():
    """
    Función principal que captura una imagen desde la webcam, detecta caras y genera archivos JSON con las coincidencias.
    """
    global cap
    cap = cv2.VideoCapture(0)  # Iniciar la captura de la webcam
    if not cap.isOpened():
        print("❌ Error accessing the webcam")
        return
    
    print("📸 Haz clic izquierdo para capturar la imagen...")
    cv2.namedWindow("Webcam - Haz clic para capturar")
    cv2.setMouseCallback("Webcam - Haz clic para capturar", capture_image)

    while cap.isOpened():
        ret, frame = cap.read()  # Leer un frame de la webcam
        if not ret:
            print("❌ Failed to capture image")
            break
        cv2.imshow("Webcam - Haz clic para capturar", frame)  # Mostrar el frame en una ventana
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # Si se presiona raton
            cv2.imwrite("personas/foto.jpg", frame)  # Guardar la imagen capturada
            cap.release()  # Liberar la webcam
            cv2.destroyAllWindows()  # Cerrar la ventana
            break

    cap.release()
    cv2.destroyAllWindows()

    lista_personas = detectar_personas("personas/foto.jpg")  # Detectar caras en la imagen capturada
    for i in range(len(lista_personas)):
        lista_ruta_famosos, lista_parecidos = encontrar_3_mas_parecidos(lista_personas[i])  # Encontrar coincidencias
        lista_nombre_famosos = sacar_nombre_ruta(lista_ruta_famosos)  # Extraer nombres de los famosos
        hacer_json(lista_personas, i, lista_ruta_famosos, lista_nombre_famosos, lista_parecidos)  # Crear JSON

    borrar_contenido_carpeta("personas")  # Borrar las imágenes de la carpeta
    
if __name__ == "__main__":
    main()  # Ejecutar la función principal
