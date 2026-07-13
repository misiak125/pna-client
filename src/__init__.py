import sys
import os
import tkinter as tk
import keyring
from tkinter import simpledialog, messagebox
import json

def resource_path(relative_path):
    relative_path = os.path.normpath(relative_path)    
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def load_api_url():
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
    config_path = os.path.join(resource_path(os.path.join('static', 'api_url.json')))
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
            api_url = config.get("API_URL")
            if not api_url:
                raise ValueError("Brak klucza 'API_URL' w pliku konfiguracyjnym.")
            return api_url
            
    except FileNotFoundError:
        root = tk.Tk()
        root.withdraw() 
        messagebox.showerror("Błąd krytyczny", f"Nie znaleziono pliku konfiguracyjnego:\n{config_path}")
        sys.exit(1)
        
    except json.JSONDecodeError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Błąd krytyczny", "Plik api_url.json jest uszkodzony (błąd składni).")
        sys.exit(1)
        
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Błąd krytyczny", f"Nie można załadować konfiguracji API:\n{e}")
        sys.exit(1)

SERVER_URL = load_api_url()
APP_NAME = "PNA"

def get_api_key():
    """Pobiera klucz API z systemu (wywoływane dopiero przy starcie w main.py)."""
    api_key = keyring.get_password(APP_NAME, "api_key")
    
    if not api_key:
        api_key = simpledialog.askstring("Logowanie", "Podaj klucz API:", show='*')
        if not api_key:
            messagebox.showerror("Błąd", "Klucz API jest wymagany do działania programu.")
            sys.exit()
            
        keyring.set_password(APP_NAME, "api_key", api_key)
        messagebox.showinfo("Sukces", "Klucz został zapisany.")

    return api_key