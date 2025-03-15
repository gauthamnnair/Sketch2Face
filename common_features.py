from PIL import Image, ImageTk
import tkinter as tk

def show_banner(path, window):
    """Loads and displays an image stretched to full width without extra space."""
    try:
        # Ensure window is updated to get the correct width
        window.update_idletasks()
        window_width = window.winfo_screenwidth()  # Get full screen width

        # Load and resize the image
        image = Image.open(path)
        image = image.resize((window_width, 200))  # Set width dynamically, height fixed
        photo = ImageTk.PhotoImage(image)

        # Create label with full width, no extra padding
        image_label = tk.Label(window, image=photo)
        image_label.image = photo  # Keep reference
        image_label.pack(side="top", anchor="n", fill="x", pady=0)  # No extra space above
    except Exception as e:
        print(f"Error loading image: {e}")

def add_footer(parent):
    """Adds a footer to the given parent window."""
    footer = tk.Label(parent, text="Copyright © 2025 Third Eye", font=("Arial", 10), fg="green")
    footer.pack(side="bottom", pady=10)
