from . import session, q_session, Session
from .models import Product, Customer, Reservation, Colour, Brand, Model
from datetime import datetime
from sqlalchemy import Select, func, asc, desc, update, delete, select



def add_product(brand, model, colour, year, price, order_id, expected_delivery):
    try:
        new_order = Product(brand=brand, model=model, colour=colour, year=year, added_on=datetime.now(),
        price=price, order_id=order_id, state="Oczekujemy na dostawę", expected_delivery = expected_delivery, old_price=price)

        session.add(new_order)
        session.commit()
    except:
        session.rollback()
        raise


def add_customer(name, phone, email, pesel, nip, company_name, adress):
    
    try: 
        new_customer = Customer(name=name, phone=phone, email=email, added_on=datetime.now(), pesel=pesel, nip=nip, company_name=company_name, adress=adress)

        session.add(new_customer)
        session.commit()
    except:
        session.rollback()
        raise


def make_reservation(customer_id, string_id, product_id, advance, adnotation, adnotation_pub, form, paid, term, delivery, payment_method):
    try:
        new_reservation=Reservation(date=datetime.now(), 
        customer_id=customer_id, product_id=product_id, advance = advance, adnotation = adnotation,
        adnotation_pub = adnotation_pub, form=form, paid=paid, term = term, delivery = delivery, 
        payment_method = payment_method, string_order_id = string_id)
        
        session.add(new_reservation)
        session.commit()
    except:
        session.rollback()
        raise


def get_all_products():
    return q_session.query(Product, Reservation).outerjoin(Reservation).where(Product.state != "Wydany").order_by(desc(Product.id)).all()


def get_all_old_products():
    return q_session.query(Product, Reservation).outerjoin(Reservation).order_by(desc(Product.id)).all()


def get_all_customers():
    return q_session.query(Customer).order_by(desc(Customer.id)).all()


def get_all_reservations():
    return q_session.query(Reservation).all()


def get_free_products():
    result = q_session.execute(
        Select(Product, func.max(Product.price), func.count(Product.id),func.lower(Product.model), func.min(Product.expected_delivery).label('expected_deliveryy')) #
        .outerjoin(Reservation)
        .where(Reservation.id==None, Product.state != "Wydany")
        .group_by(Product.brand, Product.model, Product.colour, Product.year)
        .order_by(func.lower(Product.brand), func.lower(Product.model), Product.year, func.lower(Product.colour))
    )
    
    return result


def get_free_products_split():
    result = q_session.execute(
        Select(Product, func.max(Product.price), func.count(Product.id),func.lower(Product.model), Product.expected_delivery.label('expected_deliveryy'))
        .outerjoin(Reservation)
        .where(Reservation.id==None, Product.state != "Wydany")
        .group_by(Product.brand, Product.model, Product.colour, Product.year, Product.expected_delivery)
        .order_by(func.lower(Product.brand), func.lower(Product.model), Product.year, func.lower(Product.colour))
    )
    
    return result


def get_full_reservations():
    result = q_session.execute(
        Select(Reservation, Product, Customer)
        .join(Product).join(Customer)
        .where(Product.state != "Wydany")
        .order_by(Reservation.date.desc())
    )
    return result


def get_full_old_reservations():
    result = q_session.execute(
        Select(Reservation, Product, Customer)
        .join(Product).join(Customer)
        .order_by(Reservation.date.desc())
    )
    return result


def get_product(id_given):
    return session.query(Product).where(Product.id == id_given).first()


def get_customer(id_given):
    return session.query(Customer).where(Customer.id == id_given).first()


def change_price(product_id, new_price):
    try:
        row = get_product(product_id)
        row.price = new_price
        session.commit()
    except:
        session.rollback()
        raise


def drop_product(id_given):
    try:
        session.execute(delete(Product).where(Product.id == id_given))
        session.commit()
    except:
        session.rollback()
        raise


def drop_reservation(id_given):
    try:
        product = session.query(Product).join(Reservation).where(Reservation.id == id_given).first()
        product.price = product.old_price
        session.execute(delete(Reservation).where(Reservation.id == id_given))
        session.commit()
    except:
        session.rollback()
        raise


def drop_customer(id_given):
    try:
        session.execute(delete(Customer).where(Customer.id == id_given))
        session.commit()
    except:
        session.rollback()
        raise


def get_full_reservation(id_given):
    result = session.query(Reservation, Product, Customer).join(Product).join(Customer).where(Reservation.id==id_given).first()
    
    return result


def do_customer_have_reservations(id_given):
    res = session.query(Reservation, Customer).join(Customer).where(Customer.id == id_given).first()
    if res is None:
        return False
    else:
        return True


def change_state(product_id, new_state):
    try:
        row = get_product(product_id)
        row.state = new_state
        session.commit()
    except:
        session.rollback()
        raise


def get_first_free_element(brand_given, model_given, colour_given, year_given, delivery_given):
    if delivery_given != "": 
        delivery_given = datetime.strptime(delivery_given, "%d.%m.%Y")
    else: 
        delivery_given = None
    result = session.query(Product)\
        .outerjoin(Reservation)\
        .where(Reservation.id==None, Product.state == "Oczekujemy na dostawę", 
        Product.brand==brand_given, Product.model==model_given,
        Product.colour==colour_given, Product.year==year_given, Product.expected_delivery==delivery_given)\
        .first()
    
    if result is None:
        result = session.query(Product)\
            .outerjoin(Reservation)\
            .where(Reservation.id==None, Product.state != "Wydany", 
            Product.brand==brand_given, Product.model==model_given,
            Product.colour==colour_given, Product.year==year_given, Product.expected_delivery==delivery_given)\
            .first()

    return result


def get_colours_list():
    res = session.query(Colour).order_by(Colour.name)
    lista = []
    for col in res:
        lista.append(col.name)
    
    return lista


def add_colour(col):
    try:
        colour = Colour(name=col)
        session.add(colour)
        session.commit()
    except:
        session.rollback()
        raise


def get_brands_list():
    res = session.query(Brand).order_by(Brand.name)
    lista = []
    for bra in res:
        lista.append(bra.name)
    
    return lista


def add_brand(bra):
    try:
        brand = Brand(name=bra)
        session.add(brand)
        session.commit()
    except:
        session.rollback()
        raise


def add_model(mod, brand):
    try:
        brand = session.query(Brand).where(Brand.name == brand).first()
        brand_idd = brand.id
        new_model = Model(name=mod, brand_id= brand_idd, namehash=f"{brand_idd}$^{mod}")
        session.add(new_model)
        session.commit()
    except:
        session.rollback()
        raise


def get_models_list(brand):
    if brand is None or brand=="":
        return []
    brand = session.query(Brand).where(Brand.name == brand).first()
    brand_idd = brand.id
    res = session.query(Model).where(Model.brand_id == brand_idd).order_by(Model.name)
    lista = []
    for mod in res:
        lista.append(mod.name)
    
    return lista
    

def get_reservation(id_given):
    return session.query(Reservation, Product, Customer).join(Product).join(Customer).where(Reservation.id == id_given).first()


def fake_commit():
    temp_session = Session()
    try:
        temp_session.begin()
        
        obj = None
        if temp_session.dirty:
            obj = list(temp_session.dirty)[0] 
        
        temp_session.commit()  
        
        if obj:
            temp_session.refresh(obj) 

    finally:
        temp_session.close()


def drop_brand(brand_name):
    try:
        q = session.query(Brand).where(Brand.name==brand_name).first()
        session.delete(q)
        session.commit()
    except:
        session.rollback()
        raise


def drop_model(model_name, brand_name):
    try:
        brand = session.query(Brand).where(Brand.name==brand_name).first()
        q = session.query(Model).where(Model.name==model_name, Model.brand_id==brand.id).first()
        session.delete(q)
        session.commit()
    except:
        session.rollback()
        raise


def drop_colour(colour_name):
    try:
        q = session.query(Colour).where(Colour.name==colour_name).first()
        session.delete(q)
        session.commit()
    except:
        session.rollback()
        raise


def get_brands_models(brand_name):
    
    return session.query(Model).join(Brand).where(Brand.name == brand_name).all()
    

def drop_brands_models(models):
    for model in models:
        session.delete(model)
    
    session.commit()


def edit_reservation(reservarion_id, new_price, new_advance, new_form, new_paid, new_adnotation, new_adnotation_pub, new_delivery, new_payment_method, new_term):
    reservation = session.query(Reservation, Product).join(Product).where(Reservation.id==reservarion_id).first()
    reservation.Product.price = new_price
    reservation.Reservation.adnotation = new_adnotation
    reservation.Reservation.adnotation_pub = new_adnotation_pub
    reservation.Reservation.advance = new_advance
    reservation.Reservation.form = new_form
    reservation.Reservation.paid = new_paid
    reservation.Reservation.term = new_term
    reservation.Reservation.delivery = new_delivery
    reservation.Reservation.payment_method = new_payment_method


    session.commit()


def edit_product(product_id, product_brand, product_model, product_colour, 
    product_price, product_year, product_order_id, product_state, expected_delivery, old_price):
    
    product = session.query(Product).where(Product.id == product_id).first()

    product.brand = product_brand
    product.model = product_model
    product.colour = product_colour
    product.price = product_price
    product.old_price = old_price
    product.year = product_year
    product.order_id = product_order_id
    product.state = product_state
    product.expected_delivery = expected_delivery

    session.commit()


def edit_customer(customer_id, name, phone, email, pesel, nip, company_name, adress):
    customer = session.query(Customer).where(Customer.id == customer_id).first()

    customer.name = name
    customer.phone = phone
    customer.email = email
    customer.pesel = pesel
    customer.nip = nip
    customer.company_name = company_name
    customer.adress = adress

    session.commit()


def change_date(id_given, new_date):
    product = session.query(Product).where(Product.id == id_given).first()

    product.expected_delivery = new_date

    session.commit()


def get_new_order_id():
    try:
        new_id = q_session.query(Reservation).order_by(desc(Reservation.id)).first().id + 1
        return new_id
    except:
        return 1

def get_last_reservation():
    stmt = select(Reservation).order_by(Reservation.id.desc()).limit(1)
    result = session.execute(stmt)
    result = result.scalar_one_or_none()
    return result