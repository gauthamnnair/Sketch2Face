import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import run_model
import shutil
import subprocess
import logging
import tensorflow as tf
import warnings
from pages import view_records, add_criminal_record
import json
import login as l
import common_features as cmf

uploaded_filepath = None
dashboard_window = None  # Ensure global reference

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

def open_dashboard():
    """Opens the main dashboard window."""
    global dashboard_window

    if dashboard_window and dashboard_window.winfo_exists():
        dashboard_window.lift()
        return

    dashboard_window = tk.Tk()
    dashboard_window.title("Dashboard")
    dashboard_window.state('zoomed')
    dashboard_window.configure(bg="black")

    cmf.show_banner("static/banner.jpg", dashboard_window)

    tk.Label(dashboard_window, text="Dashboard", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=20)

    button_frame = tk.Frame(dashboard_window, bg="black")
    button_frame.pack(pady=50)

    add_record_button = tk.Button(button_frame, text="Add Criminal Record", command=lambda: add_criminal_record(dashboard_window), bg="#4CAF50", fg="white", padx=20, pady=10)
    view_records_button = tk.Button(button_frame, text="View Records", command=view_records, bg="blue", fg="white", padx=20, pady=10)
    draw_faces_button = tk.Button(button_frame, text="Draw Faces", command=draw_faces, bg="#4CAF50", fg="white", padx=20, pady=10)

    add_record_button.pack(side=tk.LEFT, padx=20)
    view_records_button.pack(side=tk.LEFT, padx=20)
    draw_faces_button.pack(side=tk.LEFT, padx=20)

    dashboard_window.mainloop()

def upload_sketch():
    """Allows user to upload a sketch and saves it in temp directory while keeping its original name."""
    global uploaded_filepath, uploaded_filename, generate_button

    try:
        filepath = filedialog.askopenfilename(
            title="Select Sketch",
            filetypes=(("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp"), ("All files", "*.*"))
        )

        if filepath:
            uploaded_filename = os.path.basename(filepath)  # Extract the original filename
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)
            save_path = os.path.join(temp_dir, uploaded_filename)  # Keep the original filename
            shutil.copy(filepath, save_path)

            display_sketch(save_path)
            uploaded_filepath = save_path
            
            # Show generate button in the second square
            if generate_button:
                generate_button.pack()

        else:
            print("No file selected")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def download_image(image_path):
    """Saves the generated image to the download_reconstructed directory."""
    download_dir = "download_reconstructed"
    os.makedirs(download_dir, exist_ok=True)
    destination = os.path.join(download_dir, os.path.basename(image_path))
    shutil.copy(image_path, destination)
    messagebox.showinfo("Download Complete", f"Image saved to {destination}")
        
def display_sketch(filepath):
    """Displays uploaded sketch in UI."""
    try:
        sketch_image = Image.open(filepath).resize((500, 500), Image.LANCZOS)
        photo = ImageTk.PhotoImage(sketch_image)
        uploaded_label.config(image=photo)
        uploaded_label.image = photo
    except Exception as e:
        messagebox.showerror("Error", f"Could not display image: {e}")

def display_generated_image(image_path):
    """Displays the generated image in the middle frame."""
    global generated_label

    img = Image.open(image_path)
    img = img.resize((300, 300))  # Adjust size as needed
    img = ImageTk.PhotoImage(img)

    generated_label.config(image=img)
    generated_label.image = img  # Keep a reference to prevent garbage collection

def submit_sketch():
    """Runs the model to generate the reconstructed image and replaces Generate with Download."""
    global generate_button, download_button

    reconstructed_image_path = run_model.generate_best_reconstruction(uploaded_filepath)
    display_generated_image(reconstructed_image_path)

    # Hide generate button
    if generate_button:
        generate_button.pack_forget()
    
    # Show download button
    download_button = tk.Button(generated_frame, text="Download", command=lambda: download_image(reconstructed_image_path), bg="#FFA500", fg="white", padx=20, pady=10)
    download_button.pack()
    process_sketch()

def check_criminal_records(image_path, score):
    """Checks if the generated image matches any criminal records and displays the results."""
    try:
        with open("criminal_records.json", "r") as file:
            records = json.load(file)

        matched_records = []
        for record in records:
            if record["photo"] == os.path.basename(image_path):  # Placeholder condition
                matched_records.append(record)
        
        display_criminal_records(matched_records, score)
    except Exception as e:
        print(f"Error checking criminal records: {e}")

def display_criminal_records(records, score):
    """Displays matched criminal records in a table format below the images."""
    if records:
        table_frame = tk.Frame(draw_faces_window, bg="white")
        table_frame.pack(fill="x", pady=10)

        # Creating Table Headers
        headers = ["No.", "Name", "Crime", "Match Accuracy"]
        for col, header_text in enumerate(headers):
            header_label = tk.Label(table_frame, text=header_text, font=("Arial", 12, "bold"), bg="white", borderwidth=1, relief="solid", padx=10, pady=5)
            header_label.grid(row=0, column=col, sticky="nsew", padx=2, pady=2)

        # Populating Rows
        for i, record in enumerate(records, start=1):
            values = [i, record['name'], record['crime'], f"{score}%"]
            for col, value in enumerate(values):
                cell_label = tk.Label(table_frame, text=value, font=("Arial", 10), bg="white", borderwidth=1, relief="solid", padx=10, pady=5)
                cell_label.grid(row=i, column=col, sticky="nsew", padx=2, pady=2)

        # Make columns stretchable
        for col in range(len(headers)):
            table_frame.columnconfigure(col, weight=1)

    else:
        print("No matching criminal records found.")
    
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
            check_criminal_records(compared_image_filename, final_score)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to compare images: {e}")
            return

        # Step 3: Display images with filenames and final score
        display_images(uploaded_filepath, best_image_path, compared_image_path, uploaded_name, reconstructed_name, compared_image_filename, final_score)

def draw_faces():
    """Launches the Draw Faces interface and closes the dashboard."""
    global draw_faces_window, dashboard_window
    global uploaded_label, generated_label, compared_label
    global uploaded_filename_label, generated_filename_label, compared_filename_label
    global generate_button, generated_frame  # Make generated_frame global

    if 'dashboard_window' in globals() and dashboard_window.winfo_exists():
        dashboard_window.destroy()  # Close Dashboard

    draw_faces_window = tk.Tk()  # Create new main window
    draw_faces_window.title("Criminal Sketch Upload")
    draw_faces_window.state('zoomed')
    draw_faces_window.configure(bg="#f0f0f0")

    # Image frames
    image_frame = tk.Frame(draw_faces_window)
    image_frame.pack(expand=True, fill="both")
    #Added
    image_frame.grid_columnconfigure(0, weight=1)
    image_frame.grid_columnconfigure(1, weight=1)
    image_frame.grid_columnconfigure(2, weight=1)
    image_frame.grid_rowconfigure(0, weight=7)
    image_frame.grid_rowconfigure(1, weight=3)

    uploaded_frame = tk.Frame(image_frame, bg="white")
    uploaded_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    generated_frame = tk.Frame(image_frame, bg="white")  # Now it's global
    generated_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    compared_frame = tk.Frame(image_frame, bg="white")
    compared_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

    uploaded_label = tk.Label(uploaded_frame, bg="white", text="Upload Sketch Here", font=("Arial", 12))
    uploaded_label.pack(expand=True, fill="both")
    generated_label = tk.Label(generated_frame, bg="white", text="Reconstructed Image", font=("Arial", 12))
    generated_label.pack(expand=True, fill="both")
    compared_label = tk.Label(compared_frame, bg="white", text="Most Similar Image", font=("Arial", 12))
    compared_label.pack(expand=True, fill="both")

    uploaded_filename_label = tk.Label(uploaded_frame, text="Uploaded Sketch", bg="white")
    uploaded_filename_label.pack()
    generated_filename_label = tk.Label(generated_frame, text="Reconstructed Image", bg="white")
    generated_filename_label.pack()
    compared_filename_label = tk.Label(compared_frame, text="Most Similar Image", bg="white")
    compared_filename_label.pack()

    # Upload button inside the leftmost square
    upload_button = tk.Button(uploaded_frame, text="Upload Sketch", command=upload_sketch, bg="#4CAF50", fg="white", padx=20, pady=10)
    upload_button.pack()

    # Generate button inside the middle square (hidden initially)
    generate_button = tk.Button(generated_frame, text="Generate", command=submit_sketch, bg="#4CAF50", fg="white", padx=20, pady=10)
    generate_button.pack()
    generate_button.pack_forget()  # Hide initially

    draw_faces_window.protocol("WM_DELETE_WINDOW", return_to_dashboard)
    
def return_to_dashboard():
    """Closes the Draw Faces window and reopens the Dashboard."""
    global draw_faces_window
    if 'draw_faces_window' in globals() and draw_faces_window.winfo_exists():
        draw_faces_window.destroy()
    open_dashboard()  # Reopen the Dashboard

def close_draw_faces():
    """Closes the draw faces window safely."""
    global draw_faces_window
    if 'draw_faces_window' in globals() and draw_faces_window.winfo_exists():
        draw_faces_window.destroy()
        del draw_faces_window

# Register the function in login.py
l.set_notify_callback(open_dashboard)

l.show_login_page()
