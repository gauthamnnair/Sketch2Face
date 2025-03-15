import tkinter as tk
from tkinter import messagebox
import sqlite3
import bcrypt
import random
import common_features as cmf

# Database setup
DB_FILE = "users.db"

def setup_database():
    """Creates the users table if it does not exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_placeholder(entry, text):
    """Adds a placeholder inside an entry field."""
    entry.insert(0, text)
    entry.config(fg="gray")

    def on_focus_in(event):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, text)
            entry.config(fg="gray")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def add_password_placeholder(entry, text):
    """Adds a placeholder for the password field, switching to '*' when typing."""
    entry.insert(0, text)
    entry.config(fg="gray", show="")  # Show placeholder text normally

    def on_focus_in(event):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg="black", show="*")  # Mask input when typing

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, text)
            entry.config(fg="gray", show="")  # Show placeholder text again

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def register_user():
    """Registers a new user with a hashed password."""
    username = signup_username_entry.get().strip()
    password = signup_password_entry.get()

    if username == "Enter Username" or password == "Enter Password":
        messagebox.showerror("Error", "Username and password cannot be empty!")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if username already exists
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        messagebox.showerror("Error", "Username already exists! Try a different one.")
        return

    # Hash password and insert user
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "User registered successfully! You can now log in.")
    show_login_page()  # Switch back to login after successful registration

def verify_login(username, password):
    """Verifies user login by checking the hashed password."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result and bcrypt.checkpw(password.encode(), result[0]):  # Remove `.encode()`
        return True
    return False

notify_main = None  # Placeholder function, set from main.py

def handle_login():
    """Handles login and notifies main.py"""
    if login():
         if notify_main:
            notify_main()

def set_notify_callback(callback):
    """Allows main.py to register a callback for successful login"""
    global notify_main
    notify_main = callback

def login():
    """Handles user login and returns True if successful."""
    username = username_entry.get().strip()
    password = password_entry.get()

    if username == "Enter Username" or password == "Enter Password":
        messagebox.showerror("Login Failed", "Please enter your credentials.")
        return False

    if verify_login(username, password):
        messagebox.showinfo("Login Successful", "Welcome to the Criminal Records System!")
        login_window.destroy()

        if notify_main:  # Call open_dashboard() if it's set
            notify_main()
        return True
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")
        return False
    
def show_signup_page():
    """Switches to the signup page by destroying the login window."""
    global signup_window, signup_username_entry, signup_password_entry

    login_window.destroy()  # Close login window before opening signup

    signup_window = tk.Tk()
    signup_window.title("Signup")
    signup_window.state("zoomed")

    cmf.show_banner("static/banner.jpg", signup_window)

    # Outer frame to create a colored border effect
    outer_frame = tk.Frame(signup_window, bg="blue", padx=3, pady=3)
    outer_frame.pack(padx=10, pady=10, fill="both", expand=True)  # Fill and expand

    # Inner frame (actual form container with a solid border)
    border_frame = tk.Frame(outer_frame, relief="solid", bd=2, padx=50, pady=20, bg="white")
    border_frame.pack(pady=50)  # Centered inside outer_frame

    tk.Label(border_frame, text="Signup", font=("Arial", 16, "bold")).pack(pady=10)

    signup_username_entry = tk.Entry(border_frame, width=50)
    signup_username_entry.pack(padx=10, pady=10, ipady=3)
    add_placeholder(signup_username_entry, "Username")

    signup_password_entry = tk.Entry(border_frame, width=50)
    signup_password_entry.pack(padx=10, pady=10, ipady=3)
    add_password_placeholder(signup_password_entry, "Password")

    signup_button = tk.Button(border_frame, text="Signup", command=register_user, bg="#2196F3", fg="white", padx=20, pady=10)
    signup_button.pack(pady=10)

    # "Already a Member? Login" text link
    login_frame = tk.Frame(border_frame)
    login_frame.pack(pady=20)

    tk.Label(login_frame, text="Already a Member?", font=("Arial", 10)).pack(side=tk.LEFT)

    login_link = tk.Label(login_frame, text="Login", font=("Arial", 10, "underline"), fg="blue", cursor="hand2")
    login_link.pack(side=tk.LEFT)
    login_link.bind("<Button-1>", lambda e: show_login_page())
    cmf.add_footer(signup_window)
    
    signup_window.mainloop()


def show_login_page():
    """Switches back to the login page by destroying the signup window."""
    global login_window, username_entry, password_entry

    try:
        signup_window.destroy()  # Close signup window if open
    except NameError:
        pass  # Ignore if it doesn't exist

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.state("zoomed")

    cmf.show_banner("static/banner.jpg", login_window)

    # Outer frame to create a colored border effect
    outer_frame = tk.Frame(login_window, bg="blue", padx=3, pady=3)
    outer_frame.pack(padx=10, pady=10, fill="both", expand = True)  # Fill and expand

    # Inner frame (actual form container with a solid border)
    border_frame = tk.Frame(outer_frame, relief="solid", bd=2, padx=50, pady=20, bg="white")
    border_frame.pack(pady=50)  # Centered inside outer_frame

    tk.Label(border_frame, text="Login", font=("Arial", 16, "bold")).pack(pady=10)

    username_entry = tk.Entry(border_frame, width=50)
    username_entry.pack(padx=10, pady=10, ipady=3)
    add_placeholder(username_entry, "Username")

    password_entry = tk.Entry(border_frame, width=50)
    password_entry.pack(padx=10, pady=10, ipady=3)
    add_password_placeholder(password_entry, "Password")

    login_button = tk.Button(border_frame, text="Login", command=lambda: handle_login(), bg="#4CAF50", fg="white", padx=20, pady=10)
    login_button.pack(pady=10)

    # "Not a Member Yet? Register Now" text link
    register_frame = tk.Frame(border_frame)
    register_frame.pack(pady=10)

    tk.Label(register_frame, text="Not a member yet?", font=("Arial", 10)).pack(side=tk.LEFT)

    register_link = tk.Label(register_frame, text="Register Now", font=("Arial", 10, "underline"), fg="blue", cursor="hand2")
    register_link.pack(side=tk.LEFT)
    register_link.bind("<Button-1>", lambda e: show_signup_page())
    cmf.add_footer(login_window)

    login_window.mainloop()

# Initialize the database
setup_database()

# Start with the login page
#show_login_page()
