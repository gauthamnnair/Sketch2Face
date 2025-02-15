import numpy as np
import matplotlib.pyplot as plt
import tensorflow.keras.backend as K
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.saving import register_keras_serializable
from skimage.metrics import structural_similarity as ssim

# Register custom sampling function
@register_keras_serializable(package="Custom")
def sampling(args):
    z_mean, z_log_sigma = args
    epsilon = K.random_normal(shape=(K.shape(z_mean)[0], K.int_shape(z_mean)[1]))
    return z_mean + K.exp(z_log_sigma / 2) * epsilon

# Load the trained VAE model
vae_model = load_model("vae_2skf_best_model.h5", custom_objects={"sampling": sampling}, compile=False)

def generate_best_reconstruction(img_path):
    """Generates and returns the best reconstructed image using VAE."""

    # Load and preprocess sketch
    img = image.load_img(img_path, target_size=(256, 256))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array.astype("float32") / 255.0

    # Generate 5 reconstructed images
    reconstructions = []
    for _ in range(50):
        decode = vae_model.predict(img_array)
        reconstructions.append(np.clip(decode[0], 0, 1))

    # Compute SSIM to select the best reconstruction
    original_gray = np.dot(img_array[0, :, :, :3], [0.2989, 0.5870, 0.1140])
    best_img, best_ssim = None, -1

    for recon in reconstructions:
        recon_gray = np.dot(recon, [0.2989, 0.5870, 0.1140])
        score = ssim(original_gray, recon_gray, data_range=recon_gray.max() - recon_gray.min())

        if score > best_ssim:
            best_ssim = score
            best_img = recon

    # Save the best reconstructed image
    output_path = r"temp\reconstructed_image.png"
    plt.imsave(output_path, best_img)

    print(f"Best reconstructed image saved as '{output_path}'.")
    print("Will take 2-3 Mins for Searching and Comparing in the Database")
    return output_path
