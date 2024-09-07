import tkinter as tk
from tkinter import messagebox
import sqlite3
import bcrypt
from cryptography.fernet import Fernet
import secrets
import string
import pyperclip
import os

# Function to configure password options
def open_password_config():
    config_window = tk.Toplevel(root)
    config_window.title("Password Configuration")
    config_window.geometry("350x300")
    
    tk.Label(config_window, text="Password Length:").pack(pady=5)
    length_var = tk.IntVar(value=12)
    tk.Spinbox(config_window, from_=8, to_=32, textvariable=length_var, width=5).pack(pady=5)
    
    special_chars_var = tk.BooleanVar(value=True)
    tk.Checkbutton(config_window, text="Include Special Characters", variable=special_chars_var).pack(pady=5)
    
    numbers_var = tk.BooleanVar(value=True)
    tk.Checkbutton(config_window, text="Include Numbers", variable=numbers_var).pack(pady=5)

    uppercase_var = tk.BooleanVar(value=True)
    tk.Checkbutton(config_window, text="Include Uppercase Letters", variable=uppercase_var).pack(pady=5)

    lowercase_var = tk.BooleanVar(value=True)
    tk.Checkbutton(config_window, text="Include Lowercase Letters", variable=lowercase_var).pack(pady=5)
    
    def save_config():
        global password_length, include_special_chars, include_numbers, include_uppercase, include_lowercase
        password_length = length_var.get()
        include_special_chars = special_chars_var.get()
        include_numbers = numbers_var.get()
        include_uppercase = uppercase_var.get()
        include_lowercase = lowercase_var.get()
        config_window.destroy()

    tk.Button(config_window, text="Save", command=save_config).pack(pady=10)

# Function to generate a secure password
def generate_password(length=None):
    global include_special_chars, include_numbers, include_uppercase, include_lowercase
    if length is None:
        length = password_length
    
    characters = ''
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_numbers:
        characters += string.digits
    if include_special_chars:
        characters += string.punctuation
    
    if not characters:
        raise ValueError("No characters available for password generation.")
    
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

# Add password to the database
def add_password():
    name = name_entry.get()
    user_password = user_password_entry.get() if user_password_var.get() else generate_password()
    if name:
        encrypted_password = cipher_suite.encrypt(user_password.encode()).decode('utf-8')
        with conn:
            c.execute("INSERT INTO passwords (name, password) VALUES (?, ?)", (name, encrypted_password))
        name_entry.delete(0, tk.END)
        user_password_entry.delete(0, tk.END)
        show_password(name, user_password)
    else:
        messagebox.showwarning("Input Error", "Please enter a name.")

# Display the generated password
def show_password(name, password):
    def copy_to_clipboard():
        pyperclip.copy(password)
        messagebox.showinfo("Copied", "Password copied to clipboard.")
    
    password_window = tk.Toplevel(root)
    password_window.title("Password Generated")
    tk.Label(password_window, text=f"Password for {name}: {password}").pack(pady=5)
    tk.Button(password_window, text="Copy", command=copy_to_clipboard).pack(pady=10)

# Database connection
conn = sqlite3.connect('passwords.db')
c = conn.cursor()

# Load or generate encryption key
def load_key():
    try:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    return key

key = load_key()
cipher_suite = Fernet(key)

# Main application window
def main_application():
    global name_entry, user_password_entry, user_password_var, root
    
    root = tk.Tk()
    root.title("Secure Password Manager")

    # Password configuration button
    tk.Button(root, text="Password Configuration", command=open_password_config).pack(pady=10)

    # Input for password name
    tk.Label(root, text="Enter a name for the password:").pack(pady=5)
    name_entry = tk.Entry(root, width=50)
    name_entry.pack(pady=5)
    
    user_password_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Enter your own password", variable=user_password_var).pack(pady=5)
    user_password_entry = tk.Entry(root, width=50, show='*')
    user_password_entry.pack(pady=5)

    # Button to generate and store password
    tk.Button(root, text="Generate and Store", command=add_password).pack(pady=10)
    root.mainloop()

# Run the application
main_application()
