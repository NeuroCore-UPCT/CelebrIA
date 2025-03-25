from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import os
import cv2
import base64
import numpy as np
import json
import time
import shutil
import sys
from PIL import Image
import pandas as pd
from deepface import DeepFace

# Import functions from celebrity2.py
from celebrity2 import load_embeddings, get_face_embedding, find_similar_celebrities, extract_vector

app = Flask(__name__, 
            static_folder='Frontend/Static',
            template_folder='Frontend/Templates')

# Paths for the celebrity embeddings and image dataset
EMBEDDINGS_PATH = "representations.pkl"
IMDB_IMAGES_PATH = "imdb_data_set"

# Ensure the personas directory exists
os.makedirs('personas', exist_ok=True)

# Ensure the face-db directory exists
os.makedirs('face-db', exist_ok=True)

# Load celebrity embeddings at startup
try:
    celebrity_df = load_embeddings(EMBEDDINGS_PATH)
    print(f"Successfully loaded {len(celebrity_df)} celebrity embeddings")
except Exception as e:
    print(f"Warning: Failed to load celebrity embeddings: {e}")
    print("Using empty DataFrame as fallback")
    celebrity_df = pd.DataFrame()

@app.route('/')
def index():
    """Render the main page with webcam capture"""
    return render_template('index.html')

@app.route('/carga')
def carga():
    """Render the loading page"""
    return render_template('carga.html')

@app.route('/resultado')
def resultado():
    """Render the results page"""
    return render_template('resultado.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    """Process the captured image and find celebrity matches"""
    try:
        # Get the image data from the request
        image_data = request.json.get('image')
        
        # Get the gender filter if present
        gender = request.json.get('gender')
        
        # Remove the data URL prefix
        image_data = image_data.split(',')[1]
        
        # Decode the base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode the image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Save the original image
        original_path = "personas/foto.jpg"
        cv2.imwrite(original_path, image)
        
        # Process the image and wait for results
        results = procesar_imagen(original_path, gender)
        
        # Check if we have valid results
        if not results or len(results) == 0:
            return jsonify({"success": False, "error": "No faces detected"})
        
        return jsonify({
            "success": True, 
            "redirect": "/resultado",
            "faces_detected": len(results)
        })
    
    except Exception as e:
        print(f"Error in process_image: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/get_results')
def get_results():
    """Get the results from the JSON files"""
    try:
        results = []
        # Read all JSON files in the personas directory
        json_files = [file for file in os.listdir('personas') if file.startswith('json_persona') and file.endswith('.json')]
        
        # Log the number of JSON files found
        print(f"Found {len(json_files)} JSON files: {json_files}")
        
        for file in json_files:
            with open(os.path.join('personas', file), 'r') as f:
                result_data = json.load(f)
                # Log each result file content summary
                print(f"File {file} contains data for persona: {result_data.get('cara_detectada')}")
                results.append(result_data)
        
        # Return more diagnostic information
        return jsonify({
            "success": True,
            "file_count": len(json_files),
            "file_names": json_files,
            "results": results
        })
    
    except Exception as e:
        print(f"Error in get_results: {str(e)}")
        return jsonify({"error": str(e), "success": False})

@app.route('/face-db/<path:filename>')
def serve_image(filename):
    """Serve images from the face-db directory"""
    return send_from_directory('face-db', filename)

@app.route('/personas/<path:filename>')
def serve_persona_image(filename):
    """Serve images from the personas directory"""
    return send_from_directory('personas', filename)

@app.route('/clear_data', methods=['POST'])
def clear_data():
    """Clear the data in the personas directory"""
    try:
        # Ensure the personas directory exists
        os.makedirs('personas', exist_ok=True)
        
        # Delete all files in the personas directory
        borrar_contenido_carpeta_flask("personas")
        
        # Add a small delay to ensure files are cleared
        time.sleep(0.5)
        
        # Return success response
        return jsonify({"success": True, "message": "Data cleared successfully", "timestamp": time.time()})
    except Exception as e:
        print(f"Error clearing data: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/process_status', methods=['GET'])
def process_status():
    """Check the status of the image processing"""
    try:
        # Check if the original image exists
        if not os.path.exists('personas/foto.jpg'):
            return jsonify({
                "status": "waiting", 
                "message": "Esperando imagen..."
            })
        
        # Check if there are any JSON files in the personas directory
        json_files = [f for f in os.listdir('personas') if f.startswith('json_persona') and f.endswith('.json')]
        
        if not json_files:
            # Check if face detection has started
            face_files = [f for f in os.listdir('personas') if f.startswith('foto') and f.endswith('.jpg') and f != 'foto.jpg']
            if face_files:
                return jsonify({
                    "status": "processing", 
                    "message": "Buscando coincidencias con famosos..."
                })
            else:
                return jsonify({
                    "status": "processing", 
                    "message": "Detectando rostros en la imagen..."
                })
        
        # Read the first JSON file to check if it has matches
        with open(os.path.join('personas', json_files[0]), 'r') as f:
            data = json.load(f)
        
        if not data.get('matches') or len(data.get('matches', [])) == 0:
            return jsonify({
                "status": "error", 
                "message": "No se encontraron coincidencias con famosos"
            })
        
        return jsonify({
            "status": "complete", 
            "message": "¡Coincidencias encontradas! Redirigiendo..."
        })
    
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Error en el procesamiento: {str(e)}"
        })

# Backend functions using celebrity2.py logic

def detectar_personas(ruta_front):
    """
    Detecta las caras en una imagen y guarda cada cara detectada como una imagen separada.
    
    :param ruta_front: Ruta de la imagen donde se detectarán las caras.
    :return: Lista de rutas de las imágenes de las caras detectadas.
    """
    try:
        # Intentar extraer caras de la imagen
        faces = DeepFace.extract_faces(ruta_front, enforce_detection=False)
        lista_rutas = []
        
        if not faces or len(faces) == 0:
            print("No faces detected, using original image")
            # Si no se detectan caras, usar la imagen original
            shutil.copy(ruta_front, "personas/foto0.jpg")
            lista_rutas.append("personas/foto0.jpg")
        else:
            # Procesar cada cara detectada
            for i in range(len(faces)):
                face_array = faces[i]['face']  # Obtener el array de la cara detectada
                face_array = (face_array * 255).astype(np.uint8)  # Convertir a formato de imagen
                face_image = Image.fromarray(face_array)  # Convertir el array en una imagen PIL
                face_image.save(f"personas/foto{i}.jpg")  # Guardar la imagen
                lista_rutas.append(f"personas/foto{i}.jpg")  # Añadir la ruta a la lista
    
    except Exception as e:
        print(f"Error detecting faces: {e}")
        # En caso de error, usar la imagen original
        shutil.copy(ruta_front, "personas/foto0.jpg")
        lista_rutas = ["personas/foto0.jpg"]
    
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
    # Siempre usar la imagen original para mostrar en el cuadrado pequeño
    original_image = "personas/foto.jpg"
    
    if len(lista_personas) > 1:
        data = {
            "n_personas": len(lista_personas),  # Número de personas detectadas
            "persona": original_image,  # Ruta de la imagen original
            "cara_detectada": lista_personas[n],  # Ruta de la cara detectada
            "matches": []
        }
    elif len(lista_personas) == 1:
        data = {
            "n_personas": len(lista_personas),  # Número de personas detectadas
            "persona": original_image,  # Ruta de la imagen original
            "cara_detectada": lista_personas[0],  # Ruta de la cara detectada
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

def sacar_nombre_ruta(lista_rutas_celebridades):
    """
    Extrae los nombres de las rutas de las imágenes de los famosos.
    
    :param lista_rutas_celebridades: Lista de rutas de las imágenes de los famosos.
    :return: Lista de nombres de los famosos.
    """
    nombres = []
    for ruta in lista_rutas_celebridades:
        try:
            # Get the celebrity name from the path
            # Format is typically: imdb_data_set/Tom_Hanks/photo.jpg
            parts = ruta.split('/')
            if len(parts) >= 2:
                nombre = parts[1].split('.')[0].replace('_', ' ')
            else:
                nombre = os.path.basename(ruta).split('.')[0].replace('_', ' ')
            nombres.append(nombre)
        except Exception as e:
            print(f"Error extracting name from path {ruta}: {e}")
            nombres.append("Unknown Celebrity")
    
    return nombres

def encontrar_3_mas_parecidos(ruta_cara, gender=None):
    """
    Encuentra las 3 imágenes más parecidas en la base de datos de celebrities.
    Usa celebrity2.py para encontrar coincidencias.
    
    :param ruta_cara: Ruta de la imagen de la cara a comparar.
    :param gender: Filtro de género para la búsqueda.
    :return: Lista de rutas de las imágenes más parecidas y sus porcentajes de similitud.
    """
    try:
        # Convert gender to float if it's provided as a string
        gender_filter = None
        if gender is not None:
            try:
                gender_filter = float(gender)
                print(f"Using gender filter: {gender_filter}")
            except ValueError:
                print(f"Invalid gender value: {gender}, ignoring gender filter")
        
        # Get the face embedding
        user_embedding = get_face_embedding(ruta_cara)
        
        # Find similar celebrities (top 3) with gender filter
        top_matches = find_similar_celebrities(user_embedding, celebrity_df, top_n=3, gender=gender_filter)
        
        # Extract paths and similarities
        rutas_imagen = []
        porcentage_parecidos = []
        
        for idx, similarity in top_matches:
            # Get celebrity path
            celebrity = celebrity_df.loc[idx]
            path = f"{IMDB_IMAGES_PATH}/{celebrity['full_path'][0]}"
            
            # Copy the image to face-db for serving
            filename = f"{celebrity['celebrity_name'].replace(' ', '_')}.jpg"
            target_path = f"face-db/{filename}"
            
            try:
                # Copy the celebrity image to face-db
                if os.path.exists(path):
                    shutil.copy(path, target_path)
                else:
                    # Create a placeholder image if original not found
                    create_placeholder_image(target_path, celebrity['celebrity_name'])
                
                rutas_imagen.append(target_path)
                
                # Convert similarity to percentage (0-100)
                similarity_pct = round(similarity * 100, 2)
                porcentage_parecidos.append(similarity_pct)
                
            except Exception as e:
                print(f"Error copying celebrity image {path}: {e}")
                # Create a placeholder with error message
                error_path = f"face-db/error_{len(rutas_imagen)}.jpg"
                create_placeholder_image(error_path, "Image not found")
                rutas_imagen.append(error_path)
                porcentage_parecidos.append(50.0)  # Default similarity
        
        # Make sure we have exactly 3 results
        while len(rutas_imagen) < 3:
            error_path = f"face-db/placeholder_{len(rutas_imagen)}.jpg"
            create_placeholder_image(error_path, "No match found")
            rutas_imagen.append(error_path)
            porcentage_parecidos.append(30.0 - (5.0 * len(rutas_imagen)))
            
        return rutas_imagen[:3], porcentage_parecidos[:3]
        
    except Exception as e:
        print(f"Error finding similar celebrities: {e}")
        
        # Create placeholder images if the matching process fails
        rutas_imagen = []
        porcentage_parecidos = []
        
        for i in range(3):
            error_path = f"face-db/error_{i}.jpg"
            create_placeholder_image(error_path, f"Error: {str(e)[:20]}")
            rutas_imagen.append(error_path)
            porcentage_parecidos.append(30.0 - (5.0 * i))
            
        return rutas_imagen, porcentage_parecidos

def create_placeholder_image(path, text):
    """Create a placeholder image with text"""
    img = np.ones((300, 300, 3), dtype=np.uint8) * 200  # Light gray background
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 0.7, 2)[0]
    text_x = (img.shape[1] - text_size[0]) // 2
    text_y = (img.shape[0] + text_size[1]) // 2
    
    # Add text with black color
    cv2.putText(img, text, (text_x, text_y), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Save the image
    cv2.imwrite(path, img)

def procesar_imagen(original_path, gender=None):
    """Process the image using celebrity2.py and return the results"""
    # Detect faces
    lista_personas = detectar_personas(original_path)
    results = []
    
    # Log the gender value received
    print(f"Processing image with gender filter: {gender}")
    
    # Process each detected face
    for i in range(len(lista_personas)):
        # Find the 3 most similar celebrities with gender filter if provided
        lista_ruta_famosos, lista_parecidos = encontrar_3_mas_parecidos(lista_personas[i], gender)
        
        # Extract celebrity names from paths
        lista_nombre_famosos = sacar_nombre_ruta(lista_ruta_famosos)
        
        # Create JSON result for this face
        hacer_json(lista_personas, i, lista_ruta_famosos, lista_nombre_famosos, lista_parecidos)
        
        # Create a result object for this person
        person_result = {
            "persona": original_path,  # Original image path
            "cara_detectada": lista_personas[i],  # Detected face path
            "matches": []
        }
        
        # Add each celebrity match
        for j in range(len(lista_nombre_famosos)):
            person_result["matches"].append({
                "name": lista_nombre_famosos[j],
                "similarity": lista_parecidos[j],
                "image_data": lista_ruta_famosos[j]
            })
        
        results.append(person_result)
    
    return results

def borrar_contenido_carpeta_flask(carpeta):
    """
    Borra el contenido de una carpeta (versión para Flask)
    
    :param carpeta: Ruta de la carpeta a borrar
    """
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

if __name__ == '__main__':
    # Check if the embeddings file exists
    if not os.path.exists(EMBEDDINGS_PATH):
        print(f"Warning: Embeddings file not found at {EMBEDDINGS_PATH}")
        print("Please make sure to download or create the celebrity embeddings file.")
    
    # Check if the IMDB images directory exists
    if not os.path.exists(IMDB_IMAGES_PATH):
        print(f"Warning: IMDB images directory not found at {IMDB_IMAGES_PATH}")
        print("Please make sure to download and extract the IMDB dataset.")
    
    # Start the Flask app
    app.run(debug=True) 