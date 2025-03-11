import tkinter as tk
from tkinter import filedialog, messagebox
import json
from PIL import Image, ImageTk
import os
import shutil

JSON_FILE = "criminal_records.json"
IMAGE_DIR = "Kaggle/photos/"

def add_criminal_record(dashboard_window):
    """Opens a full-screen window to add a new criminal record."""

    def save_record():
        """Validates input and saves the record to JSON."""
        name = name_entry.get().strip()
        crime = crime_entry.get().strip()
        image_path = image_entry.get().strip()

        if not name or not crime or not image_path:
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        # Ensure the image directory exists
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)

        # Copy image to Kaggle/photos/ directory
        image_filename = os.path.basename(image_path)
        destination_path = os.path.join(IMAGE_DIR, image_filename)

        try:
            shutil.copy(image_path, destination_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy image: {e}")
            return

        # Load existing records
        try:
            with open(JSON_FILE, "r") as file:
                records = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            records = []

        # Add new record
        new_record = {"name": name, "crime": crime, "photo": image_filename}
        records.append(new_record)

        # Save updated records back to the JSON file
        with open(JSON_FILE, "w") as file:
            json.dump(records, file, indent=4)

        # Show success message
        messagebox.showinfo("Success", "Criminal record added successfully!")

        # Close the add window and return to the dashboard
        add_window.destroy()
        dashboard_window.deiconify()

    def browse_image():
        """Opens file dialog to select an image."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            image_entry.delete(0, tk.END)
            image_entry.insert(0, file_path)

    # Create a full-screen window
    add_window = tk.Toplevel()
    add_window.title("Add Criminal Record")
    add_window.attributes('-fullscreen', True)  # Full-Screen Mode
    add_window.configure(bg="#f0f0f0")

    # Hide the dashboard window while this window is open
    dashboard_window.withdraw()

    # Labels and Entry Fields
    tk.Label(add_window, text="Enter Criminal Details", font=("Arial", 24, "bold"), bg="#f0f0f0").pack(pady=20)

    tk.Label(add_window, text="Name:", font=("Arial", 14), bg="#f0f0f0").pack(pady=5)
    name_entry = tk.Entry(add_window, width=50, font=("Arial", 14))
    name_entry.pack(pady=5)

    tk.Label(add_window, text="Crime:", font=("Arial", 14), bg="#f0f0f0").pack(pady=5)
    crime_entry = tk.Entry(add_window, width=50, font=("Arial", 14))
    crime_entry.pack(pady=5)

    tk.Label(add_window, text="Photo:", font=("Arial", 14), bg="#f0f0f0").pack(pady=5)
    image_frame = tk.Frame(add_window, bg="#f0f0f0")
    image_frame.pack(pady=5)
    
    image_entry = tk.Entry(image_frame, width=40, font=("Arial", 12))
    image_entry.pack(side=tk.LEFT, padx=5)
    
    browse_button = tk.Button(image_frame, text="Browse", command=browse_image, bg="#008CBA", fg="white", font=("Arial", 12))
    browse_button.pack(side=tk.LEFT, padx=5)

    # Save Button
    save_button = tk.Button(add_window, text="Add Record", command=save_record, bg="#4CAF50", fg="white", font=("Arial", 16, "bold"), padx=30, pady=10)
    save_button.pack(pady=30)

    # Exit Button
    exit_button = tk.Button(add_window, text="Cancel", command=lambda: [add_window.destroy(), dashboard_window.deiconify()], bg="red", fg="white", font=("Arial", 14), padx=20, pady=5)
    exit_button.pack(pady=10)

    add_window.mainloop()

def load_records():
    """Loads criminal records from a JSON file."""
    if not os.path.exists(JSON_FILE):
        messagebox.showerror("Error", "Criminal records file not found!")
        return []

    with open(JSON_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format!")
            return []
#'''
def view_records():
    """Opens the View Records window and displays data in a table format with images."""
    records_window = tk.Toplevel()
    records_window.title("View Criminal Records")
    records_window.state('zoomed')  # Full-screen mode
    records_window.configure(bg="#f0f0f0")

    # Set the dimensions of the table_frame as a percentage of the window size
    window_width = records_window.winfo_screenwidth()
    window_height = records_window.winfo_screenheight()

    # Define percentages (for example, 80% of the window width and 80% of the window height)
    table_width_percentage = 0.8  # 80% of the screen width
    table_height_percentage = 0.8  # 80% of the screen height

    table_width = int(window_width * table_width_percentage)
    table_height = int(window_height * table_height_percentage)
    padx = window_width // 4

    # Title Label
    title_label = tk.Label(records_window, text="Criminal Records", font=("Arial", 20, "bold"), bg="#f0f0f0")
    title_label.pack(pady=20)

    table_frame = tk.Frame(records_window, bg="#f0f0f0", width=table_width, height=table_height)
    table_frame.pack(padx=padx, pady=10, fill="both", expand=True)

    canvas = tk.Canvas(table_frame, bg="#f0f0f0")
    scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=canvas.yview, width=20)  # Increased scrollbar width
    scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Load records
    records = load_records()
    images = {}  # Store image references

    # Table Header
    headers = ["No.", "Name", "Face (Photo)", "Crime", "Edit"]
    for col, header in enumerate(headers):
        tk.Label(scrollable_frame, text=header, font=("Arial", 14, "bold"), bg="#ccc", padx=10, pady=5, borderwidth=2, relief="solid").grid(row=0, column=col, sticky="nsew", padx=2, pady=2)

    row_num = 1  # Start from row 1 after the header

    # Insert data
    for index, record in enumerate(records, start=1):
        name = record.get("name", "Unknown")
        crime = record.get("crime", "Unknown")
        photo_filename = record.get("photo", "")

        img_path = os.path.join(IMAGE_DIR, photo_filename)
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((120, 120), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)
            images[index] = img  # Store reference
        else:
            img = None

        # Create 5 rows for each record
        for i in range(5):
            for col in range(5):
                if col == 2:  # Face (Photo) column
                    if img and i == 0:  # Place the image only in the first row
                        tk.Label(scrollable_frame, image=img, bg="#ffffff", borderwidth=1, relief="solid").grid(row=row_num, column=col, rowspan=5, sticky="nsew", padx=2, pady=2)
                elif i == 2:  # Middle row (3rd row) to display data
                    if col == 0:  # No.
                        tk.Label(scrollable_frame, text=str(index), font=("Arial", 12), bg="#ffffff", padx=10, pady=5, borderwidth=1, relief="solid").grid(row=row_num, column=col, sticky="nsew", padx=2, pady=2)
                    elif col == 1:  # Name
                        tk.Label(scrollable_frame, text=name, font=("Arial", 12), bg="#ffffff", padx=10, pady=5, borderwidth=1, relief="solid").grid(row=row_num, column=col, sticky="nsew", padx=2, pady=2)
                    elif col == 3:  # Crime
                        tk.Label(scrollable_frame, text=crime, font=("Arial", 12), bg="#ffffff", padx=10, pady=5, borderwidth=1, relief="solid").grid(row=row_num, column=col, sticky="nsew", padx=2, pady=2)
                    elif col == 4:  # Edit Button
                        edit_button = tk.Button(scrollable_frame, text="Edit", font=("Arial", 12, "bold"), bg="#ffcc00", command=lambda n=name: print(f"Edit {n}"))
                        edit_button.grid(row=row_num, column=col, sticky="nsew", padx=2, pady=2)
                else:  # Empty spaces in rows 1, 2, 4, 5 for alignment
                    if col in [0, 1, 3, 4]:  # No., Name, Crime, Edit columns
                        tk.Label(scrollable_frame, text=" ", bg="#ffffff", borderwidth=1, relief="solid").grid(row=row_num, column=col, sticky="nsew", padx=2, pady=2)

            row_num += 1  # Move to next row

        # Thick Black Separator Line
        tk.Frame(scrollable_frame, height=3, bg="black").grid(row=row_num, column=0, columnspan=5, sticky="ew", padx=5, pady=5)
        row_num += 1  # Move to the next row after the separator

    records_window.mainloop()
'''

def view_records():
    """Opens the View Records window and displays data in a table format with images."""
    records_window = tk.Toplevel()
    records_window.title("View Criminal Records")
    records_window.state('zoomed')  # Full-screen mode
    records_window.configure(bg="#f0f0f0")

    # Use grid layout for records_window instead of pack for the entire window
    records_window.grid_rowconfigure(0, weight=0)  # Title label row does not expand
    records_window.grid_rowconfigure(1, weight=1)  # Table frame row expands
    records_window.grid_columnconfigure(0, weight=1)  # The frame will expand horizontally

    # Title Label
    title_label = tk.Label(records_window, text="Criminal Records", font=("Arial", 20, "bold"), bg="#f0f0f0")
    title_label.grid(row=0, column=0, pady=20, sticky="nsew")

    # Table Frame
    table_frame = tk.Frame(records_window, bg="#f0f0f0")
    table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    # Make sure the table_frame expands in the available space
    records_window.grid_rowconfigure(1, weight=1)
    records_window.grid_columnconfigure(0, weight=1)

    # Create a canvas for scrolling
    canvas = tk.Canvas(table_frame, bg="#f0f0f0")
    scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=canvas.yview, width=20)  # Increased scrollbar width
    scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Load records
    records = load_records()
    images = {}  # Store image references

    # Table Header
    headers = ["No.", "Name", "Face (Photo)", "Crime", "Edit"]
    for col, header in enumerate(headers):
        tk.Label(scrollable_frame, text=header, font=("Arial", 14, "bold"), bg="#ccc", padx=10, pady=5, borderwidth=2, relief="solid").grid(row=0, column=col, sticky="nsew", padx=2, pady=2)

    row_num = 1  # Start from row 1 after the header

    # Insert data
    for index, record in enumerate(records, start=1):
        name = record.get("name", "Unknown")
        crime = record.get("crime", "Unknown")
        photo_filename = record.get("photo", "")

        img_path = os.path.join(IMAGE_DIR, photo_filename)
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((120, 120), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)
            images[index] = img  # Store reference
        else:
            img = None

        # Create rows for each record
        for i in range(5):
            for col in range(5):
                if col == 2:  # Face (Photo) column
                    if img and i == 0:  # Place the image only in the first row
                        tk.Label(scrollable_frame, image=img, bg="#ffffff", borderwidth=1, relief="solid").grid(row=row_num, column=col, rowspan=5, sticky="nsew", padx=2, pady=2)
                elif i == 2:  # Middle row (3rd row) to display data
                    if col == 0:  # No.
                        tk.Label(scrollable_frame, text=str(index), font=("Arial", 12), bg="#ffffff", padx=10, pady=5, borderwidth=1, relief="solid").grid(row=row_num, column=col, sticky="nsew", padx=2, pady=2)
                    elif col == 1:  # Name
                        tk.Label(scrollable_frame, text=name, font=("Arial", 12), bg="#ffffff", padx=10, pady=5, borderwidth=1, relief="solid").grid(row=row_num, column=col, sticky="nsew", padx=2, pady=2)
                    elif col == 3:  # Crime
                        tk.Label(scrollable_frame, text=crime, font=("Arial", 12), bg="#ffffff", padx=10, pady=5, borderwidth=1, relief="solid").grid(row=row_num, column=col, sticky="nsew", padx=2, pady=2)
                    elif col == 4:  # Edit Button
                        edit_button = tk.Button(scrollable_frame, text="Edit", font=("Arial", 12, "bold"), bg="#ffcc00", command=lambda n=name: print(f"Edit {n}"))
                        edit_button.grid(row=row_num, column=col, sticky="nsew", padx=2, pady=2)
                else:  # Empty spaces in rows 1, 2, 4, 5 for alignment
                    if col in [0, 1, 3, 4]:  # No., Name, Crime, Edit columns
                        tk.Label(scrollable_frame, text=" ", bg="#ffffff", borderwidth=1, relief="solid").grid(row=row_num, column=col, sticky="nsew", padx=2, pady=2)

            row_num += 1  # Move to next row

        # Thick Black Separator Line
        tk.Frame(scrollable_frame, height=3, bg="black").grid(row=row_num, column=0, columnspan=5, sticky="ew", padx=5, pady=5)
        row_num += 1  # Move to the next row after the separator

    records_window.mainloop()
'''
