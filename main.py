import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
import run_model
import subprocess
import time
import logging
import tensorflow as tf
import warnings

#  Suppress TensorFlow debug & info messages
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # 0 = all messages, 1 = filter INFO, 2 = filter WARNING, 3 = filter ERROR

#  Suppress TensorFlow warnings
tf.get_logger().setLevel(logging.ERROR)

#  Suppress Python warnings (e.g., from Keras)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Hardcoded login details
USERNAME = "admin"
PASSWORD = "password123"

is_logged_in = False
uploaded_filepath = None

def login():
    """Handles user login before allowing access to upload images."""
    global is_logged_in
    username = username_entry.get()
    password = password_entry.get()

    if username == USERNAME and password == PASSWORD:
        is_logged_in = True
        messagebox.showinfo("Login Successful", "Welcome to the Criminal Sketch Upload System!")
        login_window.destroy()
        open_main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def save_to_logs(original_path, reconstructed_path):
    """Saves uploaded and reconstructed images in a folder named after the uploaded filename."""
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)  #  Ensure logs directory exists

    #  Extract original filename (without extension)
    original_filename = os.path.basename(original_path)
    file_base_name = os.path.splitext(original_filename)[0]  # Remove file extension

    #  Create a folder using the original filename inside logs/
    upload_folder = os.path.join(logs_dir, file_base_name)
    os.makedirs(upload_folder, exist_ok=True)

    #  Define paths inside the folder
    original_save_path = os.path.join(upload_folder, original_filename)
    reconstructed_filename = f"reconstructed_{original_filename}"
    reconstructed_save_path = os.path.join(upload_folder, reconstructed_filename)

    #  Copy images to the folder
    shutil.copy(original_path, original_save_path)
    shutil.copy(reconstructed_path, reconstructed_save_path)

    #  Save log entry
    log_entry = f"Upload '{original_filename}': Stored in logs/{file_base_name}/\n"
    with open(os.path.join(logs_dir, "log.txt"), "a") as log_file:
        log_file.write(log_entry)

    print(f"Saved in logs/{file_base_name}/: {original_filename}, {reconstructed_filename}")

def display_images(uploaded_path, best_image_path, compared_image_path, uploaded_name, reconstructed_name, compared_name, accuracy):
    """Displays images and filenames in GUI."""
    for img_path, label in zip([uploaded_path, best_image_path, compared_image_path], 
                               [uploaded_label, generated_label, compared_label]):
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path).resize((500, 500), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            label.config(image=img)
            label.image = img
        else:
            label.config(text="No Image Found")

    #  Update labels with filenames & accuracy
    uploaded_filename_label.config(text=f"Uploaded Sketch: {uploaded_name}")
    generated_filename_label.config(text=f"Reconstructed Image: {reconstructed_name}")
    compared_filename_label.config(text=f"Most Similar Image: {compared_name}\nAccuracy: {accuracy:.2f}%")

def process_sketch():
    """Handles sketch processing, model execution, and image comparison."""
    global uploaded_filepath
    if uploaded_filepath:
        print(f"Processing sketch: {uploaded_filepath}")

        uploaded_name = os.path.basename(uploaded_filepath)

        # Step 1: Generate best reconstructed image
        best_image_path = run_model.generate_best_reconstruction(uploaded_filepath)
        reconstructed_name = os.path.basename(best_image_path)

        save_to_logs(uploaded_filepath, best_image_path)

        # Step 2: Run compare.py using subprocess
        try:
            result = subprocess.run(["python", "compare.py", best_image_path], capture_output=True, text=True, check=True)
            output_lines = result.stdout.strip().split("\n")

            print("Output:\n", result.stdout)

            #  Extract filename, Cosine Similarity, and Euclidean Distance
            compared_image_filename, cosine_sim, euclidean_dist = None, 0.0, 0.0
            for line in output_lines:
                if "Most similar image:" in line:
                    compared_image_filename = line.split(": ")[1].strip()
                elif "Cosine Similarity:" in line:
                    cosine_sim = float(line.split(": ")[1].split(",")[0].strip())
                elif "Euclidean Distance:" in line:
                    euclidean_dist = float(line.split(": ")[1].strip())

            if not compared_image_filename:
                print("No valid image found.")
                messagebox.showwarning("Comparison Failed", "No similar images found.")
                return

            image_folder = "Kaggle/photos"
            compared_image_path = os.path.abspath(os.path.join(image_folder, compared_image_filename))
            #print(f"Compared Image Path: {compared_image_path}")

            if not os.path.exists(compared_image_path):
                messagebox.showwarning("Comparison Failed", "No similar images found.")
                return

            #  Compute Final Custom Similarity Score
            max_euclidean = 10  # **You can adjust this based on your dataset**
            euclidean_scaled = (euclidean_dist / max_euclidean) * 100  # Normalize to 0-100
            final_score = (cosine_sim * 100) - euclidean_scaled  # **Custom Formula**

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to compare images: {e}")
            return

        # Step 3: Display images with filenames and final score
        display_images(uploaded_filepath, best_image_path, compared_image_path, uploaded_name, reconstructed_name, compared_image_filename, final_score)

def upload_sketch():
    """Allows user to upload a sketch and saves it in temp directory while keeping its original name."""
    global uploaded_filepath, uploaded_filename  #  Store the original filename

    try:
        filepath = filedialog.askopenfilename(
            title="Select Sketch",
            filetypes=(("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp"), ("All files", "*.*"))
        )

        if filepath:
            uploaded_filename = os.path.basename(filepath)  #  Extract the original filename

            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)
            save_path = os.path.join(temp_dir, uploaded_filename)  #  Keep the original filename
            shutil.copy(filepath, save_path)

            display_sketch(save_path)
            uploaded_filepath = save_path
        else:
            print("No file selected")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def display_sketch(filepath):
    """Displays uploaded sketch in UI."""
    try:
        sketch_image = Image.open(filepath).resize((500, 500), Image.LANCZOS)
        photo = ImageTk.PhotoImage(sketch_image)
        uploaded_label.config(image=photo)
        uploaded_label.image = photo
    except Exception as e:
        messagebox.showerror("Error", f"Could not display image: {e}")

def submit_sketch():
    """Handles submission and calls the main processing script."""
    global uploaded_filepath
    if uploaded_filepath:
        messagebox.showinfo("Submission", "Sketch Submitted. Processing..., Will Take 2-3 Mins")
        process_sketch()
    else:
        messagebox.showwarning("Warning", "Please upload a sketch first.")

def open_main_app():
    """Launches the image upload interface after login."""
    global uploaded_label, generated_label, compared_label
    global uploaded_filename_label, generated_filename_label, compared_filename_label

    main_window = tk.Tk()
    main_window.title("Criminal Sketch Upload")
    main_window.state('zoomed')
    main_window.configure(bg="#f0f0f0")

    image_frame = tk.Frame(main_window)
    image_frame.pack(expand=True, fill="both")

    uploaded_frame = tk.Frame(image_frame, bg="white")
    uploaded_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    generated_frame = tk.Frame(image_frame, bg="white")
    generated_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    compared_frame = tk.Frame(image_frame, bg="white")
    compared_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

    uploaded_label = tk.Label(uploaded_frame, bg="white")
    uploaded_label.pack(expand=True, fill="both")

    generated_label = tk.Label(generated_frame, bg="white")
    generated_label.pack(expand=True, fill="both")

    compared_label = tk.Label(compared_frame, bg="white")
    compared_label.pack(expand=True, fill="both")

    #  Add filename labels
    uploaded_filename_label = tk.Label(uploaded_frame, text="Uploaded Sketch", bg="white")
    uploaded_filename_label.pack()

    generated_filename_label = tk.Label(generated_frame, text="Reconstructed Image", bg="white")
    generated_filename_label.pack()

    compared_filename_label = tk.Label(compared_frame, text="Most Similar Image", bg="white")
    compared_filename_label.pack()

    button_frame = tk.Frame(main_window)
    button_frame.pack(pady=10)

    upload_button = tk.Button(button_frame, text="Upload Sketch", command=upload_sketch, bg="#4CAF50", fg="white", padx=20, pady=10)
    submit_button = tk.Button(button_frame, text="Submit Sketch", command=submit_sketch, bg="#008CBA", fg="white", padx=20, pady=10)

    upload_button.pack(side=tk.LEFT, padx=10)
    submit_button.pack(side=tk.LEFT, padx=10)

    main_window.mainloop()

login_window = tk.Tk()
login_window.title("Login")
login_window.state('zoomed')

tk.Label(login_window, text="Username:").pack(pady=5)
username_entry = tk.Entry(login_window)
username_entry.pack(pady=5)

tk.Label(login_window, text="Password:").pack(pady=5)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack(pady=5)

login_button = tk.Button(login_window, text="Login", command=login, bg="#4CAF50", fg="white", padx=20, pady=10)
login_button.pack(pady=20)

login_window.mainloop()
