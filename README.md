# PNA Client - Fleet and Reservation Management Desktop Application

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter%2FTtk-green.svg)](https://docs.python.org/3/library/tkinter.html)
[![Security](https://img.shields.io/badge/Security-OS%20Keyring-blueviolet.svg)](https://github.com/jaraco/keyring)
[![Packaging](https://img.shields.io/badge/Packaging-PyInstaller-yellowgreen.svg)](https://pyinstaller.org/)

A desktop administration system built for dealership inventory monitoring, customer records, and commercial vehicle reservations.

Designed for production environments across multi-workstation dealerships, the application connects to a central REST API, provides real-time state synchronization across workstations, renders formal reservation PDF confirmation documents, and includes an automated development environment orchestrator that provisions database and server containers on demand.

---

## Origin and Project Evolution

This project is part of a decoupled refactoring of an earlier monolithic system:
- **Predecessor (Full-Stack Monolith):** [motonita-rezerwacje](https://github.com/misiak125/motonita-rezerwacje) - The original full-stack implementation using SQLite.
- **Current Decoupled Architecture:**
  - **Desktop Client:** [pna-client](https://github.com/misiak125/pna-client) - this repository
  - **Backend API:** [pna-api](https://github.com/misiak125/pna-api) - Flask REST API server

---

## Technical Overview


1. Native OS Credential Security:
   The client interfaces directly with the native operating system password manager (**macOS Keychain**, **Windows Credential Manager**, or **Linux SecretService**) via the `keyring` library.

2. Non-blocking Asynchronous Smart Polling:
   To keep multi-user environments synchronized, background threads query a lightweight timestamp endpoint (`/api/sync-status`). Only when a database mutation is detected does the UI trigger a selective refresh.

3. Automated Document Generation (PDFs):
   The client includes a built-in document generation engine built on **ReportLab**. When confirming a reservation, the application formats and saves a formalized PDF agreement complete with customer data, vehicle specifications, pricing terms, and signature spaces. Documents are automatically organized in the user's `Documents/potwierdzenia_rez` directory and opened with the system viewer.

4. Performance Optimizations:
   Engineered for responsive multi-user usage through persistent HTTP connection pooling (`requests.Session` with `HTTPAdapter`), in-memory dictionary caching with event-driven cache invalidation, instant client-side cached search filtering, and state preservation across automatic Treeview refreshes.

5. Automated Local Development Orchestrator:
   When running in development mode, the client inspects host system Docker daemons, starts the MariaDB container, waits for the database engine to become healthy, and launches the local Flask backend as a background process. On exit, all child processes and test containers are cleaned up.

6. Distribution and Deployment Readiness:
   Configured for standalone binary bundling via PyInstaller, including dynamic asset path resolution, application icons, and graceful fallback logging.

---

## Application Navigation Guide

The application interface is organized into tabbed views designed for dealership workflows:

1. Free Vehicles ("Wolne Pojazdy"):
   - Primary operational tab displaying available inventory ready for sale.
   - Filter vehicles by production year, search text, or separate rows by expected delivery batch.
   - Selecting a row and clicking "Zarezerwuj" (or double-clicking) initiates the reservation process for a client.

2. All Vehicles ("Wszystkie Pojazdy"):
   - Comprehensive inventory registry including reserved, sold, and archived vehicles.
   - Toggle visibility checkboxes for sold and reserved stock.
   - Allows vehicle status updates, price changes, and viewing complete vehicle audit histories.

3. Customers ("Klienci"):
   - Customer CRM ledger containing contact details, tax identifiers and other information.
   - Live search bar by customer name, phone number, or company name.
   - Includes full history of transactions associated with each client.

4. Reservations ("Rezerwacje"):
   - Active and completed customer reservations showing deposit values, payment statuses, and notes.
   - **Double-click to View Details:** Double-clicking any reservation row (or clicking "Pokaż szczegóły") opens the comprehensive reservation details dialog showing client contact info, vehicle specs, payment and delivery states, notes, audit trail, and an action to regenerate the PDF confirmation.
   - **Creating a Reservation:** Select any available vehicle in "Wolne Pojazdy" or "Wszystkie Pojazdy" and click "Zarezerwuj". In the modal window, select an existing customer (or click "Nowy klient" to register one on the fly), specify the deposit amount, agreed price, contract form, payment method, and deadlines. Confirming saves the reservation and automatically generates a printable PDF contract.
   - **PDF Generation:** Select any reservation and click "Generuj potwierdzenie" (or access it from the details dialog) to regenerate and display the print-ready contract confirmation PDF.

5. Orders ("Zamówienie"):
   - Intake form for registering incoming inventory or factory orders.

6. Dictionary Management ("Dodaj Pojazd"):
   - Dedicated administrative panel for maintaining system dictionaries.
   - Used specifically to add or remove vehicle Brands, Models (associated with specific brands), and Colours.
   - Modifying entries here immediately updates the dropdown comboboxes across all other forms in the application.

---

## Directory Structure

```text
pna-client/
├── run.py                  # Entrypoint runner script
├── main.py                 # Application lifecycle, local dev orchestrator, and Tkinter root
├── reset_key.py            # Utility to clear stored API credentials from the OS keyring
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment template for server URLs
├── logs/                   # Client rotating diagnostic logs
├── motonita_rezerwacje.spec# PyInstaller build specification
└── src/
    ├── __init__.py         # Configuration loader, OS keyring integration, rotating logger
    ├── controllers.py      # HTTP communication layer
    ├── views/
    │   └── main_view.py    # Primary application GUI
    └── utils/
        ├── buttons.py      # Action handlers, event dispatchers, and dialog workflows
        └── funcs.py        # Formatting utilities, validation, and PDF generator
```

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Docker Desktop (optional, required only if using the automated local DEV mode)

### 1. Environment Setup
From the `pna-client/` directory:
```bash
python3 -m venv .venv
source .venv/bin/activate       # On Linux/macOS
# or: .venv\Scripts\activate    # On Windows

pip install -r requirements.txt
```

### 2. Environment Configuration
Create the local `.env` file:
```bash
cp .env.example .env
```
Default parameters in `.env`:
```env
API_URL=https://your-production-server.com
API_URL_DEV=http://127.0.0.1:5000
```

### 3. Static Assets and Company Details Configuration
The repository includes sample/placeholder assets in `src/static/` so the application runs out of the box without missing-file errors. Before issuing real contracts or generating PDF reservation confirmations in production, fill in your company details in the following files:
- `src/static/seller_details.txt` - Company legal name, tax identifiers (NIP/VAT ID, REGON, KRS).
- `src/static/seller_address.txt` - Physical address / vehicle pickup location printed on agreements.
- `src/static/seller_contact.txt` - Dealership phone numbers, email addresses, and website.
- `src/static/acc_numbers.json` - Bank account names and account numbers available for wire transfers.
- `src/static/header2.jpg` - Letterhead image printed at the top of PDF documents.

### 4. Launching the Application
Execute the client using the launcher script:
```bash
python run.py
```
*(Alternatively: `python main.py`)*.

---

## Step-by-Step Walkthrough for Local Development Environment Setup (also useful as a demo)

1. Ensure `pna-api` and `pna-client` are cloned next to each other in the same directory, and virtual environments with `.env` files are ready for both repositories.
2. Launch the client: `python run.py`.
3. Environment Selection: Select **DEV** in the prompt.
   - If Docker Desktop is active, the client will automatically start the MariaDB container and launch the local API server process.
4. API Authentication: On first run, enter the API key when prompted.
   - You can generate a key from the sibling `pna-api` repository using `python generate_key.py <username>`.
   - The key is securely stored in your OS credential store for future sessions.
5. Interact with the System: Browse active inventory, search through customer accounts, create a reservation, and click "Generuj potwierdzenie" to inspect the generated PDF agreement.

Note: To reset stored credentials, run `python reset_key.py`.

---

## Building Executable with PyInstaller

To bundle the client into a standalone executable using the included PyInstaller specification file (`motonita_rezerwacje.spec`), ensure your virtual environment (`.venv`) is already configured with all project dependencies installed (as described in the Getting Started section) and activated:

1. Install PyInstaller into your active virtual environment:
```bash
pip install pyinstaller
```

2. Run the build command from the `pna-client/` directory:
```bash
pyinstaller motonita_rezerwacje.spec
```

The compiled standalone application and bundled assets will be generated in the `dist/PNA/` directory (from there just run `PNA.exe`). Ensure your target environment contains a valid `.env` file adjacent to the executable or in the user directory if connecting to a custom server.
