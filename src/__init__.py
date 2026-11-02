import sys
import os
import logging
from logging.handlers import RotatingFileHandler
import tkinter as tk
import keyring
from tkinter import simpledialog, messagebox

APP_NAME = "PNA"
IS_FROZEN = getattr(sys, 'frozen', False)

def resource_path(relative_path):
    """
    Returns absolute path to a resource, working both in development mode
    and inside a PyInstaller bundled application (via sys._MEIPASS).
    """
    relative_path = os.path.normpath(relative_path)
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# ==============================================================================
# CLIENT ERROR LOGGING CONFIGURATION
# ==============================================================================

def _setup_logger():
    """
    Configures a rotating file logger for error diagnostics and operational tracking.
    """
    logger = logging.getLogger("pna_client")
    logger.setLevel(logging.INFO)

    log_path = None
    if IS_FROZEN:
        exe_dir = os.path.dirname(sys.executable)
        test_path = os.path.join(exe_dir, "error_log.txt")
        try:
            with open(test_path, "a", encoding="utf-8"):
                pass
            log_path = test_path
        except (PermissionError, OSError):
            user_dir = os.path.join(os.path.expanduser("~"), ".pna")
            os.makedirs(user_dir, exist_ok=True)
            log_path = os.path.join(user_dir, "error_log.txt")
    else:
        # Development mode - write logs to client/logs or client/error_log.txt
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        logs_dir = os.path.join(root_dir, "logs")
        try:
            os.makedirs(logs_dir, exist_ok=True)
            log_path = os.path.join(logs_dir, "error_log.txt")
        except Exception:
            log_path = os.path.join(root_dir, "error_log.txt")

    try:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=1024 * 1024,  # 1 MB
            backupCount=5,
            encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s'
        ))
        logger.addHandler(handler)
    except Exception as e:
        print(f"Failed to configure log file ({log_path}): {e}")

    # Additional console handler when running in development mode
    if not IS_FROZEN:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
        logger.addHandler(console_handler)

    logger.info("Initialized PNA client logger.")
    return logger

logger = _setup_logger()


# ==============================================================================
# ENVIRONMENT CONFIGURATION LOADING (.env)
# ==============================================================================

def _parse_env_file(filepath):
    """Parses key-value pairs from a .env file without external dependencies."""
    config = {}
    if not os.path.exists(filepath):
        return config
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    config[key.strip()] = val.strip().strip('"').strip("'")
    except Exception as e:
        logger.warning(f"Error parsing .env file ({filepath}): {e}")
    return config


def load_env_config():
    """
    Retrieves API_URL and API_URL_DEV from candidate .env files with fallback defaults.
    """
    candidate_paths = []
    
    if IS_FROZEN:
        candidate_paths.append(os.path.join(os.path.dirname(sys.executable), ".env"))
        candidate_paths.append(resource_path(".env"))
    else:
        candidate_paths.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
        candidate_paths.append(os.path.join(os.getcwd(), ".env"))
        candidate_paths.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

    env_data = {}
    for path in candidate_paths:
        if os.path.exists(path):
            env_data = _parse_env_file(path)
            if env_data:
                logger.info(f"Loaded configuration from: {path}")
                break

    api_url = env_data.get("API_URL") or os.environ.get("API_URL", "")
    api_url_dev = env_data.get("API_URL_DEV") or os.environ.get("API_URL_DEV", "http://127.0.0.1:5000")

    return api_url.rstrip("/"), api_url_dev.rstrip("/")


API_URL, API_URL_DEV = load_env_config()
SERVER_URL = API_URL
CURRENT_ENV_MODE = "PROD"


def set_server_mode(mode: str):
    """
    Switches client environment mode between 'PROD' and 'DEV'.
    """
    global SERVER_URL, CURRENT_ENV_MODE
    CURRENT_ENV_MODE = mode.upper()
    if CURRENT_ENV_MODE == "DEV":
        SERVER_URL = API_URL_DEV
    else:
        SERVER_URL = API_URL
    logger.info(f"Active environment: {CURRENT_ENV_MODE} ({SERVER_URL})")


def get_api_key(env_mode="PROD", force_ask=False):
    """
    Retrieves the API key from the system keyring.
    In DEV mode, defaults to using the same shared key as PROD unless an override exists.
    """
    api_key = None
    if not force_ask:
        if env_mode == "DEV":
            # For DEV mode, check for a dedicated DEV key first, then fall back to the primary key
            api_key = keyring.get_password(f"{APP_NAME}_DEV", "api_key")
            if not api_key:
                api_key = keyring.get_password(APP_NAME, "api_key")
        else:
            api_key = keyring.get_password(APP_NAME, "api_key")

    if not api_key:
        prompt_label = (
            "Podaj klucz API:" if env_mode == "PROD"
            else "Podaj klucz API dla środowiska DEV\n(taki sam jak w bazie lokalnej / PROD):"
        )
        api_key = simpledialog.askstring("Logowanie", prompt_label, show='*')
        if not api_key:
            messagebox.showerror("Błąd", "Klucz API jest wymagany do działania programu.")
            sys.exit(1)

        service_name = APP_NAME if env_mode == "PROD" else f"{APP_NAME}_DEV"
        try:
            keyring.set_password(service_name, "api_key", api_key)
            # If set in DEV mode and PROD has no key stored, persist to PROD as well for convenience
            if env_mode == "DEV" and not keyring.get_password(APP_NAME, "api_key"):
                keyring.set_password(APP_NAME, "api_key", api_key)
            messagebox.showinfo("Sukces", "Klucz został zapisany.")
        except Exception as e:
            logger.error(f"Failed to store key in keyring: {e}")

    return api_key


def reset_api_key(env_mode="PROD"):
    """Removes stored API key from the keyring for the specified environment."""
    services = [APP_NAME] if env_mode == "PROD" else [f"{APP_NAME}_DEV", APP_NAME]
    for s in services:
        try:
            keyring.delete_password(s, "api_key")
        except Exception:
            pass
