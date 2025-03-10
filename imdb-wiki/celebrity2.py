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

# Load the celebrity embeddings dataframe
def load_embeddings(pkl_path):
    print(f"Loading celebrity embeddings from {pkl_path}...")
    df = pd.read_pickle(pkl_path)
    print(f"Loaded {len(df)} celebrity embeddings")
    return df

# Extract the vector from the DeepFace representation object
def extract_vector(representation):
    if isinstance(representation, list) and len(representation) > 0:
        return representation[0]['embedding']
    else:
        return representation['embedding']

# Capture image from webcam
def capture_image():
    print("Initializing webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise Exception("Could not open webcam. Please check your camera connection.")
    
    # Wait for camera to initialize
    time.sleep(1)
    
    print("Press SPACE to capture the photo or ESC to cancel...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            raise Exception("Failed to capture image from webcam")
        
        # Display instructions
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "Press SPACE to take photo", (50, 50), font, 1, (0, 255, 0), 2)
        
        # Show the frame
        cv2.imshow("Webcam", frame)
        
        # Check for key press
        key = cv2.waitKey(1) & 0xFF
        
        # If space key is pressed, take the photo
        if key == 32:  # Space key
            # Display "Cheese!" moment
            cv2.putText(frame, "Cheese!", (50, 100), font, 1, (0, 255, 0), 2)
            cv2.imshow("Webcam", frame)
            cv2.waitKey(500)
            
            # Save image temporarily
            temp_path = "temp_webcam_image.jpg"
            cv2.imwrite(temp_path, frame)
            print(f"Image captured and saved to {temp_path}")
            break
        
        # If ESC key is pressed, cancel
        elif key == 27:  # ESC key
            cap.release()
            cv2.destroyAllWindows()
            raise Exception("Photo capture cancelled by user")
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    
    return temp_path

# Validate and use an existing photo
def use_existing_photo(photo_path):
    if not os.path.exists(photo_path):
        raise Exception(f"Photo not found at: {photo_path}")
    
    # Read the image to verify it's valid
    img = cv2.imread(photo_path)
    if img is None:
        raise Exception(f"Could not read image at: {photo_path}. Make sure it's a valid image file.")
    
    print(f"Using existing photo: {photo_path}")
    return photo_path

# Get face embedding for the image
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

# Find the most similar celebrities
def find_similar_celebrities(user_embedding, celebrity_df, top_n=3, gender=None):
    print("Finding celebrity lookalikes...")
    
    # Extract the vector from the user's embedding
    user_vector = extract_vector(user_embedding)
    
    # Filter by gender if specified
    if gender is not None:
        print(f"Filtering by gender: {gender}")
        
        # Print first few gender values to verify format
        print("Sample gender values in dataset:")
        for i in range(min(5, len(celebrity_df))):
            print(f"  Index {i}: {celebrity_df['gender'].iloc[i]}, Type: {type(celebrity_df['gender'].iloc[i])}")
        
        # Convert gender values to integers if they're stored as arrays/lists
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
            
        # Verify first few records in filtered dataset
        print("First 5 celebrities after filtering:")
        for i in range(min(5, len(filtered_df))):
            idx = filtered_df.index[i]
            gender_val = filtered_df['gender'].iloc[i]
            name = filtered_df['celebrity_name'].iloc[i]
            print(f"  {name}: gender={gender_val}")
    else:
        filtered_df = celebrity_df
    
    # Get vectors from all filtered celebrities for comparison
    celebrity_vectors = []
    for idx, row in filtered_df.iterrows():
        raw_vector = row['face_vector_raw']
        if raw_vector is not None:
            celebrity_vectors.append((idx, extract_vector(raw_vector)))
    
    # Calculate similarities
    similarities = []
    for idx, celeb_vector in celebrity_vectors:
        similarity = cosine_similarity([user_vector], [celeb_vector])[0][0]
        similarities.append((idx, similarity))
    
    # Group by celebrity name and keep only the highest similarity match for each
    celebrity_matches = {}
    for idx, similarity in similarities:
        celeb_name = filtered_df.loc[idx, 'celebrity_name']
        if celeb_name not in celebrity_matches or similarity > celebrity_matches[celeb_name][1]:
            celebrity_matches[celeb_name] = (idx, similarity)
    
    # Convert back to list and sort by similarity (highest first)
    unique_similarities = list(celebrity_matches.values())
    unique_similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Get top N matches
    top_matches = unique_similarities[:top_n]
    
    # Verify gender of selected matches
    print("\nVerifying gender of top matches:")
    for idx, similarity in top_matches:
        gender_val = celebrity_df.loc[idx, 'gender']
        name = celebrity_df.loc[idx, 'celebrity_name']
        print(f"  {name}: gender={gender_val}, similarity={similarity:.2f}")
    
    return top_matches

# Display the results
def display_results(user_image_path, top_matches, celebrity_df, base_path):
    print("Displaying results...")
    
    # Show the top celebrity matches with gender information
    for i, (idx, similarity) in enumerate(top_matches):
        # Get celebrity info
        celebrity = celebrity_df.loc[idx]
        celebrity_name = celebrity['celebrity_name']
        gender_val = celebrity['gender']
        print(f"Match #{i+1}: {celebrity_name}, Gender: {gender_val}, Similarity: {similarity:.2f}")
    
    # Create a figure with a grid layout
    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, 4, figure=fig)
    
    # Show the user's image
    user_img = cv2.imread(user_image_path)
    user_img = cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB)
    ax_user = fig.add_subplot(gs[0, 1:3])
    ax_user.imshow(user_img)
    ax_user.set_title("Your Photo", fontsize=16)
    ax_user.axis('off')
    
    # Show the top celebrity matches
    for i, (idx, similarity) in enumerate(top_matches):
        # Get celebrity info
        celebrity = celebrity_df.loc[idx]
        celebrity_name = celebrity['celebrity_name']
        celebrity_path = f"{base_path}/{celebrity['full_path'][0]}"
        
        # Create subplot based on position
        if i == 0:
            ax = fig.add_subplot(gs[1, 0:2])
        elif i == 1:
            ax = fig.add_subplot(gs[1, 1:3])
        else:
            ax = fig.add_subplot(gs[1, 2:4])
        
        # Display celebrity image
        try:
            celeb_img = cv2.imread(celebrity_path)
            celeb_img = cv2.cvtColor(celeb_img, cv2.COLOR_BGR2RGB)
            ax.imshow(celeb_img)
        except Exception as e:
            ax.text(0.5, 0.5, "Image not found", 
                    horizontalalignment='center', verticalalignment='center')
        
        # Add caption with name and similarity score
        ax.set_title(f"{celebrity_name}\nSimilarity: {similarity:.2f}", fontsize=14)
        ax.axis('off')
    
    # Add a main title
    plt.suptitle("Celebrity Lookalikes", fontsize=20)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    
    # Save result
    result_path = "celebrity_lookalikes_result.jpg"
    plt.savefig(result_path)
    print(f"Results saved to {result_path}")
    
    # Show the result
    plt.show()
    
    return result_path

# Main function
def find_celebrity_lookalikes(pkl_path, imdb_images_base_path, photo_path=None, use_webcam=True, num_matches=3, gender=None):
    try:
        # Load the celebrity embeddings
        celebrity_df = load_embeddings(pkl_path)
        
        # Prepare the vectors for faster comparison
        print("Preprocessing celebrity embeddings...")
        celebrity_df = celebrity_df.dropna(subset=['face_vector_raw'])
        
        # Get the user's image - either from webcam or from file
        if use_webcam:
            user_image_path = capture_image()
        else:
            if photo_path is None:
                raise Exception("Photo path not provided. Please specify a path to an image file.")
            user_image_path = use_existing_photo(photo_path)
        
        # Get face embedding for the image
        user_embedding = get_face_embedding(user_image_path)
        
        # Find similar celebrities
        top_matches = find_similar_celebrities(user_embedding, celebrity_df, top_n=num_matches, gender=gender)
        
        # Display results
        result_path = display_results(user_image_path, top_matches, celebrity_df, imdb_images_base_path)
        
        print("\nDone! Check the matplotlib window for your celebrity lookalikes.")
        print(f"Results saved to {result_path}")
        
        return top_matches, result_path
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None

if __name__ == "__main__":
    # Set up command line arguments
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
    
    # Parse arguments
    args = parser.parse_args()
    
    # If neither webcam nor photo path is specified, default to webcam
    use_webcam = args.webcam or (not args.photo)
    
    # Process gender argument - CORRECTED MAPPING
    gender = None
    if args.gender:
        # REVERSED MAPPING: 1.0 = male, 0.0 = female in the dataset
        if args.gender in ['0', 'f', 'female']:
            gender = 0.0  # Female
        elif args.gender in ['1', 'm', 'male']:
            gender = 1.0  # Male
        
        # Add debug information
        print(f"Gender filter set to: {gender} ({args.gender})")
    
    # Run the main function
    find_celebrity_lookalikes(
        pkl_path=args.pkl_path,
        imdb_images_base_path=args.imdb_path,
        photo_path=args.photo,
        use_webcam=use_webcam,
        num_matches=args.matches,
        gender=gender
    )