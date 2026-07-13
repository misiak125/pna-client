import sys
import os
import tkinter as tk
import requests
import keyring
from tkinter import simpledialog, messagebox
import json



def resource_path(relative_path):
    relative_path = os.path.normpath(relative_path)    
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def load_api_url():
    """
    Szuka pliku api_url.json i wyciąga z niego adres serwera.
    """
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
        import tkinter as tk
        root = tk.Tk()
        root.withdraw() 
        messagebox.showerror("Błąd krytyczny", f"Nie znaleziono pliku konfiguracyjnego:\n{config_path}")
        sys.exit(1)
        
    except json.JSONDecodeError:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Błąd krytyczny", "Plik api_url.json jest uszkodzony (błąd składni).")
        sys.exit(1)
        
    except Exception as e:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Błąd krytyczny", f"Nie można załadować konfiguracji API:\n{e}")
        sys.exit(1)

SERVER_URL = load_api_url()

APP_NAME = "PNA"

def get_api_key():
    """Pobiera klucz API z systemu."""
    api_key = keyring.get_password(APP_NAME, "api_key")
    
    if not api_key:
        api_key = simpledialog.askstring("Logowanie", "Podaj klucz API:", show='*')
        
        if not api_key:
            messagebox.showerror("Błąd", "Klucz API jest wymagany do działania programu.")
            sys.exit()
            
        keyring.set_password(APP_NAME, "api_key", api_key)
        messagebox.showinfo("Sukces", "Klucz został zapisany.")

    return api_key

HEADERS = {"X-API-Key": get_api_key()}


from src.views.main_view import main_window
root = tk.Tk()
app = main_window(root)

def refresh_after_commit():
    #print("after_commit")
    from src.utils.funcs import refresh_table
    refresh_table(app.free_products_tree, app.free_prod_search_entry.get(), app.split_dates.get(), 
    app.customers_tree, app.customers_search_entry.get(), app.reservations_tree, app.reservation_search_entry.get(), 
    app.show_finalized, app.all_products_tree, app.show_sold, app.show_reserved.get(), app.all_prod_search_entry.get(), 
    app.show_year.get(), app.show_year_free.get())



import requests
last_known_update = None

def check_for_updates(root_window):
    global last_known_update
    
    try:
        response = requests.get(f"{SERVER_URL}/api/sync-status", headers = HEADERS, timeout=3)
        if response.status_code == 200:
            server_update_time = response.json().get("last_update")
            if last_known_update != server_update_time:
                last_known_update = server_update_time
                refresh_after_commit()


                from src.controllers import get_brands_list, get_colours_list
                app.product_brand_entry["values"] = app.add_model_brand_entry["values"] = get_brands_list()
                app.product_colour_entry["values"] = get_colours_list()
                
                
    except requests.exceptions.RequestException:
        pass

    root_window.after(5000, lambda: check_for_updates(root_window))

check_for_updates(root)