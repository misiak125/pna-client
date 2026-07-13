import tkinter as tk
import requests

# Importujemy z naszych modułów
from src import get_api_key, SERVER_URL
from src.views.main_view import main_window
import src.controllers as controllers

def refresh_after_commit(app):
    from src.utils.funcs import refresh_table
    refresh_table(
        app.free_products_tree, app.free_prod_search_entry.get(), app.split_dates.get(), 
        app.customers_tree, app.customers_search_entry.get(), app.reservations_tree, 
        app.reservation_search_entry.get(), app.show_finalized, app.all_products_tree, 
        app.show_sold, app.show_reserved.get(), app.all_prod_search_entry.get(), 
        app.show_year.get(), app.show_year_free.get()
    )

last_known_update = None

def check_for_updates(root_window, app):
    global last_known_update
    
    try:
        # Używamy zaktualizowanych nagłówków z kontrolerów
        response = requests.get(f"{SERVER_URL}/api/sync-status", headers=controllers.HEADERS, timeout=3)
        if response.status_code == 200:
            server_update_time = response.json().get("last_update")
            if last_known_update != server_update_time:
                last_known_update = server_update_time
                refresh_after_commit(app)

                # Aktualizacja list rozwijanych
                app.product_brand_entry["values"] = app.add_model_brand_entry["values"] = controllers.get_brands_list()
                app.product_colour_entry["values"] = controllers.get_colours_list()
                
    except requests.exceptions.RequestException:
        pass

    root_window.after(5000, lambda: check_for_updates(root_window, app))


# ==========================================
# GŁÓWNY START APLIKACJI
# ==========================================
if __name__ == '__main__':
    # 1. Start głównego okna Tkinter
    root = tk.Tk()
    
    # 2. Pobieramy klucz 
    api_key = get_api_key()
    
    # 3. Wstrzykujemy klucz do kontrolerów!
    controllers.HEADERS = {"X-API-Key": api_key}
    
    # 4. Ładujemy widoki
    app = main_window(root)
    
    # 5. PODPINAMY ODŚWIEŻANIE DO KONTROLERÓW! <--- DODAJ TĘ LINIJKĘ
    controllers.refresh_callback = lambda: refresh_after_commit(app)
    
    # 6. Uruchamiamy Smart Polling
    check_for_updates(root, app)
    
    # 7. Główna pętla UI
    root.mainloop()