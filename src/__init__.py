import sys
import os

def resource_path(relative_path):
    relative_path = os.path.normpath(relative_path)    
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)\


import requests
last_known_update = None

def check_for_updates(root_window):
    global last_known_update
    
    try:
        response = requests.get(f"{SERVER_URL}/sync-status", timeout=3)
        if response.status_code == 200:
            server_update_time = response.json().get("last_update")
            
            if last_known_update != server_update_time:
                last_known_update = server_update_time
                
                
    except requests.exceptions.RequestException:
        pass

    root_window.after(5000, lambda: check_for_updates(root_window))



from src.views.main_view import main_window
root = tk.Tk()
check_for_updates(root)
app = main_window(root)
