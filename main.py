import sys
import os
import time
import socket
import threading
import subprocess
import atexit
import tkinter as tk
from tkinter import messagebox

# Import application configuration and modules
import src
from src import get_api_key, resource_path
from src.views.main_view import main_window
import src.controllers as controllers

# Global references to development environment processes
dev_api_proc = None
dev_compose_path = None
dev_api_log_file = None
is_dev_active = False
polling_active = True
last_known_update = None
DEV_CONTAINER_NAME = "dev-mariadb"


def find_docker_bin():
    """
    Locates the 'docker' executable in PATH or standard installation directories (macOS/Linux).
    """
    import shutil
    found = shutil.which("docker")
    if found:
        return found
    candidates = [
        "/usr/local/bin/docker",
        "/opt/homebrew/bin/docker",
        os.path.expanduser("~/.docker/bin/docker"),
        "/usr/bin/docker",
        "/Applications/Docker.app/Contents/Resources/bin/docker",
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return "docker"


def check_docker_daemon(docker_bin):
    """
    Checks whether the Docker daemon (e.g., Docker Desktop) is running and responsive.
    """
    try:
        res = subprocess.run([docker_bin, "info"], capture_output=True, text=True, timeout=4)
        return res.returncode == 0
    except Exception:
        return False


def is_container_running(docker_bin, name=DEV_CONTAINER_NAME):
    """Checks whether the specified container exists and is currently in 'running' state."""
    try:
        res = subprocess.run(
            [docker_bin, "inspect", "-f", "{{.State.Running}}", name],
            capture_output=True,
            text=True,
            timeout=3
        )
        return res.returncode == 0 and res.stdout.strip().lower() == "true"
    except Exception:
        return False


def container_exists(docker_bin, name=DEV_CONTAINER_NAME):
    """Checks whether the specified container exists in the system (running or stopped)."""
    try:
        res = subprocess.run(
            [docker_bin, "inspect", name],
            capture_output=True,
            text=True,
            timeout=3
        )
        return res.returncode == 0
    except Exception:
        return False


def start_dev_container(docker_bin, comp_path, status_callback=None):
    """
    Starts the MariaDB development container:
    - If already running -> skips starting.
    - If exists (stopped) -> runs 'docker start dev-mariadb'.
    - If does not exist -> runs 'docker compose up -d'.
    """
    if is_container_running(docker_bin, DEV_CONTAINER_NAME):
        src.logger.info(f"Container '{DEV_CONTAINER_NAME}' is already running.")
        if status_callback:
            status_callback(f"Container {DEV_CONTAINER_NAME} is already running...")
        return

    if container_exists(docker_bin, DEV_CONTAINER_NAME):
        src.logger.info(f"Container '{DEV_CONTAINER_NAME}' exists — starting via 'docker start'...")
        if status_callback:
            status_callback(f"1/3 Starting container ({DEV_CONTAINER_NAME})...")
        res = subprocess.run([docker_bin, "start", DEV_CONTAINER_NAME], capture_output=True, text=True, timeout=15)
        if res.returncode != 0:
            src.logger.error(f"Error executing docker start {DEV_CONTAINER_NAME}: {res.stderr}")
            raise RuntimeError(f"Failed to start container '{DEV_CONTAINER_NAME}':\n{res.stderr}")
        src.logger.info(f"Container '{DEV_CONTAINER_NAME}' started successfully.")
    else:
        src.logger.info(f"Container '{DEV_CONTAINER_NAME}' does not exist — creating via 'docker compose up -d'...")
        if status_callback:
            status_callback("1/3 Creating MariaDB container (docker compose up)...")
        res = subprocess.run([docker_bin, "compose", "-f", comp_path, "up", "-d"], capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            src.logger.error(f"Error executing docker compose up: {res.stderr}")
            raise RuntimeError(f"Failed to create Docker container:\n{res.stderr}")


def stop_dev_container(docker_bin=None):
    """
    Stops the MariaDB container directly via 'docker stop dev-mariadb'.
    Works reliably regardless of Compose project name.
    """
    if not docker_bin:
        docker_bin = find_docker_bin()
    if is_container_running(docker_bin, DEV_CONTAINER_NAME):
        src.logger.info(f"Stopping Docker container ({DEV_CONTAINER_NAME})...")
        try:
            res = subprocess.run([docker_bin, "stop", "-t", "3", DEV_CONTAINER_NAME], capture_output=True, text=True, timeout=12)
            if res.returncode == 0:
                src.logger.info(f"Container '{DEV_CONTAINER_NAME}' was successfully stopped.")
            else:
                src.logger.warning(f"docker stop warning: {res.stderr.strip()}")
        except Exception as e:
            src.logger.warning(f"Error stopping container {DEV_CONTAINER_NAME}: {e}")
    else:
        src.logger.info(f"Container '{DEV_CONTAINER_NAME}' was not running.")


def setup_exception_handlers(root):
    """
    Configures global uncaught exception handlers for Python and Tkinter callbacks.
    Logs full exception tracebacks to error_log.txt and displays a friendly error box.
    """
    def handle_exception(exc_type, exc_val, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_val, exc_tb)
            return
        src.logger.critical("Uncaught application exception:", exc_info=(exc_type, exc_val, exc_tb))
        try:
            messagebox.showerror(
                "Application Error",
                f"An unexpected error occurred:\n\n{exc_val}\n\nDetails have been logged to error_log.txt."
            )
        except Exception:
            pass

    sys.excepthook = handle_exception
    root.report_callback_exception = handle_exception


def find_dev_paths():
    """
    Locates docker-compose.yml and API directory relative to client or workspace root.
    Supports standard sibling directories like 'pna-api' and 'api'.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(base_dir, ".."))
    cwd = os.getcwd()

    candidate_dirs = [
        os.path.join(parent_dir, "pna-api"),
        os.path.join(parent_dir, "api"),
        os.path.join(cwd, "pna-api"),
        os.path.join(cwd, "api"),
    ]

    for api_dir in candidate_dirs:
        comp_path = os.path.join(api_dir, "docker-compose.yml")
        if os.path.isfile(comp_path) and os.path.isdir(api_dir):
            return os.path.abspath(comp_path), os.path.abspath(api_dir)

    return None, None


def is_port_open(host, port, timeout=1.0):
    """Checks whether a TCP port is open and accepting socket connections."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def is_db_ready(docker_bin, host="127.0.0.1", port=3306):
    """
    Verifies that MariaDB server is fully ready to process incoming SQL queries.
    Checks port connectivity and pings the database server from inside the container.
    """
    if not is_port_open(host, port, timeout=0.8):
        return False

    # Check database engine readiness via admin ping command inside the container
    for admin_cmd in ["mariadb-admin", "mysqladmin"]:
        try:
            res = subprocess.run(
                [docker_bin, "exec", DEV_CONTAINER_NAME, admin_cmd, "ping", "-h", "localhost", "--silent"],
                capture_output=True,
                timeout=2
            )
            if res.returncode == 0:
                return True
        except Exception:
            pass

    # Database engine not ready yet
    return False


def start_local_dev_environment(status_callback=None):
    """
    Starts local development stack: MariaDB container and local Flask API server.
    """
    global dev_api_proc, dev_compose_path, dev_api_log_file, is_dev_active
    comp_path, api_dir = find_dev_paths()
    if not comp_path or not api_dir:
        raise FileNotFoundError("Could not find 'api' directory or 'docker-compose.yml'.")

    dev_compose_path = comp_path
    docker_bin = find_docker_bin()
    src.logger.info(f"Using Docker binary: {docker_bin}")

    # Check whether Docker daemon is active
    if not check_docker_daemon(docker_bin):
        raise RuntimeError(
            "Docker Desktop application is not running.\n"
            "Please start Docker Desktop on your machine and try again."
        )

    # 1/3 Start MariaDB container
    start_dev_container(docker_bin, comp_path, status_callback=status_callback)

    # 2/3 Wait for MariaDB engine readiness
    if status_callback:
        status_callback("2/3 Waiting for database readiness...")
    db_ready = False
    for attempt in range(40):
        if is_db_ready(docker_bin, "127.0.0.1", 3306):
            db_ready = True
            time.sleep(0.5)
            break
        time.sleep(0.5)

    if not db_ready:
        src.logger.warning("Database engine did not report readiness within expected time. Attempting to continue...")

    # 3/3 Launch local Flask API server
    if status_callback:
        status_callback("3/3 Starting local API server...")

    api_venv_python = os.path.join(api_dir, ".venv", "bin", "python")
    if not os.path.exists(api_venv_python) and os.name == "nt":
        api_venv_python = os.path.join(api_dir, ".venv", "Scripts", "python.exe")
    api_python = api_venv_python if os.path.exists(api_venv_python) else sys.executable
    src.logger.info(f"Starting API server: {api_python} -m src.main (cwd: {api_dir})")

    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    dev_api_log_file = open(os.path.join(log_dir, "api_server.log"), "w", encoding="utf-8")

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    dev_api_proc = subprocess.Popen(
        [api_python, "-m", "src.main"],
        cwd=api_dir,
        env=env,
        stdout=dev_api_log_file,
        stderr=dev_api_log_file
    )

    # Wait until API server responds on port 5000
    api_ready = False
    for _ in range(30):
        if is_port_open("127.0.0.1", 5000, timeout=0.5):
            api_ready = True
            break
        time.sleep(0.5)

    if not api_ready:
        try:
            dev_api_log_file.flush()
            with open(os.path.join(log_dir, "api_server.log"), "r", encoding="utf-8") as f:
                api_log_tail = f.read()[-1500:].strip()
        except Exception:
            api_log_tail = "(no log available)"
        src.logger.error(f"API server did not respond on port 5000. Server log:\n{api_log_tail}")
        raise RuntimeError(
            f"API server failed to start within 15 seconds.\n\n"
            f"Server log (last lines):\n{api_log_tail}\n\n"
            f"Check log file: logs/api_server.log"
        )

    # Mark dev environment as active
    is_dev_active = True
    src.logger.info("Local development environment (container + API server) is ready.")


def cleanup_dev_environment():
    """
    Shuts down API server and stops MariaDB container upon application exit.
    Executed only if DEV environment was active.
    """
    global dev_api_proc, dev_api_log_file, is_dev_active, polling_active
    polling_active = False

    if not is_dev_active:
        return

    # 1. Terminate local Flask API server
    if dev_api_proc and dev_api_proc.poll() is None:
        src.logger.info("Stopping local API server...")
        try:
            dev_api_proc.terminate()
            dev_api_proc.wait(timeout=3)
        except Exception:
            try:
                dev_api_proc.kill()
            except Exception:
                pass
        dev_api_proc = None

    if dev_api_log_file and not dev_api_log_file.closed:
        try:
            dev_api_log_file.close()
        except Exception:
            pass
        dev_api_log_file = None

    # 2. Stop Docker container
    stop_dev_container()

    is_dev_active = False
    src.logger.info("Development environment cleanup completed.")

atexit.register(cleanup_dev_environment)


def ask_environment_choice(root):
    """
    Modal dialog prompting user to choose between PROD and DEV (local) environment.
    Only executed in non-frozen/development mode.
    """
    choice = {"mode": None}
    
    dialog = tk.Toplevel(root)
    dialog.title("Select Environment - PNA")
    dialog.geometry("460x270")
    dialog.resizable(False, False)
    
    def on_abort():
        cleanup_dev_environment()
        sys.exit(0)

    dialog.protocol("WM_DELETE_WINDOW", on_abort)
    
    # Center dialog on screen
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 460) // 2
    y = (dialog.winfo_screenheight() - 270) // 2
    dialog.geometry(f"+{x}+{y}")

    lbl = tk.Label(dialog, text="Wybierz środowisko pracy:", font=("Default", 13, "bold"), pady=12)
    lbl.pack()

    desc = tk.Label(
        dialog,
        text="Wybierz, czy chcesz połączyć się z produkcyjnym serwerem,\nczy automatycznie uruchomić lokalny Docker i serwer deweloperski.",
        justify="center",
        padx=15
    )
    desc.pack(pady=(0, 15))

    status_var = tk.StringVar(value="")
    status_label = tk.Label(dialog, textvariable=status_var, fg="#1565C0", font=("Default", 9, "italic"))
    status_label.pack(pady=(0, 10))

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(fill="x", padx=25)

    def select_prod():
        choice["mode"] = "PROD"
        dialog.destroy()

    def select_dev():
        btn_prod.config(state="disabled")
        btn_dev.config(state="disabled")

        def safe_status(msg):
            status_var.set(msg)
            dialog.update()

        try:
            start_local_dev_environment(status_callback=safe_status)
            choice["mode"] = "DEV"
            dialog.destroy()
        except Exception as err:
            src.logger.error(f"Error starting DEV environment: {err}")
            messagebox.showerror(
                "DEV Environment Error",
                f"Failed to start local environment:\n\n{err}\n\nPlease ensure Docker Desktop is running."
            )
            btn_prod.config(state="normal")
            btn_dev.config(state="normal")
            status_var.set("Error starting DEV environment.")

    btn_prod = tk.Button(
        btn_frame, 
        text="PRODUKCJA\n" + src.API_URL, 
        bg="#D32F2F", 
        fg="blue", 
        font=("Default", 10, "bold"), 
        width=21, 
        height=2, 
        command=select_prod
    )
    btn_prod.pack(side="left", padx=5)

    btn_dev = tk.Button(
        btn_frame, 
        text="LOKALNIE\nDocker + Server", 
        bg="#1976D2", 
        fg="blue", 
        font=("Default", 10, "bold"), 
        width=21, 
        height=2, 
        command=select_dev
    )
    btn_dev.pack(side="right", padx=5)

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

    if not choice["mode"]:
        cleanup_dev_environment()
        sys.exit(0)

    return choice["mode"]


# ==============================================================================
# BACKGROUND SMART POLLING (ASYNC / MULTI-THREADING)
# ==============================================================================

def refresh_after_commit(app):
    """Refreshes all UI Treeview tables after data mutations."""
    from src.utils.funcs import refresh_table
    refresh_table(
        app.free_products_tree, app.free_prod_search_entry.get(), app.split_dates.get(), 
        app.customers_tree, app.customers_search_entry.get(), app.reservations_tree, 
        app.reservation_search_entry.get(), app.show_finalized, app.all_products_tree, 
        app.show_sold, app.show_reserved.get(), app.all_prod_search_entry.get(), 
        app.show_year.get(), app.show_year_free.get()
    )


def check_for_updates_worker(root_window, app):
    """
    Worker thread that polls the API for sync timestamps without blocking the Tkinter UI.
    """
    global last_known_update, polling_active
    if not polling_active:
        return

    try:
        url = f"{src.SERVER_URL}/api/sync-status"
        response = controllers.SESSION.get(url, headers=controllers.HEADERS, timeout=4.0)
        if response.status_code == 200:
            data = controllers.safe_json(response, default={})
            server_update_time = data.get("last_update")
            if server_update_time:
                if last_known_update is None:
                    # Set baseline timestamp on first request
                    last_known_update = server_update_time
                elif last_known_update != server_update_time:
                    last_known_update = server_update_time
                    src.logger.info(f"Database update detected (timestamp: {server_update_time}). Refreshing views...")
                    
                    # Schedule Treeviews update on the main Tkinter thread
                    root_window.after(0, lambda: refresh_after_commit(app))

                    # Schedule dropdown menus update on the main Tkinter thread
                    def update_dropdowns():
                        try:
                            controllers.invalidate_cache()
                            brands = controllers.get_brands_list()
                            colours = controllers.get_colours_list()
                            if hasattr(app, 'product_brand_entry') and app.product_brand_entry:
                                app.product_brand_entry["values"] = brands
                            if hasattr(app, 'add_model_brand_entry') and app.add_model_brand_entry:
                                app.add_model_brand_entry["values"] = brands
                            if hasattr(app, 'product_colour_entry') and app.product_colour_entry:
                                app.product_colour_entry["values"] = colours
                        except Exception as dd_err:
                            src.logger.warning(f"Dropdown update error: {dd_err}")

                    root_window.after(0, update_dropdowns)

    except Exception as e:
        src.logger.warning(f"Error in background polling thread: {e}")
    finally:
        # Guarantee scheduling next polling check in 5000 ms
        if polling_active:
            root_window.after(5000, lambda: start_check_for_updates(root_window, app))


def start_check_for_updates(root_window, app):
    """Starts the background update checking thread."""
    if polling_active:
        t = threading.Thread(target=check_for_updates_worker, args=(root_window, app), daemon=True)
        t.start()


# ==============================================================================
# MAIN APPLICATION ENTRY POINT
# ==============================================================================
if __name__ == '__main__':
    # 1. Initialize main Tkinter window
    root = tk.Tk()
    
    # 2. Configure global exception handling
    setup_exception_handlers(root)

    # 3. Prompt for environment mode (DEV / PROD) - only in unfrozen development mode
    env_mode = "PROD"
    if not getattr(sys, 'frozen', False):
        env_mode = ask_environment_choice(root)
    
    src.set_server_mode(env_mode)

    # 4. Retrieve API key for the selected environment
    api_key = get_api_key(env_mode=env_mode)
    
    # 5. Inject headers into controllers
    controllers.HEADERS = {"X-API-Key": api_key}

    # 5b. Verify API key; prompt user to re-enter if rejected (401 Unauthorized)
    while True:
        try:
            test_resp = controllers.SESSION.get(
                f"{src.SERVER_URL}/api/sync-status",
                headers=controllers.HEADERS,
                timeout=4.0
            )
            if test_resp.status_code == 401:
                messagebox.showwarning(
                    "Niepoprawny klucz API",
                    f"Serwer ({env_mode}) odrzucił zapisany klucz API (401 Unauthorized).\nPodaj poprawny klucz do bazy."
                )
                api_key = get_api_key(env_mode=env_mode, force_ask=True)
                controllers.HEADERS = {"X-API-Key": api_key}
                continue
            break
        except Exception:
            # Network or connection issues are handled downstream by controllers
            break
    
    # 6. Initialize UI views
    app = main_window(root)
    
    # 7. Bind automatic refresh callback to controllers
    controllers.refresh_callback = lambda: refresh_after_commit(app)
    
    # 8. Start asynchronous Smart Polling in background
    start_check_for_updates(root, app)
    
    # 9. Handle window close event
    def on_window_close():
        global polling_active
        polling_active = False
        cleanup_dev_environment()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_window_close)

    # 10. Start Tkinter main event loop
    root.mainloop()
