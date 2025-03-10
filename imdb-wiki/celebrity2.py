import os
import pandas as pd
import numpy as np
import cv2
from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import time
import argparse

# Cargar el dataframe de embeddings de celebridades
def load_embeddings(pkl_path):
    print(f"Loading celebrity embeddings from {pkl_path}...")
    df = pd.read_pickle(pkl_path)
    print(f"Loaded {len(df)} celebrity embeddings")
    return df

# Extraer el vector del objeto de representación de DeepFace
def extract_vector(representation):
    if isinstance(representation, list) and len(representation) > 0:
        return representation[0]['embedding']
    else:
        return representation['embedding']

# Capturar imagen desde la webcam
def capture_image():
    print("Initializing webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise Exception("Could not open webcam. Please check your camera connection.")
    
    # Esperar a que la cámara se inicialice
    time.sleep(1)
    
    print("Press SPACE to capture the photo or ESC to cancel...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            raise Exception("Failed to capture image from webcam")
        
        # Mostrar instrucciones
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "Press SPACE to take photo", (50, 50), font, 1, (0, 255, 0), 2)
        
        # Mostrar el frame
        cv2.imshow("Webcam", frame)
        
        # Comprobar si se ha pulsado una tecla
        key = cv2.waitKey(1) & 0xFF
        
        # Si se pulsa la tecla espacio, tomar la foto
        if key == 32:  # Tecla espacio
            # Mostrar el momento "¡Cheese!"
            cv2.putText(frame, "Cheese!", (50, 100), font, 1, (0, 255, 0), 2)
            cv2.imshow("Webcam", frame)
            cv2.waitKey(500)
            
            # Guardar la imagen temporalmente
            temp_path = "temp_webcam_image.jpg"
            cv2.imwrite(temp_path, frame)
            print(f"Image captured and saved to {temp_path}")
            break
        
        # Si se pulsa la tecla ESC, cancelar
        elif key == 27:  # Tecla ESC
            cap.release()
            cv2.destroyAllWindows()
            raise Exception("Photo capture cancelled by user")
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    
    return temp_path

# Validar y usar una foto existente
def use_existing_photo(photo_path):
    if not os.path.exists(photo_path):
        raise Exception(f"Photo not found at: {photo_path}")
    
    # Leer la imagen para verificar que es válida
    img = cv2.imread(photo_path)
    if img is None:
        raise Exception(f"Could not read image at: {photo_path}. Make sure it's a valid image file.")
    
    print(f"Using existing photo: {photo_path}")
    return photo_path

# Obtener el embedding facial para la imagen
def get_face_embedding(image_path):
    print("Processing face in the image...")
    try:
        embedding = DeepFace.represent(
            img_path=image_path,
            model_name="VGG-Face",
            enforce_detection=False
        )
        return embedding
    except Exception as e:
        raise Exception(f"Error processing face: {str(e)}")

# Encontrar las celebridades más similares
def find_similar_celebrities(user_embedding, celebrity_df, top_n=3, gender=None):
    print("Finding celebrity lookalikes...")
    
    # Extraer el vector del embedding del usuario
    user_vector = extract_vector(user_embedding)
    
    # Filtrar por género si se especifica
    if gender is not None:
        print(f"Filtering by gender: {gender}")
        
        # Imprimir los primeros valores de género para verificar el formato
        print("Sample gender values in dataset:")
        for i in range(min(5, len(celebrity_df))):
            print(f"  Index {i}: {celebrity_df['gender'].iloc[i]}, Type: {type(celebrity_df['gender'].iloc[i])}")
        
        # Convertir valores de género a enteros si están almacenados como arrays/listas
        if isinstance(celebrity_df['gender'].iloc[0], (list, np.ndarray)):
            print("Gender values stored as arrays/lists")
            filtered_df = celebrity_df[celebrity_df['gender'].apply(lambda x: x[0] == gender)]
        else:
            filtered_df = celebrity_df[celebrity_df['gender'] == gender]
            
        if len(filtered_df) == 0:
            print(f"No celebrities found with gender '{gender}'. Using all celebrities.")
            filtered_df = celebrity_df
        else:
            print(f"Found {len(filtered_df)} celebrities with specified gender.")
            
        # Verificar los primeros registros en el conjunto de datos filtrado
        print("First 5 celebrities after filtering:")
        for i in range(min(5, len(filtered_df))):
            idx = filtered_df.index[i]
            gender_val = filtered_df['gender'].iloc[i]
            name = filtered_df['celebrity_name'].iloc[i]
            print(f"  {name}: gender={gender_val}")
    else:
        filtered_df = celebrity_df
    
    # Obtener vectores de todas las celebridades filtradas para comparación
    celebrity_vectors = []
    for idx, row in filtered_df.iterrows():
        raw_vector = row['face_vector_raw']
        if raw_vector is not None:
            celebrity_vectors.append((idx, extract_vector(raw_vector)))
    
    # Calcular similitudes
    similarities = []
    for idx, celeb_vector in celebrity_vectors:
        similarity = cosine_similarity([user_vector], [celeb_vector])[0][0]
        similarities.append((idx, similarity))
    
    # Agrupar por nombre de celebridad y mantener solo la coincidencia de mayor similitud para cada una
    celebrity_matches = {}
    for idx, similarity in similarities:
        celeb_name = filtered_df.loc[idx, 'celebrity_name']
        if celeb_name not in celebrity_matches or similarity > celebrity_matches[celeb_name][1]:
            celebrity_matches[celeb_name] = (idx, similarity)
    
    # Convertir de nuevo a lista y ordenar por similitud (mayor primero)
    unique_similarities = list(celebrity_matches.values())
    unique_similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Obtener las N mejores coincidencias
    top_matches = unique_similarities[:top_n]
    
    # Verificar el género de las coincidencias seleccionadas
    print("\nVerifying gender of top matches:")
    for idx, similarity in top_matches:
        gender_val = celebrity_df.loc[idx, 'gender']
        name = celebrity_df.loc[idx, 'celebrity_name']
        print(f"  {name}: gender={gender_val}, similarity={similarity:.2f}")
    
    return top_matches

# Mostrar los resultados
def display_results(user_image_path, top_matches, celebrity_df, base_path):
    print("Displaying results...")
    
    # Mostrar las mejores coincidencias de celebridades con información de género
    for i, (idx, similarity) in enumerate(top_matches):
        # Obtener información de la celebridad
        celebrity = celebrity_df.loc[idx]
        celebrity_name = celebrity['celebrity_name']
        gender_val = celebrity['gender']
        print(f"Match #{i+1}: {celebrity_name}, Gender: {gender_val}, Similarity: {similarity:.2f}")
    
    # Crear una figura con un diseño de cuadrícula
    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, 4, figure=fig)
    
    # Mostrar la imagen del usuario
    user_img = cv2.imread(user_image_path)
    user_img = cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB)
    ax_user = fig.add_subplot(gs[0, 1:3])
    ax_user.imshow(user_img)
    ax_user.set_title("Your Photo", fontsize=16)
    ax_user.axis('off')
    
    # Mostrar las mejores coincidencias de celebridades
    for i, (idx, similarity) in enumerate(top_matches):
        # Obtener información de la celebridad
        celebrity = celebrity_df.loc[idx]
        celebrity_name = celebrity['celebrity_name']
        celebrity_path = f"{base_path}/{celebrity['full_path'][0]}"
        
        # Crear subgráfico basado en la posición
        if i == 0:
            ax = fig.add_subplot(gs[1, 0:2])
        elif i == 1:
            ax = fig.add_subplot(gs[1, 1:3])
        else:
            ax = fig.add_subplot(gs[1, 2:4])
        
        # Mostrar imagen de la celebridad
        try:
            celeb_img = cv2.imread(celebrity_path)
            celeb_img = cv2.cvtColor(celeb_img, cv2.COLOR_BGR2RGB)
            ax.imshow(celeb_img)
        except Exception as e:
            ax.text(0.5, 0.5, "Image not found", 
                    horizontalalignment='center', verticalalignment='center')
        
        # Añadir leyenda con nombre y puntuación de similitud
        ax.set_title(f"{celebrity_name}\nSimilarity: {similarity:.2f}", fontsize=14)
        ax.axis('off')
    
    # Añadir un título principal
    plt.suptitle("Celebrity Lookalikes", fontsize=20)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    
    # Guardar resultado
    result_path = "celebrity_lookalikes_result.jpg"
    plt.savefig(result_path)
    print(f"Results saved to {result_path}")
    
    # Mostrar el resultado
    plt.show()
    
    return result_path

# Función principal
def find_celebrity_lookalikes(pkl_path, imdb_images_base_path, photo_path=None, use_webcam=True, num_matches=3, gender=None):
    try:
        # Cargar los embeddings de celebridades
        celebrity_df = load_embeddings(pkl_path)
        
        # Preparar los vectores para una comparación más rápida
        print("Preprocessing celebrity embeddings...")
        celebrity_df = celebrity_df.dropna(subset=['face_vector_raw'])
        
        # Obtener la imagen del usuario - ya sea desde la webcam o desde un archivo
        if use_webcam:
            user_image_path = capture_image()
        else:
            if photo_path is None:
                raise Exception("Photo path not provided. Please specify a path to an image file.")
            user_image_path = use_existing_photo(photo_path)
        
        # Obtener el embedding facial para la imagen
        user_embedding = get_face_embedding(user_image_path)
        
        # Encontrar celebridades similares
        top_matches = find_similar_celebrities(user_embedding, celebrity_df, top_n=num_matches, gender=gender)
        
        # Mostrar resultados
        result_path = display_results(user_image_path, top_matches, celebrity_df, imdb_images_base_path)
        
        print("\nDone! Check the matplotlib window for your celebrity lookalikes.")
        print(f"Results saved to {result_path}")
        
        return top_matches, result_path
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None

if __name__ == "__main__":
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Find celebrity lookalikes from a photo")
    
    parser.add_argument("--pkl_path", type=str, 
                        default="representations.pkl",
                        help="Path to the pickle file with celebrity embeddings")
    
    parser.add_argument("--imdb_path", type=str, 
                        default="imdb_data_set",
                        help="Path to the IMDB dataset image directory")
    
    parser.add_argument("--photo", type=str, 
                        help="Path to an existing photo (if webcam not used)")
    
    parser.add_argument("--webcam", action="store_true",
                        help="Use webcam to capture photo")
    
    parser.add_argument("--matches", type=int, default=3,
                        help="Number of celebrity matches to show (default: 3)")
    
    parser.add_argument("--gender", type=str, choices=['0', '1', 'm', 'f', 'male', 'female'],
                        help="Filter celebrities by gender (0/m/male or 1/f/female)")
    
    # Analizar argumentos
    args = parser.parse_args()
    
    # Si no se especifica ni webcam ni ruta de foto, usar webcam por defecto
    use_webcam = args.webcam or (not args.photo)
    
    # Procesar argumento de género - MAPEO CORREGIDO
    gender = None
    if args.gender:
        # MAPEO INVERTIDO: 1.0 = masculino, 0.0 = femenino en el conjunto de datos
        if args.gender in ['0', 'f', 'female']:
            gender = 0.0  # Femenino
        elif args.gender in ['1', 'm', 'male']:
            gender = 1.0  # Masculino
        
        # Añadir información de depuración
        print(f"Gender filter set to: {gender} ({args.gender})")
    
    # Ejecutar la función principal
    find_celebrity_lookalikes(
        pkl_path=args.pkl_path,
        imdb_images_base_path=args.imdb_path,
        photo_path=args.photo,
        use_webcam=use_webcam,
        num_matches=args.matches,
        gender=gender
    )