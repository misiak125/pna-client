import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import os
import time
from tkinter import messagebox
from urllib.parse import urlparse
import src

# Persistent HTTP session with connection pooling for low-bandwidth optimization
SESSION = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=Retry(total=1, backoff_factor=0.3))
SESSION.mount("http://", adapter)
SESSION.mount("https://", adapter)

HEADERS = {}
refresh_callback = None

# Simple in-memory cache for rarely changing dictionaries
_cached_brands = None
_cached_colours = None

def invalidate_cache():
    """Clears in-memory caches for brands and colours."""
    global _cached_brands, _cached_colours
    _cached_brands = None
    _cached_colours = None

class MockObj:
    """Mock object allowing attribute assignment via dot notation (emulates SQLAlchemy model instances)."""
    pass

def _format_date_for_server(date_obj):
    """Helper function formatting Tkinter/datetime date to full ISO timestamp string."""
    if not date_obj:
        return None
        
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime("%Y-%m-%dT00:00:00")

    date_str = str(date_obj)
    if "T" not in date_str:
        return date_str + "T00:00:00"
    return date_str


def safe_json(response, default=None):
    """
    Safely decodes JSON from a requests Response object.
    Prevents unhandled crashes on empty responses, 502/504 HTML errors, or server cold boots.
    """
    if response is None:
        return default
    try:
        return response.json()
    except Exception as e:
        raw_text = getattr(response, 'text', '')
        src.logger.error(f"[JSON DECODE ERROR] Failed to decode JSON response: {e}. Body (first 200 chars): {raw_text[:200]}")
        return default


# --- MAIN HTTP REQUEST & ERROR HANDLER ---
def _safe_request(method, endpoint, silent=False, retries=3, **kwargs):
    """
    Dispatches an HTTP request and handles exceptions.
    For GET requests, implements automatic retries on network instability.
    :param silent: If True, suppresses GUI error popups.
    """
    url = f"{src.SERVER_URL}{endpoint}"
    last_exception = None

    # Mutating requests (POST/PUT/DELETE) should not be blindly repeated automatically
    max_attempts = retries if method.upper() == "GET" else 1

    for attempt in range(max_attempts):
        try:
            response = SESSION.request(method, url, headers=HEADERS, timeout=(4.0, 10.0), **kwargs)
           
            if response.status_code in (200, 201):
                return response
                
            # Error responses from API 
            error_msg = f"Server returned status code {response.status_code}"
            try:
                res_data = response.json()
                if isinstance(res_data, dict):
                    error_msg = res_data.get("error") or res_data.get("message") or error_msg
            except Exception:
                if response.text:
                    error_msg = response.text[:200]

            src.logger.warning(f"[API ERROR {response.status_code}] {method} {endpoint}: {error_msg}")

            if not silent:
                messagebox.showerror("Server Error", f"Server rejected request ({response.status_code}):\n\n{error_msg}")
            else:
                src.logger.error(f"[POLLING ERROR] {error_msg}")

            raise ValueError(f"API Request Failed ({response.status_code}): {error_msg}")

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exception = e
            src.logger.warning(f"[HTTP RETRY {attempt+1}/{max_attempts}] Connection error on {method} {endpoint}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(0.5 * (attempt + 1))
                continue
        except requests.exceptions.RequestException as e:
            last_exception = e
            break

    src.logger.error(f"[HTTP CONNECTION FAILED] {method} {endpoint}: {last_exception}")
    if not silent:
        messagebox.showerror(
            "Connection Error", 
            f"No connection to API server.\nPlease check your Internet access or ensure the server is running.\n\nDetails:\n{last_exception}"
        )
    else:
        src.logger.error(f"[POLLING ERROR] Connection to server failed: {last_exception}")

    raise ConnectionError("No connection to API") from last_exception


""" ============================================================================
    1. GET - DATA RETRIEVAL
============================================================================ """

def get_free_products():
    """Fetches non-reserved, unsold products grouped by specs without splitting dates."""
    res = _safe_request("GET", "/api/products/free")
    data = safe_json(res, default=[])
    
    results = []
    for d in data:
        row = MockObj()
        row.Product = MockObj()
        row.Product.brand = d.get('brand', '')
        row.Product.model = d.get('model', '')
        row.Product.year = d.get('year')
        row.Product.colour = d.get('colour', '')
        row.Product.first_id = d.get('first_free_id')
        row.Product.id = d.get('first_free_id')
        row.max = d.get('price')
        row.count = d.get('count', 0)
        deliv = d.get('delivery')
        row.expected_deliveryy = datetime.strptime(deliv, '%d.%m.%Y') if deliv else None
        
        results.append(row)
    return results

def get_free_products_split():
    res = _safe_request("GET", "/api/products/free?split_dates=true")
    data = safe_json(res, default=[])
    
    results = []
    for d in data:
        row = MockObj()
        row.Product = MockObj()
        row.Product.brand = d.get('brand', '')
        row.Product.model = d.get('model', '')
        row.Product.year = d.get('year')
        row.Product.colour = d.get('colour', '')
        row.Product.first_id = d.get('first_free_id')
        row.Product.id = d.get('first_free_id')
        row.max = d.get('price')
        row.count = d.get('count', 0)
        deliv = d.get('delivery')
        row.expected_deliveryy = datetime.strptime(deliv, '%d.%m.%Y') if deliv else None
        
        results.append(row)
    return results

def get_all_customers():
    res = _safe_request("GET", "/api/customers")
    data = safe_json(res, default=[])
    
    results = []
    for c in data:
        row = MockObj()
        row.id = c.get('id')
        row.name = c.get('name', '')
        row.phone = c.get('phone', '')
        row.email = c.get('email', '')
        row.pesel = c.get('pesel', '')
        row.nip = c.get('nip', '')
        row.adress = c.get('adress', '')
        row.company_name = c.get('company_name', '')
        added_str = c.get('added_on')
        row.added_on = datetime.strptime(added_str, '%d-%m-%Y %H:%M') if added_str else datetime.now()
        results.append(row)
    return results

def get_full_reservations():
    return _fetch_reservations(show_finalized=False)

def get_full_old_reservations():
    return _fetch_reservations(show_finalized=True)

def _fetch_reservations(show_finalized):
    url = f"/api/reservations?show_finalized={'true' if show_finalized else 'false'}"
    res = _safe_request("GET", url)
    data = safe_json(res, default=[])
    
    results = []
    for r in data:
        row = MockObj()
        row.Reservation = MockObj()
        row.Customer = MockObj()
        row.Product = MockObj()
        
        row.Reservation.id = r.get('reservation_id')
        row.Reservation.string_order_id = r.get('order_id', '')
        row.Reservation.adnotation = r.get('adnotation', '')
        row.Reservation.paid = r.get('paid', False)
        date_str = r.get('date')
        row.Reservation.date = datetime.strptime(date_str, '%d-%m-%Y %H:%M') if date_str else datetime.now()
        
        row.Customer.name = r.get('customer_name', '')
        row.Product.brand = r.get('brand', '')
        row.Product.model = r.get('model', '')
        row.Product.colour = r.get('colour', '')
        
        results.append(row)
    return results

def get_all_products():
    return _fetch_all_products(show_sold=False)

def get_all_old_products():
    return _fetch_all_products(show_sold=True)

def _fetch_all_products(show_sold):
    url = f"/api/products/all?show_sold={'true' if show_sold else 'false'}"
    res = _safe_request("GET", url)
    data = safe_json(res, default=[])
    
    results = []
    for p in data:
        row = MockObj()
        row.Product = MockObj()
        
        row.Product.id = p.get('id')
        row.Product.brand = p.get('brand', '')
        row.Product.model = p.get('model', '')
        row.Product.year = p.get('year')
        row.Product.colour = p.get('colour', '')
        row.Product.price = p.get('price')
        row.Product.state = p.get('state', '')
        row.Product.order_id = p.get('order_id', '')
        added_str = p.get('added_on')
        row.Product.added_on = datetime.strptime(added_str, '%d-%m-%Y %H:%M') if added_str else datetime.now()
        deliv_str = p.get('delivery')
        row.Product.expected_delivery = datetime.strptime(deliv_str, '%d.%m.%Y') if deliv_str else None
        
        row.Reservation = MockObj() if p.get('is_reserved') == "TAK" else None
        results.append(row)
    return results

# ----- SINGLE DATABASE OBJECTS -----

def get_product(id_given):
    """Retrieves full product record by ID."""
    res = _safe_request("GET", f"/api/products/{id_given}")
    d = safe_json(res, default=None)
    if not d: return None
    
    row = MockObj()
    row.id = d.get('id')
    row.brand = d.get('brand', '')
    row.model = d.get('model', '')
    row.colour = d.get('colour', '')
    row.year = d.get('year')
    row.price = d.get('price')
    row.old_price = d.get('old_price')
    row.state = d.get('state', '')
    row.order_id = d.get('order_id', '')
    exp_str = d.get('expected_delivery')
    row.expected_delivery = datetime.strptime(exp_str[:10], '%Y-%m-%d') if exp_str else None
    row.history = d.get('history', '')
    return row

def get_customer(id_given):
    """Retrieves full customer record by ID."""
    res = _safe_request("GET", f"/api/customers/{id_given}")
    c = safe_json(res, default=None)
    if not c: return None
    
    row = MockObj()
    row.id = c.get('id')
    row.name = c.get('name', '')
    row.phone = c.get('phone', '')
    row.email = c.get('email', '')
    row.pesel = c.get('pesel', '')
    row.nip = c.get('nip', '')
    row.company_name = c.get('company_name', '')
    row.adress = c.get('adress', '')
    row.history = c.get('history', '')
    return row

def get_full_reservation(id_given):
    """Retrieves composite reservation object including product and customer data."""
    res = _safe_request("GET", f"/api/reservations/{id_given}")
    d = safe_json(res, default=None)
    if not d: return None
    
    row = MockObj()
    row.Reservation = MockObj()
    row.Product = MockObj()
    row.Customer = MockObj()
    
    r = d.get("reservation", {})
    p = d.get("product", {})
    c = d.get("customer", {})
    
    row.Reservation.id = r.get('id')
    row.Reservation.advance = r.get('advance')
    row.Reservation.adnotation = r.get('adnotation', '')
    row.Reservation.adnotation_pub = r.get('adnotation_pub', '')
    row.Reservation.form = r.get('form')
    row.Reservation.paid = r.get('paid', False)
    row.Reservation.term = r.get('term', '')
    row.Reservation.delivery = r.get('delivery', False)
    row.Reservation.payment_method = r.get('payment_method', '')
    row.Reservation.string_order_id = r.get('string_order_id', '')
    date_str = r.get('date')
    row.Reservation.date = datetime.strptime(date_str[:19], '%Y-%m-%dT%H:%M:%S') if date_str else None
    row.Reservation.history = r.get('history', '')
    
    # --- Product details ---
    row.Product.id = p.get('id')
    row.Product.brand = p.get('brand', '')
    row.Product.model = p.get('model', '')
    row.Product.colour = p.get('colour', '')
    row.Product.year = p.get('year')
    row.Product.price = p.get('price')
    row.Product.old_price = p.get('old_price')
    row.Product.state = p.get('state', '')
    row.Product.order_id = p.get('order_id', '')
    exp_str = p.get('expected_delivery')
    row.Product.expected_delivery = datetime.strptime(exp_str[:10], '%Y-%m-%d') if exp_str else None
    row.Product.history = p.get('history', '')
    
    # --- Customer details ---
    row.Customer.id = c.get('id')
    row.Customer.name = c.get('name', '')
    row.Customer.phone = c.get('phone', '')
    row.Customer.email = c.get('email', '')
    row.Customer.pesel = c.get('pesel', '')
    row.Customer.nip = c.get('nip', '')
    row.Customer.adress = c.get('adress', '')
    row.Customer.company_name = c.get('company_name', '')
    row.Customer.history = c.get('history', '')
    
    return row

get_reservation = get_full_reservation

def do_customer_have_reservations(id_given):
    """Checks whether the specified customer has active or past reservations."""
    res = _safe_request("GET", f"/api/customers/{id_given}/has_reservations")
    data = safe_json(res, default={})
    return data.get("is_reserved", False)

def get_first_free_element(brand_given, model_given, colour_given, year_given, delivery_given):
    """Retrieves the first available unreserved product ID matching specifications."""
    params = {
        "brand": brand_given,
        "model": model_given,
        "colour": colour_given,
        "year": year_given,
        "delivery": delivery_given
    }
    res = _safe_request("GET", "/api/products/first_free", params=params)
    d = safe_json(res, default=None)
    if not d: return None
    
    row = MockObj()
    row.id = d.get('id')
    row.price = d.get('price')
    return row

def get_last_reservation():
    """Retrieves the most recent reservation record."""
    res = _safe_request("GET", "/api/reservations/last")
    d = safe_json(res, default=None)
    if not d: return None
    row = MockObj()
    row.id = d.get('id')
    row.string_order_id = d.get('string_order_id')
    return row

def get_new_order_id():
    """Fetches next auto-incrementing order ID sequence from API."""
    res = _safe_request("GET", "/api/reservations/next_id")
    data = safe_json(res, default={})
    return data.get("next_id", 1)


# ----- CACHED LOOKUP DICTIONARIES -----

def get_colours_list():
    """Fetches list of vehicle colours with local in-memory caching."""
    global _cached_colours
    if _cached_colours is not None:
        return _cached_colours
    res = _safe_request("GET", "/api/colours")
    _cached_colours = safe_json(res, default=[])
    return _cached_colours

def get_brands_list():
    """Fetches list of vehicle brands with local in-memory caching."""
    global _cached_brands
    if _cached_brands is not None:
        return _cached_brands
    res = _safe_request("GET", "/api/brands")
    _cached_brands = safe_json(res, default=[])
    return _cached_brands

def get_models_list(brand):
    """Fetches models for a specific brand."""
    res = _safe_request("GET", "/api/models", params={"brand": brand})
    return safe_json(res, default=[])

def get_brands_models(brand_name):
    """Wraps model names in MockObj for UI compatibility."""
    models = get_models_list(brand_name)
    results = []
    for m in models:
        row = MockObj()
        row.name = m
        results.append(row)
    return results


""" ============================================================================
    2. POST / PUT / DELETE - DATA MUTATIONS
============================================================================ """

def add_product(brand, model, colour, year, price, order_id, expected_delivery):
    data = {
        "brand": brand, "model": model, "colour": colour, 
        "year": year, "price": price, "order_id": order_id,
        "expected_delivery": _format_date_for_server(expected_delivery)
    }
    _safe_request("POST", "/api/products", json=data)

def add_customer(name, phone, email, pesel, nip, company_name, adress):
    data = {
        "name": name, "phone": phone, "email": email,
        "pesel": pesel, "nip": nip, "company_name": company_name, "adress": adress
    }
    _safe_request("POST", "/api/customers", json=data)

def make_reservation(customer_id, string_id, product_id, advance, adnotation, adnotation_pub, form, paid, term, delivery, payment_method, price=None):
    data = {
        "customer_id": customer_id, "string_order_id": string_id, "product_id": product_id,
        "advance": advance, "adnotation": adnotation, "adnotation_pub": adnotation_pub,
        "form": form, "paid": paid, "term": term, "delivery": delivery, "payment_method": payment_method
    }
    if price is not None and str(price).strip() != "":
        data["price"] = price

    res = _safe_request("POST", "/api/reservations", json=data)
    return safe_json(res, default={})

def add_colour(col):
    invalidate_cache()
    _safe_request("POST", "/api/colours", json={"name": col})

def add_brand(bra):
    invalidate_cache()
    _safe_request("POST", "/api/brands", json={"name": bra})

def add_model(mod, brand):
    _safe_request("POST", "/api/models", json={"brand": brand, "model": mod})

def edit_product(product_id, product_brand, product_model, product_colour, product_price, product_year, product_order_id, product_state, expected_delivery, old_price):
    data = {
        "brand": product_brand, "model": product_model, "colour": product_colour, 
        "price": product_price, "year": product_year, "order_id": product_order_id, 
        "state": product_state, "old_price": old_price,
        "expected_delivery": _format_date_for_server(expected_delivery) 
    }
    _safe_request("PUT", f"/api/products/{product_id}", json=data)

def change_price(product_id, new_price):
    _safe_request("PUT", f"/api/products/{product_id}", json={"price": new_price})

def change_state(product_id, new_state):
    _safe_request("PUT", f"/api/products/{product_id}", json={"state": new_state})

def change_date(id_given, new_date):
    _safe_request("PUT", f"/api/products/{id_given}", json={
        "expected_delivery": _format_date_for_server(new_date) 
    })

def batch_change_dates(id_list, new_date):
    """
    Batch update expected delivery date for multiple vehicles in a single HTTP request.
    """
    if not id_list:
        return
    data = {
        "ids": id_list,
        "expected_delivery": _format_date_for_server(new_date)
    }
    _safe_request("PUT", "/api/products/batch/date", json=data)

def edit_customer(customer_id, name, phone, email, pesel, nip, company_name, adress):
    """Updates customer details in the database."""
    data = {
        "name": name, "phone": phone, "email": email, "pesel": pesel,
        "nip": nip, "company_name": company_name, "adress": adress
    }
    _safe_request("PUT", f"/api/customers/{customer_id}", json=data)

def edit_reservation(reservarion_id, new_price, new_advance, new_form, new_paid, new_adnotation, new_adnotation_pub, new_delivery, new_payment_method, new_term):
    """Updates reservation terms and payment statuses."""
    data = {
        "price": new_price, "advance": new_advance, "form": new_form, 
        "paid": new_paid, "adnotation": new_adnotation, "adnotation_pub": new_adnotation_pub, 
        "delivery": new_delivery, "payment_method": new_payment_method, "term": new_term
    }
    _safe_request("PUT", f"/api/reservations/{reservarion_id}", json=data)

def drop_product(id_given):
    """Deletes a product by ID."""
    _safe_request("DELETE", f"/api/products/{id_given}")

def drop_reservation(id_given):
    """Deletes a reservation by ID."""
    _safe_request("DELETE", f"/api/reservations/{id_given}")

def drop_customer(id_given):
    """Deletes a customer by ID."""
    _safe_request("DELETE", f"/api/customers/{id_given}")

def drop_colour(colour_name):
    """Deletes a vehicle colour option and clears local cache."""
    invalidate_cache()
    _safe_request("DELETE", "/api/colours", json={"name": colour_name})

def drop_brand(brand_name):
    """
    Deletes a brand. The server cascades deletion of all associated models atomically in one transaction.
    """
    invalidate_cache()
    _safe_request("DELETE", "/api/brands/", json={"name": brand_name})

def drop_model(model_name, brand_name):
    """Deletes a specific model of a brand."""
    _safe_request("DELETE", "/api/models/", json={"brand": brand_name, "model": model_name})

def drop_brands_models(models, brand_name):
    """Fallback no-op: server handles cascade model deletion inside drop_brand."""
    pass


def fake_commit():
    """Triggers UI table refresh callback if registered."""
    if refresh_callback:
        refresh_callback()
