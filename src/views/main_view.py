from tkinter import ttk, messagebox, Toplevel, Label, Button, IntVar, Checkbutton, Text, WORD, StringVar, OptionMenu, END, BooleanVar, Frame
import tkcalendar as cal
import babel.numbers
import src.controllers as con
import src.utils.funcs as fun
import src.utils.buttons as but
import time
from datetime import datetime
from PIL import Image, ImageTk
from src import resource_path
import os
import json
from dateutil.relativedelta import relativedelta


class main_window:    
    def __init__(self, root):
        self.root = root
        self.root.title("Zamówienia Motorland")
        self.root.geometry("1500x900")
		

        ico = Image.open(resource_path(os.path.join('static', 'icon.png')))
        photo = ImageTk.PhotoImage(ico)
        root.wm_iconphoto(False, photo)
		
        notebook = ttk.Notebook(self.root)

        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)
        tab4 = ttk.Frame(notebook)
        tab5 = ttk.Frame(notebook)
        tab6 = ttk.Frame(notebook)

        notebook.add(tab1, text="Wolne Pojazdy")
        notebook.add(tab5, text="Wszystkie Pojazdy")
        notebook.add(tab2, text="Klienci")
        notebook.add(tab3, text="Rezerwacje")
        notebook.add(tab4, text="Zamówienie")
        notebook.add(tab6, text="Dodaj Pojazd")

        self.create_free_products_tab(tab1)
        self.create_all_products_tab(tab5)
        self.create_customers_tab(tab2)
        self.create_reservations_tab(tab3)
        self.create_add_product_tab(tab4)
        self.create_add_option_tab(tab6)

        
        fun.refresh_table(self.free_products_tree, self.free_prod_search_entry.get(), self.split_dates.get(), 
        self.customers_tree, self.customers_search_entry.get(), self.reservations_tree, self.reservation_search_entry.get(),
        self.show_finalized, self.all_products_tree, self.show_sold, self.show_reserved.get(), self.all_prod_search_entry.get(), 
        self.show_year.get(), self.show_year_free.get())
        ''''''

        

        notebook.pack(padx=10, pady=10, fill="both", expand=True)
        

    
    def create_free_products_tab(self, tab):
        filters_frame = ttk.Frame(tab)
        filters_frame.pack(fill='x')
        
        self.split_dates = BooleanVar()
        split_dates_button = Checkbutton(filters_frame, variable=self.split_dates, text="Rozdziel przewidywane daty", 
        onvalue=True, offvalue=False, command=lambda: con.fake_commit())
        split_dates_button.grid(padx=10, pady=(10, 0), row = 0, column=2)
        split_dates_button.select()

        self.show_year_free = StringVar()
        year_options = [str(year) for year in range(2023, datetime.now().year+2) ] + ['wszystkie']
        self.show_year_free.set("wszystkie")
        self.show_year_free.trace_add("write", lambda x, y, z: con.fake_commit())
        show_year_label = Label(filters_frame, text="Rok:", justify='left')
        show_year_label.grid(padx=10, pady=(10, 0), row = 0, column = 0)
        show_year_dropdown = OptionMenu(filters_frame, self.show_year_free, *year_options)
        show_year_dropdown.grid(padx=10, pady=(10, 0), row = 0, column = 1)

        self.free_products_tree = ttk.Treeview(tab, columns=("brand", "model", "year", "colour", 
        "free_count", "date", "price"), show="headings")
        self.free_products_tree.heading("brand", text="Marka")
        self.free_products_tree.heading("model", text="Model")
        self.free_products_tree.heading("year", text="Rocznik")
        self.free_products_tree.heading("colour", text="Kolor")
        self.free_products_tree.heading("free_count", text="Liczba")
        self.free_products_tree.heading("date", text="Dostawa")
        self.free_products_tree.heading("price", text="Najw. Cena")

        self.free_products_tree.column("brand", width=100)
        self.free_products_tree.column("model", width=125)
        self.free_products_tree.column("year", width=75)
        self.free_products_tree.column("colour", width=150)
        self.free_products_tree.column("free_count", width=30)
        self.free_products_tree.column("date", width=80)
        self.free_products_tree.column("price", width=60)

        self.free_products_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.free_products_tree.bind("<Double-1>", lambda x: self.create_reservation( 
        fun.get_product_specs_id(self.free_products_tree), "NIE", self.root))

        create_reservation_button = Button(tab, text="Zarezerwuj", command=lambda: self.create_reservation( 
        fun.get_product_specs_id(self.free_products_tree), "NIE", self.root))
        create_reservation_button.pack(padx=10, pady=(0, 10), side="right")
        '''
        change_date_button = Button(tab, text="Zmień datę", command=lambda: but.change_group_date_by_spec(self.free_products_tree, self.root))
        change_date_button.pack(padx=10, pady=(0, 10), side="right")
        '''
        free_prod_search_label = Label(tab, text="Wyszukaj:")
        free_prod_search_label.pack(padx=(15, 10), pady=(0, 10), side="left")
        self.free_prod_search_entry = ttk.Entry(tab)
        self.free_prod_search_entry.pack(padx=10, pady=(10, 20), fill="x")
        self.free_prod_search_entry.bind("<KeyRelease>", lambda x: con.fake_commit())



    def create_all_products_tab(self, tab):
        filters_frame = ttk.Frame(tab)
        filters_frame.pack(fill='x')
        self.show_sold = IntVar()
        Button1 = Checkbutton(filters_frame, text = "Pokaż wydane pojazdy", 
                    variable = self.show_sold, onvalue = 1, offvalue = 0,
                    command=lambda: con.fake_commit())

        Button1.grid(row=0, column=0, padx=20, pady=(10, 0),  sticky="w")

        self.show_reserved = StringVar()
        reserved_options = ["wszystkie", "zarezerwowane", "niezarezerwowane"]
        self.show_reserved.set("wszystkie")
        self.show_reserved.trace_add("write", lambda x, y, z: con.fake_commit())
        show_reserved_label = Label(filters_frame, text="Pokaż:", justify='left')
        show_reserved_label.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="e")
        show_reserved_dropdown = OptionMenu(filters_frame, self.show_reserved, *reserved_options)
        show_reserved_dropdown.grid(row=0, column=2, padx=0, pady=(10, 0), sticky="ew")

        self.show_year = StringVar()
        year_options = [str(year) for year in range(2023, datetime.now().year+2) ] + ['wszystkie']
        self.show_year.set("wszystkie")
        self.show_year.trace_add("write", lambda x, y, z: con.fake_commit())
        show_year_label = Label(filters_frame, text="Rok:", justify='left')
        show_year_label.grid(row=0, column=3, padx=10, pady=(10, 0), sticky="e")
        show_year_dropdown = OptionMenu(filters_frame, self.show_year, *year_options)
        show_year_dropdown.grid(row=0, column=4, padx=0, pady=(10, 0), sticky="ew")

        self.all_products_tree = ttk.Treeview(tab, columns=("id", "brand", "model", "year", 
        "colour", "price", "state", "added_on", "reservation", "expected_delivery", "order_id"), show="headings")

        self.all_products_tree["displaycolumns"]=("brand", "model", "year", 
        "colour", "price", "state", "added_on", "reservation", "expected_delivery", "order_id")



        self.all_products_tree.heading("brand", text="Marka")
        self.all_products_tree.heading("model", text="Model")
        self.all_products_tree.heading("year", text="Rocznik")
        self.all_products_tree.heading("colour", text="Kolor")
        self.all_products_tree.heading("price", text="Cena")
        self.all_products_tree.heading("state", text="Stan")
        self.all_products_tree.heading("added_on", text="Dodany")
        self.all_products_tree.heading("reservation", text="Rezerwacja")
        self.all_products_tree.heading("expected_delivery", text="Dostawa")
        self.all_products_tree.heading("order_id", text="Nr Zamówienia")
    
        self.all_products_tree.column("brand", width="100")
        self.all_products_tree.column("model", width="150")
        self.all_products_tree.column("year", width="51")
        self.all_products_tree.column("colour", width="150")
        self.all_products_tree.column("price", width="80")
        self.all_products_tree.column("state", width="100")
        self.all_products_tree.column("reservation", width="85")
        self.all_products_tree.column("added_on", width="115")
        self.all_products_tree.column("order_id", width="90")
        self.all_products_tree.column("expected_delivery", width="75")

        self.all_products_tree.bind("<Double-1>", lambda x:[self.create_reservation( 
        fun.get_selected_element_id(self.all_products_tree), fun.get_is_reserved(self.all_products_tree), self.root)])

        self.all_products_tree.column("order_id", width="150")
        self.all_products_tree.pack(fill="both", expand=True, padx=10, pady=10)

        delete_button = Button(tab, text="Usuń", 
        command=lambda: [but.delete_product(fun.get_selected_element_id(self.all_products_tree), 
        fun.get_is_reserved(self.all_products_tree), self.root)])
        delete_button.pack(pady=(0, 10), padx=10, side="left")

        change_state_button = Button(tab, text="Edytuj", command=lambda: [self.edit_product(fun.get_selected_element_id(self.all_products_tree), 
        self.root)])
        change_state_button.pack(padx=10, pady=(0, 10), side="right")

        change_date_button = Button(tab, text="Zmień datę", command=lambda: but.change_group_date_by_id(self.all_products_tree, self.root))
        change_date_button.pack(padx=10, pady=(0, 10), side="right")

        create_reservation_button = Button(tab, text="Zarezerwuj", command=lambda: self.create_reservation( 
        fun.get_selected_element_id(self.all_products_tree), fun.get_is_reserved(self.all_products_tree), self.root))
        create_reservation_button.pack(padx=10, pady=(0, 10), side="right")

        all_prod_search_label = Label(tab, text="Wyszukaj:")
        all_prod_search_label.pack(padx=(15, 10), pady=(0, 10), side="left")
        self.all_prod_search_entry = ttk.Entry(tab)
        self.all_prod_search_entry.pack(padx=10, pady=(5, 15), fill="x")
        self.all_prod_search_entry.bind("<KeyRelease>", lambda x: con.fake_commit())


    def create_customers_tab(self, tab):
        self.customers_tree = ttk.Treeview(tab, columns=("id", "name", "phone", "email", "pesel", "adress", "company_name", "nip", "added_on"), show="headings")
        self.customers_tree["displaycolumns"]=("name", "phone", "email", "pesel", "adress", "company_name", "nip")
        self.customers_tree.heading("id", text="ID")
        self.customers_tree.heading("name", text="Imię i Nazwisko")
        self.customers_tree.heading("phone", text="Nr.Tel.")
        self.customers_tree.heading("email", text="Email")
        self.customers_tree.heading("pesel", text="PESEL")
        self.customers_tree.heading("nip", text="NIP")
        self.customers_tree.heading("adress", text="Adres")
        self.customers_tree.heading("company_name", text="Nazwa firmy")

        self.customers_tree.column("name", width="150")
        self.customers_tree.column("phone", width="55")
        self.customers_tree.column("email", width="170")
        self.customers_tree.column("pesel", width="50")
        self.customers_tree.column("nip", width="60")
        self.customers_tree.column("adress", width="100")
        self.customers_tree.column("company_name", width="120")

        self.customers_tree.bind("<Double-1>", lambda x: but.on_customer_click(self.root))
        self.customers_tree.pack(fill="both", expand=True, padx=10, pady=10)

        edit_button = Button(tab, text="Edytuj", command=lambda: self.edit_customer(fun.get_selected_element_id(self.customers_tree), self.root))
        edit_button.pack(padx=10, pady=10, side="right")

        create_new_customer_button = Button(tab, text="Dodaj klienta", command=lambda: self.create_new_customer(self.root))
        create_new_customer_button.pack(side="right", padx=10, pady=10)

        delete_button = Button(tab, text="Usuń", 
        command=lambda: [but.delete_customer(fun.get_selected_element_id(self.customers_tree), self.root)])
        delete_button.pack(pady=10, padx=10, side="left")

        
        customers_search_label = Label(tab, text="Wyszukaj:", padx=10)
        customers_search_label.pack(padx=0, pady=10, side="left")
        self.customers_search_entry = ttk.Entry(tab)
        self.customers_search_entry.pack(padx=10, pady=20, fill="x")
        self.customers_search_entry.bind("<KeyRelease>", lambda x: con.fake_commit())


    def create_new_customer(self, lasttop, callback = None, select = lambda: []):
        top = Toplevel(lasttop)
        top.title("Dodaj nowego klienta")
        top.columnconfigure(0, weight=0)
        top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)
        top.rowconfigure(1, weight=1)
        top.rowconfigure(2, weight=1)
        top.rowconfigure(3, weight=1)
        top.rowconfigure(4, weight=1)
        
        name_label = Label(top, text="Imię i Nazwisko:*")
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w") 

        name_entry = ttk.Entry(top)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew") 
        
        phone_label = Label(top, text="Numer telefonu:*")
        phone_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        phone_entry = ttk.Entry(top)
        phone_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        
        email_label = Label(top, text="Email:")
        email_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        email_entry = ttk.Entry(top)
        email_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        pesel_label = Label(top, text="PESEL:")
        pesel_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        pesel_entry = ttk.Entry(top)
        pesel_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        company_name_label = Label(top, text="Nazwa firmy:")
        company_name_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        company_name_entry = ttk.Entry(top)
        company_name_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        nip_label = Label(top, text="NIP:")
        nip_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        nip_entry = ttk.Entry(top)
        nip_entry.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

        adress_label = Label(top, text="Adres:")
        adress_label.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        adress_entry = Text(top, wrap=WORD, height=5)
        adress_entry.grid(row=6, column=1, padx=10, pady=10, sticky="ew")

        add_button = Button(top, text="Dodaj", command=lambda:[but.sum_up_customer(name_entry.get().strip(), 
            phone_entry.get().strip(), email_entry.get().strip(), pesel_entry.get().strip(), nip_entry.get().strip(), 
            company_name_entry.get().strip(), adress_entry.get('1.0', 'end').strip(), top),
            select()])
        add_button.grid(row=7, column=1, padx=10, pady=10, sticky="e")

        
        #top.geometry(f"400x{top.winfo_reqheight()+70}")

        lasttop.wait_window(top)

        if callback:
            callback()


    def create_reservations_tab(self, tab):
        
        self.show_finalized = IntVar()
        Button1 = Checkbutton(tab, text = "Pokaż ukończone transakcje", 
                    variable = self.show_finalized, onvalue = 1, offvalue = 0,
                    command=lambda: con.fake_commit())

        Button1.pack()
        
        self.reservations_tree = ttk.Treeview(tab, columns=("id", "string_order_id", "name",
        "date",  "brand", "model", "colour", "adnotations"), show="tree headings")
        
        self.reservations_tree["displaycolumns"]=("string_order_id", "name", 
        "date", "brand", "model", "colour", "adnotations")

        self.reservations_tree.heading("#0", text="$")
        self.reservations_tree.heading("id", text="ID")
        self.reservations_tree.heading("string_order_id", text="ID")
        self.reservations_tree.heading("name", text="Imię i Nazwisko")
        self.reservations_tree.heading("date", text="Data")
        self.reservations_tree.heading("brand", text="Marka")
        self.reservations_tree.heading("model", text="Model")
        self.reservations_tree.heading("colour", text="Kolor")
        self.reservations_tree.heading("adnotations", text="Uwagi")

        self.reservations_tree.column("#0", width=62, stretch=False, anchor='w')
        self.reservations_tree.column("id", width=62, stretch=False, anchor='center')
        self.reservations_tree.column("string_order_id", width=70, stretch=False, anchor='center')
        self.reservations_tree.column("name", width=100)
        self.reservations_tree.column("date", width=100)
        self.reservations_tree.column("brand", width=100)
        self.reservations_tree.column("model", width=100)
        self.reservations_tree.column("colour", width=100)
        self.reservations_tree.column("adnotations")

        self.reservations_tree.bind("<Double-1>", lambda x: self.show_reservation_details(fun.get_selected_element_id(self.reservations_tree), self.root))

        green_icon = fun.create_colored_icon("#03C04A")
        red_icon = fun.create_colored_icon("#FF2800")
        self.reservations_tree.icons = {True: green_icon, False: red_icon}

        self.reservations_tree.pack(fill="both", expand=True, padx=10, pady=10)

        delete_button = Button(tab, text="Usuń", 
        command=lambda: [but.delete_reservation(fun.get_selected_element_id(self.reservations_tree), self.root)])
        delete_button.pack(pady=10, padx=10, side="left")

        show_more_button = Button(tab, text="Pokaż szczegóły", command=lambda: self.show_reservation_details(fun.get_selected_element_id(self.reservations_tree), self.root))
        show_more_button.pack(padx=10, pady=10, side="right")


        reservation_search_label = Label(tab, text="Wyszukaj:", padx=10)
        reservation_search_label.pack(padx=0, pady=10, side="left")
        self.reservation_search_entry = ttk.Entry(tab)
        self.reservation_search_entry.pack(padx=10, pady=20, fill="x")
        self.reservation_search_entry.bind("<KeyRelease>", lambda x: con.fake_commit())


    def show_reservation_details(self, res_id, lasttop):
        if res_id == -1:
            messagebox.showerror("Error", "Wybierz rezerwację")
            return

        top=Toplevel(lasttop)
        top.title("Szczegóły rezerwacji")
        reservarion = con.get_reservation(res_id)

        if reservarion.Reservation.paid: spaid="Zapłacono"
        else: spaid="Nie zapłacono"

        if reservarion.Reservation.delivery: sdel = "Tak"
        else: sdel = "Nie"

        if reservarion.Reservation.form: sform="Zadatek"
        else: sform="Zaliczka"

        try:
            expected_delivery = reservarion.Product.expected_delivery.strftime('%d.%m.%Y')
        except:
            expected_delivery = ""
        
        main_frame = ttk.Frame(top)
        main_frame.pack(padx=10, pady=10, fill='x')
        
        details = [
            ("Imię i Nazwisko:", reservarion.Customer.name),
            ("Numer tel:", reservarion.Customer.phone),
            ("Email:", reservarion.Customer.email),
            ("PESEL:", reservarion.Customer.pesel),
            ("Adres:", reservarion.Customer.adress),
            ("Nazwa firmy:", reservarion.Customer.company_name),
            ("NIP:", reservarion.Customer.nip),
            ("Marka:", reservarion.Product.brand),
            ("Model:", reservarion.Product.model),
            ("Kolor:", reservarion.Product.colour),
            ("Rocznik:", reservarion.Product.year),
            ("Cena:", fun.short_price(reservarion.Product.price)),
            ("Metoda płatności:", reservarion.Reservation.payment_method),
            ("Wartość zaliczki:", fun.short_price(reservarion.Reservation.advance)),
            ("Forma:", sform),
            ("Rozlicenie:", spaid),
            ("Przewidywana dostawa:", expected_delivery),
            ("Data realizacji na umowie:", reservarion.Reservation.term),
            ("Dostawa:", sdel),
            ("Uwagi do rezerwacji:", reservarion.Reservation.adnotation),
            ("Uwagi dla klienta:", reservarion.Reservation.adnotation_pub),
            ("Data rezerwacji:", reservarion.Reservation.date.strftime('%d.%m.%Y %H:%M'))
        ]
        i=0
        

        for label_text, value_text in details:
            if value_text == "" or value_text is None:
                continue
            if i%2 == 1: 
                col = "#5E5E5E"
                fr = 1
            else:
                fr=1
                col = "#4FC3F7"
            i+=1
            detail_frame = Frame(main_frame, highlightbackground=col, highlightthickness=fr)
            #detail_frame['borderwidth'] = 1
            #detail_frame['relief'] = 'solid'
            detail_frame.pack(fill='x', pady=2)
            
            lbl = Label(detail_frame, 
                    text=label_text,
                    font=("Default", 12),
                    anchor='w',
                    width=25, 
                    justify='left')
            lbl.pack(side='left', padx=(10, 10))
            
            val = Label(detail_frame, 
                    text=value_text,
                    font=("Default", 12),
                    anchor='w',
                    wraplength=550,
                    justify='left')
            val.pack(side='left', fill='x', expand=True, padx=(0, 10))
            val.bind("<Button-3>", lambda x: fun.show_copy_menu(x, x.widget, top))
        

        edit_button = Button(top, text="Edytuj", command=lambda: self.edit_reservation(res_id, top))
        edit_button.pack(padx=10, pady=(0, 10), side='right')

        change_state_button = Button(top, text="Zmień stan pojazdu", command=lambda: but.change_state(reservarion.Product.id, top))
        change_state_button.pack(padx=10, pady=(0, 10), side='left')

        generate_confirmation_button = Button(top, text="Generuj potwierdzenie", command=lambda: fun.generate_pdf_confirmation(res_id))
        generate_confirmation_button.pack(padx=0, pady=(0, 10), side='left')


    def create_reservation(self, to_reservation_id, is_reserved, lasttop):
        if is_reserved == "TAK":
            messagebox.showerror("Error", "Ten pojazd jest już zarezerwowany")
        else:
            if to_reservation_id == -1:
                messagebox.showerror("Error", "Wybierz produkt")
                return

            to_reservation = con.get_product(to_reservation_id)

            top = Toplevel(lasttop)
            top.title("Utwórz rezerwację")

            top.grid_rowconfigure(0, weight=0)
            top.grid_rowconfigure(1, weight=1)
            top.grid_rowconfigure(2, weight=0)
            top.grid_rowconfigure(3, weight=1)
            top.grid_rowconfigure(4, weight=0)
            top.grid_columnconfigure(0, weight=1)
            top.grid_columnconfigure(1, weight=1)

            tytul_rezerwacji = Label(top, text=f"Zarezerwuj {to_reservation.brand} {to_reservation.model} "\
                f"{to_reservation.year} {to_reservation.colour}", font=("Default", 14))
            tytul_rezerwacji.grid(row=0, column=0, columnspan=2, pady=(10, 0), sticky="nsew") 

            customer_frame = ttk.Frame(top)
            customer_frame.grid(row=1, columnspan=2, column=0, padx=10, pady=10, sticky="nsew")
            customer_frame.grid_rowconfigure(0, weight=1)
            customer_frame.grid_columnconfigure(0, weight=1)

            res_customers_tree = ttk.Treeview(customer_frame, columns=("id", "name", "phone", "email"), show="headings")
            res_customers_tree["displaycolumns"]=("name", "phone", "email")
            res_customers_tree.heading("id")
            res_customers_tree.heading("name", text="Imię i Nazwisko")
            res_customers_tree.heading("phone", text="Nr.Tel.")
            res_customers_tree.heading("email", text="Email")

            res_customers_tree.grid(row=0, column=0, sticky="nsew", padx=0, pady=0) #row1??? columnspan=2, 

            fun.refresh_res_customer(res_customers_tree)

            customer_addons_frame = ttk.Frame(top)
            customer_addons_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
            customer_addons_frame.grid_rowconfigure(0, weight=0)
            customer_addons_frame.grid_columnconfigure(0, weight=0)
            customer_addons_frame.grid_columnconfigure(1, weight=1)
            customer_addons_frame.grid_columnconfigure(2, weight=0)


            search_label = Label(customer_addons_frame, text="Wyszukaj:", padx=10)
            search_label.grid(row=0, column=0, sticky="w", pady=(0, 0))
            search_entry = ttk.Entry(customer_addons_frame)
            search_entry.grid(row=0, column=1, padx=10, pady=(0, 0), sticky="ew")
            search_entry.bind("<KeyRelease>", lambda x: fun.filter_tree(search_entry, con.get_all_customers(), res_customers_tree, "name")) #SERVER albo inna optymalizacja

            new_customer_button = Button(customer_addons_frame, text="Nowy klient", 
            command=lambda: self.create_new_customer(top, None, 
            lambda: [search_entry.delete(0, END), res_customers_tree.selection_set(fun.refresh_res_customer(res_customers_tree))]))
            new_customer_button.grid(row=0, column=2, padx=10, pady=(0, 0), sticky="e")

            reservation_frame = ttk.Frame(top)
            reservation_frame.grid(row=3, columnspan=2, column=0, padx=10, pady=0, sticky="nsew")
            reservation_frame.grid_rowconfigure(0, weight=0)
            reservation_frame.grid_rowconfigure(1, weight=0)
            reservation_frame.grid_rowconfigure(2, weight=0)
            reservation_frame.grid_rowconfigure(3, weight=1)
            reservation_frame.grid_rowconfigure(4, weight=1)
            reservation_frame.grid_columnconfigure(0, weight=0)
            reservation_frame.grid_columnconfigure(1, weight=1)
            reservation_frame.grid_columnconfigure(2, weight=0)
            reservation_frame.grid_columnconfigure(3, weight=1)

            reservation_advance_label = Label(reservation_frame, text = "Wartość zaliczki:")
            reservation_advance_entry = ttk.Entry(reservation_frame)

            reservation_advance_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            reservation_advance_entry.grid(row=0, column=1, padx=0, pady=10, sticky="ew")

            new_price_label = Label(reservation_frame, text = "Ustalona cena:")
            new_price_entry = ttk.Entry(reservation_frame)

            new_price_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
            new_price_entry.grid(row=1, column=1, padx=0, pady=(0, 10), sticky="ew")
            new_price_entry.insert(0, fun.short_price(to_reservation.price))

            reservation_form = StringVar()
            reservation_form.set('zaliczka/zadatek')
            form_box=OptionMenu(reservation_frame, reservation_form, *['zaliczka', 'zadatek'])
            form_box.grid(row=0, column=2, padx=0, pady=10, columnspan=2)

            payment_method = StringVar()
            payment_method.set('płatność')
            banks_json=json.load(open(resource_path("static/acc_numbers.json"), "r", encoding="utf-8"))
            banks = ['gotówka', 'karta']+list(banks_json.keys())
            payment_method_box=OptionMenu(reservation_frame, payment_method, *banks)
            payment_method_box.grid(row=1, column=2, padx=0, pady=(0, 10), columnspan=2)

            checkbuttons_frame = ttk.Frame(reservation_frame)
            checkbuttons_frame.grid(row=2, column=2, padx=0, pady=(0, 10), columnspan=2)

            reservation_paid = BooleanVar()
            paid_button = Checkbutton(checkbuttons_frame, text="Zapłacono", variable=reservation_paid, offvalue=False, onvalue=True)
            paid_button.grid(row=0, column=0, padx=10, pady=0, columnspan=1)
            
            delivery = BooleanVar()
            delivery_button = Checkbutton(checkbuttons_frame, text="Dostawa", variable=delivery, offvalue=False, onvalue=True)
            delivery_button.grid(row=0, column=1, padx=10, pady=0, columnspan=1)
            
            term_label = Label(reservation_frame, text = "Termin realizacji:")
            term_entry = ttk.Entry(reservation_frame)

            term_label.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="w")
            term_entry.grid(row=2, column=1, padx=0, pady=(0, 10), columnspan=2, sticky="ew")

            POLISH_MONTHS = [
                "Styczeń", "Luty", "Marzec", "Kwiecień",
                "Maj", "Czerwiec", "Lipiec", "Sierpień",
                "Wrzesień", "Październik", "Listopad", "Grudzień"
            ]   
            
            if to_reservation.expected_delivery is not None:
                if to_reservation.expected_delivery.day > 15: double_term = True
                else: double_term = False
                month_index = to_reservation.expected_delivery.month - 1
                if double_term:
                    next_month_date = to_reservation.expected_delivery + relativedelta(months=+1)
                    next_month_index = next_month_date.month - 1
                    term_entry.insert(0, f"{POLISH_MONTHS[month_index]} {to_reservation.expected_delivery.year}r. / {POLISH_MONTHS[next_month_index]} {next_month_date.year}r.")
                else:
                    term_entry.insert(0, f"{POLISH_MONTHS[month_index]} {to_reservation.expected_delivery.year}r.")

            adnotation_label = Label(reservation_frame, text = "Uwagi:")
            adnotation_entry = Text(reservation_frame, wrap=WORD, height=5)

            adnotation_label.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="w")
            adnotation_entry.grid(row=3, column=1, padx=0, pady=(0, 10), sticky="nsew", columnspan=3)

            adnotation_pub_label = Label(reservation_frame, text = "Uwagi dla klienta:")
            adnotation_pub_entry = Text(reservation_frame, wrap=WORD, height=5)

            adnotation_pub_label.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="w")
            adnotation_pub_entry.grid(row=4, column=1, padx=0, pady=(0, 10), sticky="nsew", columnspan=3)
            
            cancel_button = Button(top, text="Anuluj", command=lambda: top.destroy())
            cancel_button.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="w")

            make_button = Button(top, text="Zarezerwuj", command=lambda: [fun.confirm_reservation(to_reservation, fun.get_selected_element_id(res_customers_tree), 
                reservation_advance_entry.get().strip(), new_price_entry.get().strip(), adnotation_entry.get('1.0', 'end').strip(), adnotation_pub_entry.get('1.0', 'end').strip(),
                reservation_form.get(), reservation_paid.get(), term_entry.get().strip(), delivery.get(), payment_method.get(), top)])
            make_button.grid(row=4, column=1, padx=10, pady=(0, 10), sticky="e")
            
    
    def create_add_product_tab(self, tab):
        

        product_brand_label = ttk.Label(tab, text="Marka:*", justify="left")
        product_brand_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        product_brand_var = StringVar()
        self.product_brand_entry = ttk.Combobox(tab, textvariable = product_brand_var, state="readonly")
        self.product_brand_entry["values"] = con.get_brands_list()
        self.product_brand_entry.grid(row=0, column=1, padx=15, pady=15, sticky="w")


        product_model_label = ttk.Label(tab, text="Model:*", justify="left")
        product_model_label.grid(row=0, column=2, padx=15, pady=15, sticky="w")

        product_model_var = StringVar()
        self.product_model_entry = ttk.Combobox(tab, textvariable = product_model_var, state="readonly")
        self.product_model_entry.bind("<Button-1>", lambda x: fun.fill_models(self.product_model_entry, product_brand_var.get()))
        self.product_model_entry.grid(row=0, column=3, padx=15, pady=15, sticky="w")
        self.product_brand_entry.bind("<<ComboboxSelected>>", lambda x: self.product_model_entry.set(""))


        product_colour_label = ttk.Label(tab, text="Kolor:*", justify="left")
        product_colour_label.grid(row=1, column=0, padx=15, pady=15, sticky="w")

        product_colour_var = StringVar()
        self.product_colour_entry = ttk.Combobox(tab, textvariable = product_colour_var, state="readonly")
        self.product_colour_entry["values"] = con.get_colours_list()
        self.product_colour_entry.grid(row=1, column=1, padx=15, pady=15, sticky="w")
        
        
        product_price_label = ttk.Label(tab, text="Cena:", justify="left")
        product_price_label.grid(row=2, column=0, padx=15, pady=15, sticky="w")

        self.product_price_entry = ttk.Entry(tab)
        self.product_price_entry.grid(row=2, column=1, padx=15, pady=15, sticky="ew")


        product_year_label = ttk.Label(tab, text="Rocznik:*", justify="left")
        product_year_label.grid(row=1, column=2, padx=15, pady=15, sticky="w")

        self.product_year_entry = ttk.Entry(tab)
        self.product_year_entry.grid(row=1, column=3, padx=15, pady=15, sticky="ew")

        product_order_id_label = ttk.Label(tab, text="Nr zamówienia:", justify="left")
        product_order_id_label.grid(row=2, column=2, padx=15, pady=15, sticky="w")

        self.product_order_id_entry = ttk.Entry(tab)
        self.product_order_id_entry.grid(row=2, column=3, padx=15, pady=15, sticky="ew")
        
        product_quantity_label = ttk.Label(tab, text="Ilość:*", justify="left")
        product_quantity_label.grid(row=3, column=2, padx=15, pady=15, sticky="w")

        self.product_quantity_entry = ttk.Entry(tab)
        self.product_quantity_entry.insert(1, 1)
        self.product_quantity_entry.grid(row=3, column=3, padx=15, pady=15, sticky="ew")

        product_expected_delivery_label = ttk.Label(tab, text="Przewidywana dostawa:", justify="left")
        product_expected_delivery_label.grid(row=3, column=0, padx=15, pady=15, sticky="w")


        self.product_expected_delivery_entry = cal.DateEntry(tab, date_pattern='dd.mm.yyyy', showweeknumbers=False, selectmode='day',
            font=("Default", 12),
            weekendbackground = "#E5E5E5", 
            weekendforeground = "#000000",
            othermonthbackground = "#8F8F8F",
            othermonthforeground = "#4A4A4A",
            othermonthwebackground = "#8F8F8F",
            othermonthweforeground = "#4A4A4A")
        self.product_expected_delivery_entry.grid(row=3, column=1, padx=15, pady=15, sticky="ew")
        self.product_expected_delivery_entry.delete(0, END)

        add_button = Button(tab, text="Dodaj", command=lambda: [but.sum_up_product(product_brand_var.get().strip(), product_model_var.get().strip(),
            product_colour_var.get().strip(), self.product_price_entry.get().lower().strip(), self.product_year_entry.get().lower().strip(), self.product_order_id_entry.get().strip(),
            self.product_quantity_entry.get().strip(), self.product_expected_delivery_entry.get(), self.product_expected_delivery_entry.get_date()),
            self.product_brand_entry.set(""), self.product_model_entry.set(""), self.product_colour_entry.set(""), self.product_year_entry.delete(0, END), self.product_order_id_entry.delete(0, END), self.product_price_entry.delete(0, END), 
            self.product_expected_delivery_entry.delete(0, END), self.product_quantity_entry.delete(0, END), self.product_quantity_entry.insert(0,"1")])
        add_button.grid(row=4, column=0, padx=15, pady=15, sticky="w")

        
    def create_add_option_tab(self, tab):
        brand_label = Label(tab, text = "Dodaj markę: ")
        brand_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        brand_entry = ttk.Entry(tab)
        brand_entry.grid(row=0, column=1, padx=10, pady=10, columnspan=2, sticky="ew")
        brand_button = Button(tab, text="Dodaj", command=lambda: [but.add_brand(brand_entry.get(), self.product_brand_entry, self.add_model_brand_entry), brand_entry.delete(0, END)])
        brand_button.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        drop_brand_button = Button(tab, text="Usuń", command=lambda: [but.delete_brand(brand_entry.get(), self.product_brand_entry, self.add_model_brand_entry), brand_entry.delete(0, END)])
        drop_brand_button.grid(row=0, column=4, padx=10, pady=10, sticky="w")


        colour_label = Label(tab, text = "Dodaj kolor: ")
        colour_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        colour_entry = ttk.Entry(tab)
        colour_entry.grid(row=2, column=1, padx=10, pady=10, columnspan=2, sticky="ew")
        colour_button = Button(tab, text="Dodaj", command=lambda: [but.add_colour(colour_entry.get(), self.product_colour_entry), colour_entry.delete(0, END)])
        colour_button.grid(row=2, column=3, padx=10, pady=10, sticky="w")
        drop_colour_button = Button(tab, text="Usuń", command=lambda: [but.delete_colour(colour_entry.get(), self.product_colour_entry), colour_entry.delete(0, END)])
        drop_colour_button.grid(row=2, column=4, padx=10, pady=10, sticky="w")


        model_label = Label(tab, text = "Dodaj model: ")
        model_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        model_entry = ttk.Entry(tab)
        new_model_brand = StringVar()
        self.add_model_brand_entry=ttk.Combobox(tab, textvariable=new_model_brand, state="readonly")
        self.add_model_brand_entry["values"] = con.get_brands_list()
        self.add_model_brand_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        model_entry.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        model_button = Button(tab, text="Dodaj", command=lambda: [but.add_model(model_entry.get(), new_model_brand.get()), model_entry.delete(0, END), self.add_model_brand_entry.set('')])
        model_button.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        drop_model_button = Button(tab, text="Usuń", command=lambda: [but.delete_model(model_entry.get(), new_model_brand.get()), model_entry.delete(0, END), self.add_model_brand_entry.set('')])
        drop_model_button.grid(row=1, column=4, padx=10, pady=10, sticky="w")


    def edit_reservation(self, reservation_id, lasttop):
    
        if reservation_id == -1:
            messagebox.showerror("Error", "Wybierz produkt")
            return

        reservation = con.get_full_reservation(reservation_id)

        top = Toplevel()
        top.title("Edytuj rezerwację")
        lasttop.destroy()

        top.grid_rowconfigure(0, weight=0)
        top.grid_rowconfigure(1, weight=1)
        top.grid_rowconfigure(2, weight=0)
        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=1)

        tytul_rezerwacji = Label(top, text=f"Edytuj {reservation.Product.brand} {reservation.Product.model} "\
            f"dla {reservation.Customer.name}", font=("Default", 14))
        tytul_rezerwacji.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew") 

        reservation_frame = ttk.Frame(top)
        reservation_frame.grid(row=1, columnspan=2, column=0, padx=10, pady=10, sticky="nsew")
        reservation_frame.grid_rowconfigure(0, weight=0)
        reservation_frame.grid_rowconfigure(1, weight=0)
        reservation_frame.grid_rowconfigure(2, weight=0)
        reservation_frame.grid_rowconfigure(3, weight=1)
        reservation_frame.grid_rowconfigure(4, weight=1)
        reservation_frame.grid_columnconfigure(0, weight=0)
        reservation_frame.grid_columnconfigure(1, weight=1)
        reservation_frame.grid_columnconfigure(2, weight=0)
        reservation_frame.grid_columnconfigure(3, weight=1)

        reservation_advance_label = Label(reservation_frame, text = "Wartość zaliczki:")
        reservation_advance_entry = ttk.Entry(reservation_frame)
        reservation_advance_entry.insert(0,fun.short_price(reservation.Reservation.advance))

        reservation_advance_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        reservation_advance_entry.grid(row=0, column=1, padx=0, pady=10, sticky="ew")

        new_price_label = Label(reservation_frame, text = "Ustalona cena:")
        new_price_entry = ttk.Entry(reservation_frame)
        new_price_entry.insert(0, fun.short_price(reservation.Product.price))

        new_price_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        new_price_entry.grid(row=1, column=1, padx=0, pady=10, sticky="ew")

        reservation_form = StringVar()
        if reservation.Reservation.form == 0:
            og_form = "zaliczka"
        else:
            og_form = "zadatek"
        reservation_form.set(og_form)
        form_box=OptionMenu(reservation_frame, reservation_form, *['zaliczka', 'zadatek'])
        form_box.grid(row=0, column=2, padx=0, pady=10, columnspan=2)

        payment_method = StringVar()
        payment_method.set('płatność')
        banks_json=json.load(open(resource_path("static/acc_numbers.json"), "r", encoding="utf-8"))
        banks = ['gotówka', 'karta']+list(banks_json.keys())
        payment_method_box=OptionMenu(reservation_frame, payment_method, *banks)
        payment_method_box.grid(row=1, column=2, padx=0, pady=(0, 10), columnspan=2)

        payment_method.set(reservation.Reservation.payment_method)

        checkbuttons_frame = Frame(reservation_frame)
        checkbuttons_frame.grid(row=2, column=2, padx=0, pady=(0, 10), columnspan=2)

        delivery = BooleanVar(value=reservation.Reservation.delivery)
        delivery_button = Checkbutton(checkbuttons_frame, text="Dostawa", variable=delivery, offvalue=False, onvalue=True)
        delivery_button.grid(row=0, column=1, padx=10, pady=0, columnspan=1)
        
        reservation_paid = BooleanVar(value=reservation.Reservation.paid)
        paid_button = Checkbutton(checkbuttons_frame, text="Zapłacono", variable=reservation_paid, offvalue=False, onvalue=True)
        paid_button.grid(row=0, column=0, padx=10, pady=0, columnspan=1)


        term_label = Label(reservation_frame, text = "Termin realizacji:")  
        term_entry = ttk.Entry(reservation_frame)

        term_label.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="w")
        term_entry.grid(row=2, column=1, padx=0, pady=(10, 10), columnspan=2, sticky="ew")
        term_entry.insert(0, reservation.Reservation.term)

        adnotation_label = Label(reservation_frame, text = "Uwagi:")
        adnotation_entry = Text(reservation_frame, wrap=WORD, height=5)
        adnotation_entry.insert(END, reservation.Reservation.adnotation)

        adnotation_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        adnotation_entry.grid(row=3, column=1, padx=0, pady=10, sticky="nsew", columnspan=3)

        adnotation_pub_label = Label(reservation_frame, text = "Uwagi dla klienta:")
        adnotation_pub_entry = Text(reservation_frame, wrap=WORD, height=5)
        adnotation_pub_entry.insert(END, reservation.Reservation.adnotation_pub)

        adnotation_pub_label.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="w")
        adnotation_pub_entry.grid(row=4, column=1, padx=0, pady=(0, 10), sticky="nsew", columnspan=3)
                
        cancel_button = Button(top, text="Anuluj", command=lambda: top.destroy())
        cancel_button.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        make_button = Button(top, text="Akceptuj", command=lambda: [but.confirm_edit_reservation(reservation, new_price_entry.get().strip(),
            reservation_advance_entry.get().strip(),
            reservation_form.get(), reservation_paid.get(), adnotation_entry.get('1.0', 'end').strip(),
            adnotation_pub_entry.get('1.0', 'end').strip(), term_entry.get().strip(), delivery.get(), payment_method.get(), top)])
        make_button.grid(row=4, column=1, padx=10, pady=10, sticky="e")


    def edit_product(self, product_id, root):
        if product_id == -1:
            messagebox.showerror("Error", "Wybierz produkt")
            return

        top = Toplevel(root)
        top.title("Edytuj pojazd")

        product_brand_label = ttk.Label(top, text="Marka:*", justify="left")
        product_brand_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.edit_product_brand_var = StringVar()
        self.edit_product_brand_entry = ttk.Combobox(top, textvariable = self.edit_product_brand_var, state="readonly")
        self.edit_product_brand_entry["values"] = con.get_brands_list() 
        self.edit_product_brand_entry.grid(row=0, column=1, padx=15, pady=15, sticky="w")


        product_model_label = ttk.Label(top, text="Model:*", justify="left")
        product_model_label.grid(row=0, column=2, padx=15, pady=15, sticky="w")

        self.edit_product_model_var = StringVar()
        self.edit_product_model_entry = ttk.Combobox(top, textvariable = self.edit_product_model_var, state="readonly")
        self.edit_product_model_entry.bind("<Button-1>", lambda x: fun.fill_models(self.edit_product_model_entry, self.edit_product_brand_var.get()))
        self.edit_product_model_entry.grid(row=0, column=3, padx=15, pady=15, sticky="w")
        self.edit_product_brand_entry.bind("<<ComboboxSelected>>", lambda x: self.edit_product_model_entry.set(""))


        product_colour_label = ttk.Label(top, text="Kolor:*", justify="left")
        product_colour_label.grid(row=1, column=0, padx=15, pady=15, sticky="w")

        self.edit_product_colour_var = StringVar()
        product_colour_entry = ttk.Combobox(top, textvariable = self.edit_product_colour_var, state="readonly")
        product_colour_entry["values"] = con.get_colours_list()
        product_colour_entry.grid(row=1, column=1, padx=15, pady=15, sticky="w")
        
        
        product_price_label = ttk.Label(top, text="Cena:", justify="left")
        product_price_label.grid(row=2, column=0, padx=15, pady=15, sticky="w")

        product_price_entry = ttk.Entry(top)
        product_price_entry.grid(row=2, column=1, padx=15, pady=15, sticky="ew")


        product_year_label = ttk.Label(top, text="Rocznik:*", justify="left")
        product_year_label.grid(row=1, column=2, padx=15, pady=15, sticky="w")

        product_year_entry = ttk.Entry(top)
        product_year_entry.grid(row=1, column=3, padx=15, pady=15, sticky="ew")

        product_order_id_label = ttk.Label(top, text="Nr zamówienia:", justify="left")
        product_order_id_label.grid(row=2, column=2, padx=15, pady=15, sticky="w")

        product_order_id_entry = ttk.Entry(top)
        product_order_id_entry.grid(row=2, column=3, padx=15, pady=15, sticky="ew")
        
        product_state_label = ttk.Label(top, text="Stan:", justify="left")
        product_state_label.grid(row=3, column=2, padx=15, pady=15, sticky="w")

        self.edit_product_state = StringVar()
        product_state_entry = ttk.Combobox(top, textvariable=self.edit_product_state, state="readonly")
        product_state_entry["values"] = ("Oczekujemy na dostawę", "Na stanie", "Wydany")
        product_state_entry.grid(row=3, column=3, padx=15, pady=15, sticky="ew")

        product_expected_delivery_label = ttk.Label(top, text="Przewidywana dostawa:", justify="left")
        product_expected_delivery_label.grid(row=3, column=0, padx=15, pady=15, sticky="w")


        product_expected_delivery_entry = cal.DateEntry(top, date_pattern='dd.mm.yyyy', showweeknumbers=False, selectmode='day',
            font=("Default", 12),
            weekendbackground = "#E5E5E5", 
            weekendforeground = "#000000",
            othermonthbackground = "#8F8F8F",
            othermonthforeground = "#4A4A4A",
            othermonthwebackground = "#8F8F8F",
            othermonthweforeground = "#4A4A4A")
        product_expected_delivery_entry.grid(row=3, column=1, padx=15, pady=15, sticky="ew")
        product_expected_delivery_entry.delete(0, END)

        product = con.get_product(product_id)
        #print(product.brand, product.model, product.colour, product.state)
        self.edit_product_brand_var.set(product.brand)
        self.edit_product_model_entry["values"] = con.get_models_list(product.brand)
        self.edit_product_model_var.set(product.model)
        self.edit_product_colour_var.set(product.colour)
        self.edit_product_state.set(product.state)
        product_year_entry.insert(0, product.year)
        if product.expected_delivery is not None: product_expected_delivery_entry.insert(0, product.expected_delivery.strftime("%d.%m.%Y"))
        product_price_entry.insert(0, fun.short_price(product.price))
        product_order_id_entry.insert(0, product.order_id)


        yes_button = Button(top, text="Potwierdź", command=lambda: [but.sum_up_edit_product(product.id, 
        self.edit_product_brand_var.get(), self.edit_product_model_var.get(), 
        self.edit_product_colour_var.get(), product_price_entry.get().strip(),  product_year_entry.get().strip(), 
        product_order_id_entry.get().strip(), self.edit_product_state.get(), 
        product_expected_delivery_entry.get(), product_expected_delivery_entry.get_date(), top)])
        yes_button.grid(row=4, column=3, padx=15, pady=15, sticky="e")
        no_button = Button(top, text="Anuluj", command=lambda: [top.destroy()])
        no_button.grid(row=4, column=0, padx=15, pady=15, sticky="w")


    def edit_customer(self, customer_id, lasttop):
        if customer_id == -1:
            messagebox.showerror("Error", "Wybierz klienta")
            return
        
        top = Toplevel(lasttop)
        top.title("Edytuj klienta")
        top.columnconfigure(0, weight=0)
        top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)
        top.rowconfigure(1, weight=1)
        top.rowconfigure(2, weight=1)
        top.rowconfigure(3, weight=1)
        top.rowconfigure(4, weight=1)
        top.rowconfigure(5, weight=1)
        top.rowconfigure(6, weight=1)
        top.rowconfigure(7, weight=1)
        
        name_label = Label(top, text="Imię i Nazwisko:*")
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w") 

        name_entry = ttk.Entry(top)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew") 
        
        phone_label = Label(top, text="Numer telefonu:*")
        phone_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        phone_entry = ttk.Entry(top)
        phone_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        
        email_label = Label(top, text="Email:")
        email_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        email_entry = ttk.Entry(top)
        email_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        pesel_label = Label(top, text="PESEL:")
        pesel_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        pesel_entry = ttk.Entry(top)
        pesel_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        company_name_label = Label(top, text="Nazwa firmy:")
        company_name_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        company_name_entry = ttk.Entry(top)
        company_name_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        nip_label = Label(top, text="NIP:")
        nip_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        nip_entry = ttk.Entry(top)
        nip_entry.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

        adress_label = Label(top, text="Adres:")
        adress_label.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        adress_entry = Text(top, wrap=WORD, height=5)
        adress_entry.grid(row=6, column=1, padx=10, pady=10, sticky="ew")

        customer = con.get_customer(customer_id)

        name_entry.insert(0, customer.name)
        phone_entry.insert(0, customer.phone)
        email_entry.insert(0, customer.email)
        pesel_entry.insert(0, customer.pesel)
        nip_entry.insert(0, customer.nip)
        adress_entry.insert(END, customer.adress)
        company_name_entry.insert(0, customer.company_name)

        add_button = Button(top, text="Potwierdź", command=lambda:[but.sum_up_edit_customer(customer_id, name_entry.get().strip(), 
            phone_entry.get().strip(), email_entry.get().strip(), pesel_entry.get().strip(), nip_entry.get().strip(), 
            company_name_entry.get().strip(), adress_entry.get('1.0', 'end').strip(), top)])
        add_button.grid(row=7, column=1, padx=10, pady=10, sticky="e")

        no_button = Button(top, text="Anuluj", command=lambda: top.destroy())
        no_button.grid(row=7, column=0, padx=10, pady=10, sticky="w")
        #top.geometry(f"400x{top.winfo_reqheight()+70}")

        lasttop.wait_window(top)
    