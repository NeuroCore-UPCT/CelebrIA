import cv2
import numpy as np
import os
import json
from deepface import DeepFace

# Constants for paths
FOLDER_PATH = "imagenes"  
HAARCASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
EMBEDDINGS_JSON_PATH = os.path.join(FOLDER_PATH, "embeddings.json")
FINAL_JSON_PATH = "embeddings_famosos.json"

# Ensure the folder exists
os.makedirs(FOLDER_PATH, exist_ok=True)

# Function to get the next capture number
def obtener_numero_captura() -> int:
    """
    Retrieves the next available capture number based on images already stored in the folder.
    
    Returns:
        int: The next available capture number.
    """
    archivos = [f for f in os.listdir(FOLDER_PATH) if f.startswith("captura_") and f.endswith("_1.jpg")]
    if not archivos:
        return 1  # No captures found, start with 1
    # Extract numbers from filenames and get the maximum one
    numeros = [int(f.split("_")[1]) for f in archivos]
    return max(numeros) + 1

# Function to load embeddings from a JSON file
def cargar_embeddings(ruta_json: str) -> dict:
    """
    Loads embeddings from a JSON file.
    
    Args:
        ruta_json (str): Path to the JSON file containing the embeddings.
    
    Returns:
        dict: A dictionary of embeddings loaded from the file.
    """
    try:
        with open(ruta_json, "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print(f"❌ File not found: {ruta_json}")
        return {}
    except json.JSONDecodeError:
        print(f"❌ Error decoding JSON from file: {ruta_json}")
        return {}

# Function to calculate similarity between two embeddings
def calcular_similitud(embedding1: list, embedding2: list) -> float:
    """
    Calculates similarity between two embeddings using Euclidean distance.
    
    Args:
        embedding1 (list): The first embedding.
        embedding2 (list): The second embedding.
    
    Returns:
        float: Similarity percentage between 0 and 100.
    """
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    
    # Calculate the Euclidean distance between the embeddings
    distancia = np.linalg.norm(embedding1 - embedding2)
    distancia_maxima = np.sqrt(len(embedding1)) * 10  # Maximum possible distance
    similitud = (1 - (distancia / distancia_maxima)) * 100  # Normalize the similarity to a percentage
    
    return max(0, min(similitud, 100))  # Ensure similarity is between 0 and 100

# Function to find the top three most similar embeddings
def encontrar_tres_mas_parecidos(embedding_captura: list, embeddings_final: list) -> list:
    """
    Finds the top three most similar embeddings to a given capture embedding.

    Args:
        embedding_captura (list): The embedding of the captured face.
        embeddings_final (list): A list of final embeddings to compare with.

    Returns:
        list: A sorted list of the top three most similar embeddings with their similarity scores.
    """
    similitudes = [
        (item["ruta"], calcular_similitud(embedding_captura, item["embedding"]))
        for item in embeddings_final
    ]
    
    # Sort by similarity in descending order
    similitudes.sort(key=lambda x: x[1], reverse=True)
    
    return similitudes[:3]

# Function to delete all files in a folder
def borrar_contenido_carpeta(carpeta: str) -> None:
    """
    Deletes all files in the specified folder.
    
    Args:
        carpeta (str): The path to the folder whose contents will be deleted.
    """
    confirmacion = input("Type '.' to delete all files in the folder: ")
    if confirmacion.lower() == ".":
        for archivo in os.listdir(carpeta):
            ruta_archivo = os.path.join(carpeta, archivo)
            if os.path.isfile(ruta_archivo):
                os.remove(ruta_archivo)  # Delete the file
        print("All files have been deleted.")
    else:
        print("Operation canceled.")

def main():
    # Step 1: Capture and save the image
    numero_captura = obtener_numero_captura()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error accessing the webcam")
        return
    
    print("📸 Press 'SPACE' to capture the image...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture image")
            break

        cv2.imshow("Webcam - Press SPACE to capture", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # Press SPACE to capture
            original_filename = f"captura_{numero_captura}.jpg"
            original_path = os.path.join(FOLDER_PATH, original_filename)
            cv2.imwrite(original_path, frame)  # Save captured image
            print(f"✅ Original image saved at: {original_path}")
            break

    cap.release()
    cv2.destroyAllWindows()

    # Step 2: Detect face and calculate embeddings
    face_classifier = cv2.CascadeClassifier(HAARCASCADE_PATH)
    img = cv2.imread(original_path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale for face detection
    faces = face_classifier.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

    if len(faces) > 0:
        embeddings_dict = {}

        for i, (x, y, w, h) in enumerate(faces, start=1):
            face_crop = img[y:y+h, x:x+w]

            cropped_filename = f"captura_{numero_captura}_{i}.jpg"
            cropped_path = os.path.join(FOLDER_PATH, cropped_filename)
            cv2.imwrite(cropped_path, face_crop)
            print(f"✅ Cropped image saved at: {cropped_path}")

            print(f"⚙ Calculating embedding for: {cropped_filename}...")
            try:
                embedding = DeepFace.represent(
                    img_path=cropped_path, model_name="Facenet", enforce_detection=False
                )[0]["embedding"]
                embeddings_dict[cropped_filename] = embedding
            except Exception as e:
                print(f"❌ Error calculating embedding for {cropped_filename}: {e}")

        # Save embeddings to JSON
        with open(EMBEDDINGS_JSON_PATH, "w") as f:
            json.dump(embeddings_dict, f)

        print(f"✅ Embeddings saved to: {EMBEDDINGS_JSON_PATH}")
    else:
        print("⚠ No face detected in the image.")

    # Step 3: Compare with final embeddings
    embeddings_captura = cargar_embeddings(EMBEDDINGS_JSON_PATH)
    embeddings_final = cargar_embeddings(FINAL_JSON_PATH)
    
    for nombre_imagen, embedding_captura in embeddings_captura.items():
        print(f"Detected person in {nombre_imagen}:")
        tres_mas_parecidos = encontrar_tres_mas_parecidos(embedding_captura, embeddings_final)
        
        for i, (ruta, similitud) in enumerate(tres_mas_parecidos, start=1):
            print(f"{i}. {ruta} with a {similitud:.2f}% similarity.")
        print()

    # Step 4: Clean folder
    borrar_contenido_carpeta(FOLDER_PATH)

if __name__ == "__main__":
    main()
