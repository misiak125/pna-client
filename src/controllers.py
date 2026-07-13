import requests
from datetime import datetime
import os
from tkinter import messagebox
from urllib.parse import urlparse
from src import SERVER_URL

HEADERS = {}
refresh_callback = None

class MockObj:
    """klasa pozwalająca na przypisywanie atrybutów po kropce (imitacja SQLAlchemy)"""
    pass

def _format_date_for_server(date_obj):
    """Pomocnicza funkcja formatująca datę z Tkintera na pełen format ISO z czasem"""
    if not date_obj:
        return None
        
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime("%Y-%m-%dT00:00:00")

    date_str = str(date_obj)
    if "T" not in date_str:
        return date_str + "T00:00:00"
    return date_str

# --- GŁÓWNY HANDLER ZAPYTAŃ HTTP I BŁĘDÓW ---
def _safe_request(method, endpoint, silent=False, **kwargs):
    """
    Wysyła zapytanie HTTP i obsługuje błędy z Tkinter messagebox.
    :param silent: Jeśli True, nie wyświetla wyskakujących okienek.
    """
    url = f"{SERVER_URL}{endpoint}"
    try:
        response = requests.request(method, url, headers=HEADERS, timeout=5, **kwargs)
       
        if response.status_code in (200, 201):
            return response
            
        # Błędy zwrócone przez API 
        error_msg = "Nieznany błąd serwera."
        try:
            error_msg = response.json().get("error", f"Kod błędu: {response.status_code}")
        except ValueError:
            pass

        if not silent:
            messagebox.showerror("Odpowiedź Serwera", f"Serwer odrzucił żądanie:\n\n{error_msg}")
            
        else:
            print(f"[POLLING ERROR] {error_msg}")

        raise ValueError("API Request Failed")

    except requests.exceptions.RequestException as e:
        if not silent:
            messagebox.showerror("Błąd Połączenia", f"Brak połączenia z bazą danych.\nUpewnij się, że masz dostęp do Internetu.\n\nSzczegóły:\n{e}")
            
        else:
            print(f"[POLLING ERROR] Brak połączenia z serwerem: {e}")

        raise ConnectionError("No connection to API")


""" ============================================================================
    1. GET - POBIERANIE DANYCH 
============================================================================ """

def get_free_products():
    res = _safe_request("GET", "/api/products/free")
    if not res: return []
    
    results = []
    for d in res.json():
        row = MockObj()
        row.Product = MockObj()
        row.Product.brand = d['brand']
        row.Product.model = d['model']
        row.Product.year = d['year']
        row.Product.colour = d['colour']
        
        row.Product.id = d.get('first_free_id')
        row.max = d['price']
        row.count = d['count']
        row.expected_deliveryy = datetime.strptime(d['delivery'], '%d.%m.%Y') if d['delivery'] else None
        
        results.append(row)
    return results

def get_free_products_split():
    res = _safe_request("GET", "/api/products/free?split_dates=true")
    if not res: return []
    
    results = []
    for d in res.json():
        row = MockObj()
        row.Product = MockObj()
        row.Product.brand = d['brand']
        row.Product.model = d['model']
        row.Product.year = d['year']
        row.Product.colour = d['colour']
        
        row.max = d['price']
        row.count = d['count']
        row.expected_deliveryy = datetime.strptime(d['delivery'], '%d.%m.%Y') if d['delivery'] else None
        
        results.append(row)
    return results

def get_all_customers():
    res = _safe_request("GET", "/api/customers")
    if not res: return []
    
    results = []
    for c in res.json():
        row = MockObj()
        row.id = c['id']
        row.name = c['name']
        row.phone = c['phone']
        row.email = c['email']
        row.pesel = c['pesel']
        row.nip = c['nip']
        row.adress = c['adress']
        row.company_name = c['company_name']
        row.added_on = datetime.strptime(c['added_on'], '%d-%m-%Y %H:%M') if c['added_on'] else datetime.now()
        results.append(row)
    return results

def get_full_reservations():
    return _fetch_reservations(show_finalized=False)

def get_full_old_reservations():
    return _fetch_reservations(show_finalized=True)

def _fetch_reservations(show_finalized):
    url = f"/api/reservations?show_finalized={'true' if show_finalized else 'false'}"
    res = _safe_request("GET", url)
    if not res: return []
    
    results = []
    for r in res.json():
        row = MockObj()
        row.Reservation = MockObj()
        row.Customer = MockObj()
        row.Product = MockObj()
        
        row.Reservation.id = r['reservation_id']
        row.Reservation.string_order_id = r['order_id']
        row.Reservation.adnotation = r['adnotation']
        row.Reservation.paid = r['paid']
        row.Reservation.date = datetime.strptime(r['date'], '%d-%m-%Y %H:%M') if r['date'] else datetime.now()
        
        row.Customer.name = r['customer_name']
        row.Product.brand = r['brand']
        row.Product.model = r['model']
        row.Product.colour = r['colour']
        
        results.append(row)
    return results

def get_all_products():
    return _fetch_all_products(show_sold=False)

def get_all_old_products():
    return _fetch_all_products(show_sold=True)

def _fetch_all_products(show_sold):
    url = f"/api/products/all?show_sold={'true' if show_sold else 'false'}"
    res = _safe_request("GET", url)
    if not res: return []
    
    results = []
    for p in res.json():
        row = MockObj()
        row.Product = MockObj()
        
        row.Product.id = p['id']
        row.Product.brand = p['brand']
        row.Product.model = p['model']
        row.Product.year = p['year']
        row.Product.colour = p['colour']
        row.Product.price = p['price']
        row.Product.state = p['state']
        row.Product.order_id = p['order_id']
        row.Product.added_on = datetime.strptime(p['added_on'], '%d-%m-%Y %H:%M') if p['added_on'] else datetime.now()
        row.Product.expected_delivery = datetime.strptime(p['delivery'], '%d.%m.%Y') if p['delivery'] else None
        
        row.Reservation = MockObj() if p['is_reserved'] == "TAK" else None
        results.append(row)
    return results

# ----- POJEDYNCZE OBIEKTY Z BAZY -----

def get_product(id_given):
    res = _safe_request("GET", f"/api/products/{id_given}")
    if not res: return None
    
    d = res.json()
    row = MockObj()
    row.id = d['id']
    row.brand = d['brand']
    row.model = d['model']
    row.colour = d['colour']
    row.year = d['year']
    row.price = d['price']
    row.old_price = d['old_price']
    row.state = d['state']
    row.order_id = d['order_id']
    row.expected_delivery = datetime.strptime(d['expected_delivery'], '%Y-%m-%d') if d['expected_delivery'] else None
    return row

def get_customer(id_given):
    res = _safe_request("GET", f"/api/customers/{id_given}")
    if not res: return None
    
    c = res.json()
    row = MockObj()
    row.id = c['id']
    row.name = c['name']
    row.phone = c['phone']
    row.email = c['email']
    row.pesel = c['pesel']
    row.nip = c['nip']
    row.company_name = c['company_name']
    row.adress = c['adress']
    return row

def get_full_reservation(id_given):
    res = _safe_request("GET", f"/api/reservations/{id_given}")
    if not res: return None
    
    d = res.json()
    row = MockObj()
    
    row.Reservation = MockObj()
    row.Product = MockObj()
    row.Customer = MockObj()
    
    r = d.get("reservation", {})
    p = d.get("product", {})
    c = d.get("customer", {})
    
    row.Reservation.id = r.get('id')
    row.Reservation.advance = r.get('advance')
    row.Reservation.adnotation = r.get('adnotation')
    row.Reservation.adnotation_pub = r.get('adnotation_pub')
    row.Reservation.form = r.get('form')
    row.Reservation.paid = r.get('paid')
    row.Reservation.term = r.get('term')
    row.Reservation.delivery = r.get('delivery')
    row.Reservation.payment_method = r.get('payment_method')
    row.Reservation.string_order_id = r.get('string_order_id')
    row.Reservation.date = datetime.strptime(r.get('date'), '%Y-%m-%dT%H:%M:%S') if r.get('date') else None
    
    # --- DANE PRODUKTU ---
    row.Product.id = p.get('id')
    row.Product.brand = p.get('brand')
    row.Product.model = p.get('model')
    row.Product.colour = p.get('colour')
    row.Product.year = p.get('year')
    row.Product.price = p.get('price')
    row.Product.old_price = p.get('old_price')
    row.Product.state = p.get('state')
    row.Product.order_id = p.get('order_id')
    row.Product.expected_delivery = datetime.strptime(p.get('expected_delivery'), '%Y-%m-%d') if p.get('expected_delivery') else None
    
    # --- DANE KLIENTA ---
    row.Customer.id = c.get('id')
    row.Customer.name = c.get('name')
    row.Customer.phone = c.get('phone')
    row.Customer.email = c.get('email')
    row.Customer.pesel = c.get('pesel')
    row.Customer.nip = c.get('nip')
    row.Customer.adress = c.get('adress')
    row.Customer.company_name = c.get('company_name')
    
    return row

get_reservation = get_full_reservation

def do_customer_have_reservations(id_given):
    res = _safe_request("GET", f"/api/customers/{id_given}/has_reservations")
    if not res: return False
    return res.json().get("is_reserved", False)

def get_first_free_element(brand_given, model_given, colour_given, year_given, delivery_given):
    # Odtworzenie zapytania pobierającego PIERWSZY WOLNY produkt do rezerwacji
    params = {
        "brand": brand_given,
        "model": model_given,
        "colour": colour_given,
        "year": year_given,
        "delivery": delivery_given
    }
    res = _safe_request("GET", "/api/products/first_free", params=params)
    if not res: return None
    
    d = res.json()
    row = MockObj()
    row.id = d['id']
    row.price = d['price']
    return row

def get_last_reservation():
    res = _safe_request("GET", "/api/reservations/last")
    if not res: return None
    d = res.json()
    row = MockObj()
    row.id = d['id']
    row.string_order_id = d['string_order_id']
    return row

def get_new_order_id():
    res = _safe_request("GET", "/api/reservations/next_id")
    if not res: return 1
    return res.json().get("next_id", 1)


# ----- SŁOWNIKI -----

def get_colours_list():
    res = _safe_request("GET", "/api/colours")
    return res.json() if res else []

def get_brands_list():
    res = _safe_request("GET", "/api/brands")
    return res.json() if res else []

def get_models_list(brand):
    res = _safe_request("GET", "/api/models", params={"brand": brand})
    return res.json() if res else []

def get_brands_models(brand_name):
    models = get_models_list(brand_name)
    results = []
    for m in models:
        row = MockObj()
        row.name = m
        results.append(row)
    return results


""" ============================================================================
    2. POST / PUT / DELETE - MODYFIKACJA DANYCH
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

def make_reservation(customer_id, string_id, product_id, advance, adnotation, adnotation_pub, form, paid, term, delivery, payment_method):
    data = {
        "customer_id": customer_id, "string_order_id": string_id, "product_id": product_id,
        "advance": advance, "adnotation": adnotation, "adnotation_pub": adnotation_pub,
        "form": form, "paid": paid, "term": term, "delivery": delivery, "payment_method": payment_method
    }
    _safe_request("POST", "/api/reservations", json=data)

def add_colour(col):
    _safe_request("POST", "/api/colours", json={"name": col})

def add_brand(bra):
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

def edit_customer(customer_id, name, phone, email, pesel, nip, company_name, adress):
    data = {
        "name": name, "phone": phone, "email": email, "pesel": pesel,
        "nip": nip, "company_name": company_name, "adress": adress
    }
    _safe_request("PUT", f"/api/customers/{customer_id}", json=data)

def edit_reservation(reservarion_id, new_price, new_advance, new_form, new_paid, new_adnotation, new_adnotation_pub, new_delivery, new_payment_method, new_term):
    data = {
        "price": new_price, "advance": new_advance, "form": new_form, 
        "paid": new_paid, "adnotation": new_adnotation, "adnotation_pub": new_adnotation_pub, 
        "delivery": new_delivery, "payment_method": new_payment_method, "term": new_term
    }
    _safe_request("PUT", f"/api/reservations/{reservarion_id}", json=data)


def drop_product(id_given):
    _safe_request("DELETE", f"/api/products/{id_given}")

def drop_reservation(id_given):
    _safe_request("DELETE", f"/api/reservations/{id_given}")

def drop_customer(id_given):
    _safe_request("DELETE", f"/api/customers/{id_given}")

def drop_colour(colour_name):
    _safe_request("DELETE", "/api/colours", json={"name": colour_name})

def drop_brand(brand_name):
    print("here")
    _safe_request("DELETE", "/api/brands", json={"name": brand_name})

def drop_model(model_name, brand_name):
    _safe_request("DELETE", "/api/models/", json={"brand": brand_name, "model": model_name})

def drop_brands_models(models, brand_name):
    """ W oryginalnym kodzie ta funkcja czyściła modele dla konkretnej marki. """
    for model in models:
        drop_model(model.name, brand_name)


def get_all_reservations():
    """ Zapasowe (dla kompatybilności), jeśli masz to wywołanie w starszej części UI """
    return get_full_reservations()

def fake_commit():
    if refresh_callback:
        refresh_callback()
    pass

