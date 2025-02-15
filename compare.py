import os
import numpy as np
from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean

# Choose the best-performing model
MODEL_NAME = "Facenet"  # Try: "VGG-Face", "ArcFace", "Dlib", "DeepID", "Facenet"

def compare(generated_image_path, image_folder="Kaggle/photos"):
    """Finds the most similar image to the reconstructed image."""
    
    print(f"Using {MODEL_NAME} model for comparison...")

    #  Load the DeepFace model once to avoid redundant calls
    try:
        model = DeepFace.build_model(MODEL_NAME)
    except Exception as e:
        print(f"Error loading {MODEL_NAME} model: {e}")
        return None

    #  Compute the embedding for the generated image
    print("Computing embedding for the reconstructed image...")
    try:
        generated_embedding = DeepFace.represent(
            generated_image_path, model_name=MODEL_NAME, enforce_detection=False
        )

        if not generated_embedding or not generated_embedding[0].get('embedding'):
            print("Error: No valid embedding found for the generated image.")
            return None

        generated_embedding = np.array(generated_embedding[0]['embedding'])

    except Exception as e:
        print(f"Error computing embedding for reconstructed image: {e}")
        return None

    similarity_scores = []

    #  Ensure image folder exists
    if not os.path.exists(image_folder):
        print(f"Error: Image folder '{image_folder}' not found.")
        return None

    #  Loop through all images in the dataset folder
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)

        try:
            #  Compute embedding for dataset image
            face_embedding = DeepFace.represent(
                image_path, model_name=MODEL_NAME, enforce_detection=False
            )

            if not face_embedding or not face_embedding[0].get('embedding'):
                print(f"Skipping {image_name} (No valid face detected)")
                continue

            face_embedding = np.array(face_embedding[0]['embedding'])

            #  Compute both cosine similarity and Euclidean distance
            cosine_sim = cosine_similarity([generated_embedding], [face_embedding])[0][0]
            l2_distance = euclidean(generated_embedding, face_embedding)

            #  Store results (higher cosine similarity is better, lower L2 distance is better)
            similarity_scores.append((image_name, cosine_sim, l2_distance))

        except Exception as e:
            print(f"Skipping {image_name} due to error: {e}")

    if not similarity_scores:
        print("No valid images found for comparison.")
        return None

    #  Sort by cosine similarity (descending) and L2 distance (ascending)
    similarity_scores.sort(key=lambda x: (-x[1], x[2]))

    #  Get the most similar image
    most_similar_image_name, highest_score, lowest_distance = similarity_scores[0]
    most_similar_image_path = os.path.join(image_folder, most_similar_image_name)

    print(f"Most similar image: {most_similar_image_name}")
    print(f"Cosine Similarity: {highest_score:.4f}, Euclidean Distance: {lowest_distance:.4f}")

    return most_similar_image_path

#  Corrected function call with proper path separator
compare("temp/reconstructed_image.png")
