import re
from .funcs import animate_gif, validate_nip, validate_pesel, short_price, change_dates, generate_pdf_confirmation
from tkinter import Toplevel, Label, ttk, messagebox, Button, StringVar, END
from PIL import ImageTk, Image
import src.controllers as con
from src import resource_path
import os
import tkcalendar as cal
import babel.numbers

def on_customer_click(lasttop):
    top = Toplevel(lasttop)
    frame_counter = 0
    top.title("GRATULACJE!")
    cat_gif = Image.open(resource_path(os.path.join("static", "cat1.gif")))
    frames = []
    for i in range(cat_gif.n_frames):
        cat_gif.seek(i)  
        frame = ImageTk.PhotoImage(cat_gif.copy())  
        frames.append(frame)
    gif_label = Label(top)
    gif_label.pack()

    text_label = Label(top, text="Pogłaskałeś klienta!", 
        font=("Helvetica", 17, "bold"), bg="black", fg="white")
    text_label.place(anchor="w", x=10, y=20)

    animate_gif(gif_label, frames, frame_counter)


def sum_up_product(product_brand, product_model, product_colour, product_price, product_year, product_order_id, quantity, expected_delivery_str, expected_delivery):
        #print(f"!{expected_delivery_str}!")
        if expected_delivery_str == "" or expected_delivery_str == None:
            #print("here")
            expected_delivery = None
        if not product_price:
            product_price = 0.0

        try:
            product_price = product_price.replace(',', '.', 1)
        except:
            pass

        if not product_brand or not product_model or not product_colour or not quantity or not product_year:
            messagebox.showerror("Error", "Wypełnij pole Marka, Model, Rocznik, Kolor oraz Ilość")
            return

        try:
            product_price = float(product_price)
            product_price = round(product_price, 2)
            product_model = str(product_model)
            product_colour = str(product_colour)
            product_brand = str(product_brand)
            product_order_id = str(product_order_id)
            product_year = int(product_year)
            quantity = int(quantity)
            if product_year < 1000:
                product_year+=2000
            for i in range(quantity):
                con.add_product(product_brand, product_model, product_colour, product_year, product_price, product_order_id, expected_delivery)
            messagebox.showinfo("Sukces", "Dodano produkt")
        except ValueError:
            messagebox.showerror("Error", "Niewłaściwie podane dane")


def sum_up_customer(new_customer_name, new_customer_phone, new_customer_email, new_customer_pesel, new_customer_nip, new_customer_company, new_customer_adress, lasttop):

    new_customer_email=str(new_customer_email)
    new_customer_phone=str(new_customer_phone)
    new_customer_phone=new_customer_phone.replace(' ', '')
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_customer_email)
    new_customer_phone = new_customer_phone.replace(" ", "")
    valid_phone = re.match("^\\+?[1-9][0-9]{7,14}$", new_customer_phone)
    valid_nip = validate_nip(new_customer_nip)
    valid_pesel = validate_pesel(new_customer_pesel)
    if new_customer_name=="":
        messagebox.showerror("Error", "Wprowadź imię i nazwisko", parent=lasttop)
        return
    if " " not in new_customer_name:
        messagebox.showerror("Error", "Wporwadź poprawne imię i nazwisko", parent=lasttop)
        return
    if not valid_phone or new_customer_phone=="":
        messagebox.showerror("Error", "Wprowadź poprwany numer telefonu", parent=lasttop)
        return
    if not valid and not new_customer_email=="":
        messagebox.showerror("Error", "Wprowadź poprawny adres email", parent=lasttop)
        return
    if valid_pesel == "invalid":
        messagebox.showerror("Error", "Wprowadź poprawny numer PESEL", parent=lasttop)
        return
    if valid_nip=='invalid':
        messagebox.showerror("Error", "Wprowadź poprawny NIP", parent=lasttop)
        return
    if  (valid_nip != "" and new_customer_company == "") or (valid_nip == "" and new_customer_company != ""):
        messagebox.showerror("Error", "Wprowadź NIP wraz z nazwą firmy", parent=lasttop)
        return
    '''
    if new_customer_email=="":
        ensure_no_email(lasttop, new_customer_name, new_customer_phone, new_customer_email, valid_pesel, valid_nip)
        return
    '''

    lasttop.destroy()
    con.add_customer(new_customer_name, new_customer_phone, new_customer_email, valid_pesel, valid_nip, new_customer_company, new_customer_adress)


def ensure_no_email(lasttop, new_customer_name, new_customer_phone, new_customer_email, new_customer_pesel, new_customer_nip):
    top=Toplevel(lasttop)
    ask_label = Label(top, text="Czy chcesz dodać adres email?", font=("Default", 14))
    ask_label.grid(pady=10, padx=10, row=0, column=0, columnspan=2, sticky="nsew")

    yes_button = Button(top, text="Tak", command=lambda: top.destroy())
    no_button = Button(top, text="Nie", command=lambda: [top.destroy(), con.add_customer(new_customer_name, new_customer_phone, new_customer_email, new_customer_pesel, new_customer_nip), lasttop.destroy()])

    yes_button.grid(pady=10, padx=10, row=1, column=1, sticky="e")
    no_button.grid(pady=10, padx=10, row=1, column=0, sticky="w")

    top.grid_columnconfigure(0, weight=1)
    top.grid_columnconfigure(1, weight=1)
    top.grid_rowconfigure(0, weight=1)
    

def delete_product(product_id, is_reserved, lasttop):
    if product_id == -1:
        messagebox.showerror("Error", "Wybierz pojazd.")
        return
    if is_reserved == "TAK":
        messagebox.showerror("Error", "Ten pojazd jest zarezerwowany.\nAnuluj rezerwację tego pojazdu i spróbuj ponownie.")
        return
    top = Toplevel(lasttop)
    top.title("Potwierdź usunięcie")
    product = con.get_product(product_id)

    top.rowconfigure(0, weight=1)
    top.rowconfigure(1, weight=1)
    top.columnconfigure(0, weight=1)
    top.columnconfigure(1, weight=1)

    label = Label(top, text=f"Czy na pewno chcesz usunąć {product.brand} {product.model} {product.colour} {product.year}?", font=("Default", 14))
    label.grid(pady=10, padx=10, row=0, column=0, columnspan=2)

    no_button = Button(top, text="NIE", command=top.destroy)
    no_button.grid(row=1, column=0, padx=10, pady=10, sticky="sw")

    yes_button = Button(top, text="TAK", command=lambda: [con.drop_product(product.id), top.destroy()])
    yes_button.grid(row=1, column=1, padx=10, pady=10, sticky="se")


def delete_reservation(reservation_id, lasttop):
    if reservation_id == -1:
        messagebox.showerror("Error", "Wybierz rezerwację.")
        return
    top = Toplevel(lasttop)
    top.title("Potwierdź usunięcie")
    reservation = con.get_full_reservation(reservation_id)

    top.rowconfigure(0, weight=1)
    top.rowconfigure(1, weight=1)
    top.columnconfigure(0, weight=1)
    top.columnconfigure(1, weight=1)

    label = Label(top, text=f"Czy na pewno chcesz anulować rezerwację dla {reservation.Customer.name} na\n{reservation.Product.brand}"
    f" {reservation.Product.model} {reservation.Product.colour} {reservation.Product.year}?", font=("Default", 14))
    label.grid(pady=10, padx=10, row=0, column=0, columnspan=2)

    no_button = Button(top, text="NIE", command=top.destroy)
    no_button.grid(row=1, column=0, padx=10, pady=10, sticky="sw")

    yes_button = Button(top, text="TAK", command=lambda: [con.drop_reservation(reservation.Reservation.id), top.destroy()])
    yes_button.grid(row=1, column=1, padx=10, pady=10, sticky="se")


def delete_customer(customer_id, lasttop):
    if customer_id == -1:
        messagebox.showerror("Error", "Wybierz klienta.")
        return

    if con.do_customer_have_reservations(customer_id):
        messagebox.showerror("Error", "Ten klient posiada rezerwacje.\nAnuluj wszystkie rezerwacje tego klienta i spróbuj ponownie.")
        return
    top = Toplevel(lasttop)
    top.title("Potwierdź usunięcie")

    customer  = con.get_customer(customer_id)

    top.rowconfigure(0, weight=1)
    top.rowconfigure(1, weight=1)
    top.columnconfigure(0, weight=1)
    top.columnconfigure(1, weight=1)

    label = Label(top, text=f"Czy na pewno chcesz usunąć klienta {customer.name} {customer.phone}?", font=("Default", 14))
    label.grid(pady=10, padx=10, row=0, column=0, columnspan=2)

    no_button = Button(top, text="NIE", command=top.destroy)
    no_button.grid(row=1, column=0, padx=10, pady=10, sticky="sw")

    yes_button = Button(top, text="TAK", command=lambda: [con.drop_customer(customer.id), top.destroy()])
    yes_button.grid(row=1, column=1, padx=10, pady=10, sticky="se")


def change_state(product_id, lasttop):
    if product_id==-1:
        messagebox.showerror("Error", "Wybierz produkt")
        return
    
    top=Toplevel(lasttop)
    top.title("Zmień stan pojazdu")
    top.rowconfigure(0, weight=1)
    top.rowconfigure(1, weight=1)
    top.columnconfigure(0, weight=1)
    top.columnconfigure(1, weight=1)

    product = con.get_product(product_id)

    label = Label(top, text=f"Zmień stan {product.brand} {product.model} {product.colour} {product.year}", font=("Default", 14))
    label.grid(pady=10, padx=10, row=0, column=0, columnspan=2)

    product_new_state = StringVar()
    select = ttk.Combobox(top, textvariable = product_new_state,  state="readonly")
    select['values'] = ("Oczekujemy na dostawę", "Na stanie", "Wydany")
    select.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    product_new_state.set(product.state)


    no_button = Button(top, text="Anuluj", command=top.destroy)
    no_button.grid(row=2, column=0, padx=10, pady=10, sticky="sw")


    yes_button = Button(top, text="Potwierdź", command=lambda: [con.change_state(product.id, product_new_state.get()), top.destroy()])
    yes_button.grid(row=2, column=1, padx=10, pady=10, sticky="se")
    
    


def add_brand(brand, brand_cbox, new_brand_cbox):
    brand = brand.strip()
    if brand == "":
        return
    try:
        con.add_brand(brand)
        brand_cbox["values"] = con.get_brands_list()
        new_brand_cbox["values"] = con.get_brands_list()
        messagebox.showinfo("Sukces", "Pomyślnie dodano markę")
    except:
        messagebox.showerror("Error", "Nie udało się dodać marki")


def add_colour(colour, colour_cbox):
    colour = colour.strip()
    if colour == "":
        return
    try:
        con.add_colour(colour)
        colour_cbox["values"] = con.get_colours_list()
        messagebox.showinfo("Sukces", "Pomyślnie dodano kolor")
    except:
        messagebox.showerror("Error", "Nie udało się dodać koloru")


def add_model(model, brand):
    model = model.strip()
    if model == "" or brand == "" or brand is None:
        return
    try:
        con.add_model(model, brand)
        messagebox.showinfo("Sukces", "Pomyślnie dodano model")
    except:
        messagebox.showerror("Error", "Nie udało się dodać modelu")


def delete_brand(brand, brand_cbox, new_brand_cbox):
    brand = brand.strip()
    if brand == "":
        return
    models = con.get_brands_models(brand) #SERVER
    if models is not None and len(models)>0:
        if not ensure_delete_models(): return
    try:
        con.drop_brands_models(models)
        con.drop_brand(brand)
        brand_cbox["values"] = con.get_brands_list()
        new_brand_cbox["values"] = con.get_brands_list()
        messagebox.showinfo("Sukces", "Pomyślnie usunięto markę")
    except:
        messagebox.showerror("Error", f"Nie udało się usunąć marki")


def delete_colour(colour, colour_cbox):
    colour = colour.strip()
    if colour == "":
        return
    try:
        con.drop_colour(colour)
        colour_cbox["values"] = con.get_colours_list()
        messagebox.showinfo("Sukces", "Pomyślnie usunięto kolor")
    except:
        messagebox.showerror("Error", "Nie udało się usunąć koloru")


def delete_model(model, brand):
    model = model.strip()
    if model == "" or brand == "" or brand is None:
        return
    try:
        con.drop_model(model, brand)
        messagebox.showinfo("Sukces", "Pomyślnie usunięto model")
    except:
        messagebox.showerror("Error", f"Nie udało się usunąć modelu")


def ensure_delete_models():
    response = messagebox.askyesno("Potwierdzenie", "Ta marka posiada przypisane modele. Czy na pewno chcesz ją usunąć, a za razem jej wszystkie modele?")
    return response


def confirm_edit_reservation(reservation, price_entry, advance_entry, form_entry, paid_entry, adnotation_entry, adnotation_entry_pub, term, delivery, payment_method, lasttop):
    if price_entry == '' or price_entry is None:
        messagebox.showerror("Error", "Podaj cenę", parent=lasttop)
        return
    
    if advance_entry == '' or advance_entry is None:
        messagebox.showerror("Error", "Podaj wartość zaliczki", parent=lasttop)
        return

    try:
        advance_entry = advance_entry.replace(',', '.', 1)
    except:
        pass

    try:
        price_entry = price_entry.replace(',', '.', 1)
    except:
        pass

    changes="Zmiany:\n"

    try:
        advance_entry = float(advance_entry)
        advance_entry = round(advance_entry, 2)
        price_entry = float(price_entry)
        price_entry = round(price_entry, 2)
    except Exception as e:
        messagebox.showerror("Error", "Błędnie podane dane", parent=lasttop)
        return
    
    if reservation.Product.price != price_entry:
        changes = changes+f"Cena: {short_price(reservation.Product.price)} 🡢 {short_price(price_entry)}\n"
    
    if reservation.Reservation.advance != advance_entry:
        changes = changes+f"Zaliczka: {short_price(reservation.Reservation.advance)} 🡢 {short_price(advance_entry)}\n"

    if reservation.Reservation.form:
        form = 'zadatek'
    else:
        form = 'zaliczka'
    
    if form_entry == 'zadatek':
        new_form = True
    else:
        new_form = False

    if form != form_entry:
        changes = changes+f"Forma: {form} 🡢 {form_entry}\n"

    if reservation.Reservation.paid:
        og_paid = "Zapłacono"
    else:
        og_paid = "Nie zapłacono"

    if paid_entry:
        new_paid = "Zapłacono"
    else:
        new_paid = "Nie zapłacono"

    if reservation.Reservation.delivery:
        og_delivery = "Tak"
    else:
        og_delivery = "Nie"

    if delivery:
        new_delivery = "Tak"
    else:
        new_delivery = "Nie"

    if og_delivery != new_delivery:
        changes = changes+f"Dostawa: {og_delivery} 🡢 {new_delivery}\n"

    if og_paid != new_paid:
        changes = changes+f"Rozliczenie: {og_paid} 🡢 {new_paid}\n"

    if reservation.Reservation.payment_method != payment_method:
        changes = changes+f"Forma płatności: {reservation.Reservation.payment_method} 🡢 {payment_method}\n"

    if reservation.Reservation.term != term:
        changes = changes+f"Termin realizacji: {reservation.Reservation.term} 🡢 {term}\n"

    if reservation.Reservation.adnotation != adnotation_entry:
        changes = changes+f"Uwagi: {reservation.Reservation.adnotation} 🡢 {adnotation_entry}\n"

    if reservation.Reservation.adnotation_pub != adnotation_entry_pub:
        changes = changes+f"Uwagi dla klienta: {reservation.Reservation.adnotation_pub} 🡢 {adnotation_entry_pub}\n"

    if changes == "Zmiany:\n":
        messagebox.showerror("Error", "Wprowadź zmiany", parent=lasttop)
        return

    
    top = Toplevel()
    lasttop.destroy()
    top.title("Potwierdź zmiany")

    changes_label=Label(top, text=changes, font=("Default, 12"), justify='left')
    changes_label.pack(pady=10, padx=10)

    yes_button = Button(top, text="Potwierdź", command=lambda: [con.edit_reservation(reservation.Reservation.id, price_entry, 
    advance_entry, new_form, paid_entry, adnotation_entry, adnotation_entry_pub, delivery, payment_method, term), top.destroy()])
    yes_button.pack(padx=10, pady=10, side='right')
    no_button = Button(top, text="Anuluj", command=lambda: top.destroy())
    no_button.pack(padx=10, pady=10, side='left')


def sum_up_edit_product(product_id, product_brand, product_model, product_colour, product_price, product_year, product_order_id, product_state, expected_delivery_str, expected_delivery, lasttop):
    #print(f"!{expected_delivery_str}!")
    if expected_delivery_str == "" or expected_delivery_str == None:
        #print("here")
        expected_delivery = None
    if not product_price:
        product_price = 0.0

    try:
        product_price = product_price.replace(',', '.', 1)
    except:
        pass

    if not product_brand or not product_model or not product_colour or not product_year:
        messagebox.showerror("Error", "Wypełnij pole Marka, Model, Rocznik, Kolor oraz Ilość")
        return

    try:
        product_price = float(product_price)
        product_price = round(product_price, 2)
        product_model = str(product_model)
        product_colour = str(product_colour)
        product_brand = str(product_brand)
        product_order_id = str(product_order_id)
        product_year = int(product_year)
        if product_year < 1000:
            product_year+=2000
    except ValueError:
        messagebox.showerror("Error", "Niewłaściwie podane dane")
        return

    product = con.get_product(product_id)

    changes = "Zmiany:\n"
    if product_brand != product.brand: 
        changes = changes+f"Marka: {product.brand} 🡢 {product_brand}\n"

    if product_model != product.model: 
        changes = changes+f"Model: {(product.model)} 🡢 {(product_model)}\n"

    if product_colour != product.colour: 
        changes = changes+f"Kolor: {(product.colour)} 🡢 {(product_colour)}\n"

    if product_price != product.price: 
        changes = changes+f"Cena: {short_price(product.price)} 🡢 {short_price(product_price)}\n"
        old_price = product_price
    else:
        old_price = product.old_price
        
    if product_year != product.year: 
        changes = changes+f"Roczni: {(product.year)} 🡢 {(product_year)}\n"

    if product_order_id != product.order_id: 
        changes = changes+f"Nr. zamówienia: {(product.order_id)} 🡢 {(product_order_id)}\n"

    if product_state != product.state: 
        changes = changes+f"Stan: {(product.state)} 🡢 {(product_state)}\n"

    if product.expected_delivery is None:
        og_delivery = None
    else:
        og_delivery = product.expected_delivery.strftime('%d.%m.%Y')

    if expected_delivery is None:
        fdelivery = None
    else:
        fdelivery = expected_delivery.strftime('%d.%m.%Y')

    if fdelivery != og_delivery: 
        changes = changes+f"Przewidywana dostawa: {og_delivery} 🡢 {fdelivery}\n"

    if changes == "Zmiany:\n": 
        messagebox.showerror("Error", "Wprowadź zmiany", parent=lasttop)
        return
    
    lasttop.destroy()
    top = Toplevel()

    changes_label = Label(top, text=changes, font=("Default", 12), justify='left')
    changes_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)
    yes_button = Button(top, text="Potwierdź", command=lambda: [con.edit_product(product_id, product_brand, 
    product_model, product_colour, product_price, product_year, product_order_id, product_state, expected_delivery, old_price), top.destroy()])
    yes_button.grid(row=4, column=3, padx=15, pady=15, sticky="e")
    no_button = Button(top, text="Anuluj", command=lambda: [top.destroy()])
    no_button.grid(row=4, column=0, padx=15, pady=15, sticky="w")


def sum_up_edit_customer(customer_id, new_customer_name, new_customer_phone, new_customer_email, new_customer_pesel, new_customer_nip, company_name, adress, lasttop):

    new_customer_email=str(new_customer_email)
    new_customer_phone=str(new_customer_phone)
    new_customer_phone=new_customer_phone.replace(' ', '')
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_customer_email)
    new_customer_phone = new_customer_phone.replace(" ", "")
    valid_phone = re.match("^\\+?[1-9][0-9]{7,14}$", new_customer_phone)
    valid_nip = validate_nip(new_customer_nip)
    valid_pesel = validate_pesel(new_customer_pesel)
    if new_customer_name=="":
        messagebox.showerror("Error", "Wprowadź imię i nazwisko", parent=lasttop)
        return
    if " " not in new_customer_name:
        messagebox.showerror("Error", "Wporwadź poprawne imię i nazwisko", parent=lasttop)
        return
    if not valid_phone or new_customer_phone=="":
        messagebox.showerror("Error", "Wprowadź poprwany numer telefonu", parent=lasttop)
        return
    if not valid and not new_customer_email=="":
        messagebox.showerror("Error", "Wprowadź poprawny adres email", parent=lasttop)
        return
    if valid_pesel == "invalid":
        messagebox.showerror("Error", "Wprowadź poprawny numer PESEL", parent=lasttop)
        return
    if valid_nip=='invalid':
        messagebox.showerror("Error", "Wprowadź poprawny NIP", parent=lasttop)
        return
    if  (valid_nip != "" and company_name == "") or (valid_nip == "" and company_name != ""):
        messagebox.showerror("Error", "Wprowadź NIP wraz z nazwą firmy", parent=lasttop)
        return
        
    customer = con.get_customer(customer_id)

    changes = "Zmiany:\n"

    if customer.name != new_customer_name: 
        changes = changes+f"Imię i nazwisko: {customer.name} 🡢 {new_customer_name}\n"

    if customer.phone != new_customer_phone: 
        changes = changes+f"Nr. tel: {customer.phone} 🡢 {new_customer_phone}\n"

    if customer.email != new_customer_email:
        changes = changes+f"Email: {customer.email} 🡢 {new_customer_email}\n"

    if customer.pesel != valid_pesel: 
        changes = changes+f"PESEL: {customer.pesel} 🡢 {valid_pesel}\n"

    if customer.company_name != company_name: 
        changes = changes+f"Nazwa firmy: {customer.company_name} 🡢 {company_name}\n"

    if customer.nip != valid_nip: 
        changes = changes+f"NIP: {customer.nip} 🡢 {valid_nip}\n"

    if customer.adress != adress: 
        changes = changes+f"Adres: \n {customer.adress} \n 🡣 \n{adress}\n"


    if changes == "Zmiany:\n": 
        messagebox.showerror("Error", "Wprowadź zmiany", parent=lasttop)
        return

    lasttop.destroy()
    top = Toplevel()

    label = Label(top, text=changes, font=("Default", 12), justify='left')
    label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    yes_button = Button(top, text="Potwierdź", command=lambda: [con.edit_customer(customer_id, new_customer_name, 
    new_customer_phone, new_customer_email, valid_pesel, valid_nip, company_name, adress), top.destroy()])
    yes_button.grid(row=4, column=3, padx=15, pady=15, sticky="e")
    no_button = Button(top, text="Anuluj", command=lambda: [top.destroy()])
    no_button.grid(row=4, column=0, padx=15, pady=15, sticky="w")


'''
def change_group_date_by_spec(tree, lasttop):
    selection = tree.selection()
    if len(selection) == 0:
        messagebox.showerror("Error", "Wybierz elementy.")
    old_date = tree.item(selection[0], 'values')[5]
    for item in selection:
        if tree.item(item, 'values')[5] != old_date:
            messagebox.showerror("Error", "Wybierz elementy z tej samej dostawy.")
            return

    top = Toplevel(lasttop)
    top.title("Zmień datę")

    product_expected_delivery_entry = DateEntry(top, date_pattern='dd.mm.yyyy', showweeknumbers=False, selectmode='day',
        font=("Default", 12),
        weekendbackground = "#E5E5E5", 
        weekendforeground = "#000000",
        othermonthbackground = "#8F8F8F",
        othermonthforeground = "#4A4A4A",
        othermonthwebackground = "#8F8F8F",
        othermonthweforeground = "#4A4A4A")
    product_expected_delivery_entry.grid(row=0, column=0, padx=15, pady=15, sticky="ew", columnspan = 2)
    product_expected_delivery_entry.delete(0, END)
    product_expected_delivery_entry.insert(0, old_date)

    products = con.get_all_products()

    products_filtered = []
    for product in products:
        tuprod = ()
'''

def change_group_date_by_id(tree, lasttop):
    selection = tree.selection()
    if len(selection) == 0:
        messagebox.showerror("Error", "Wybierz elementy.")
        return
    old_date = tree.item(selection[0], 'values')[9]
    for item in selection:
        if tree.item(item, 'values')[9] != old_date:
            messagebox.showerror("Error", "Wybierz elementy z tej samej dostawy.")
            return

    top = Toplevel(lasttop)
    top.title("Zmień datę")

    product_expected_delivery_entry = cal.DateEntry(top, date_pattern='dd.mm.yyyy', showweeknumbers=False, selectmode='day',
        font=("Default", 12),
        weekendbackground = "#E5E5E5", 
        weekendforeground = "#000000",
        othermonthbackground = "#8F8F8F",
        othermonthforeground = "#4A4A4A",
        othermonthwebackground = "#8F8F8F",
        othermonthweforeground = "#4A4A4A")
    product_expected_delivery_entry.grid(row=0, column=0, padx=15, pady=15, sticky="ew", columnspan = 2)
    product_expected_delivery_entry.delete(0, END)
    product_expected_delivery_entry.insert(0, old_date)

    id_list = [tree.item(item, 'value')[0] for item in selection]

    yes_button = Button(top, text="Potwierdź", command= lambda: [change_dates(id_list, product_expected_delivery_entry.get_date()), top.destroy()])
    yes_button.grid(row=1, column=1, padx=10, pady=10)

    no_button = Button(top, text="Anuluj", command= lambda: [top.destroy()])
    no_button.grid(row=1, column=0, padx=10, pady=10)