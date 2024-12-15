import sqlite3
import re
from tkinter import *
from tkinter.messagebox import showerror, showwarning, showinfo
from ttkthemes import themed_style
from tkinter import ttk, filedialog, messagebox
from tkcalendar import Calendar
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Montserrat-Regular', 'fonts/Montserrat-Regular.ttf'))

# Для работы с базой данных
class Database:
    def __init__(self, db_name="global_nomad.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@_%._%'),
            password TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS direction (
            direction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_direction TEXT NOT NULL,
            description TEXT NOT NULL,
	    created_by INTEGER,
	    FOREIGN KEY(created_by) REFERENCES administrator(id_admin)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS packages (
            packages_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            direction_id INTEGER,
            date DATE NOT NULL,
            id_payment_method INTEGER,
            FOREIGN KEY(id_payment_method) REFERENCES payment_methods(id_payment_method)
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(direction_id) REFERENCES direction(direction_id)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS administrator (
                id_admin INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                admin_login TEXT NOT NULL UNIQUE,
                admin_password TEXT NOT NULL UNIQUE,
                admin_name TEXT NOT NULL,
                admin_last_name TEXT NOT NULL
            )''')
        conn.commit()
        conn.close()


# Приложение
class UserInterface:
    def __init__(self):
        self.current_user_uid = None
        self.current_admin_uid = None
        self.background_image = None
        self.db = Database()
        self.db.create_tables()
        self.choice_window = None
        self.main_root = None
        self.admin_root = None

    def connect_db(self):
        conn =sqlite3.connect("global_nomad.db")

    # фоновое изображение
    def set_background_image(self, window):
        background_label = Label(window, image=self.background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Окно выбора роли
    def run(self):
        self.choice_window = Tk()
        self.choice_window.title('Выбор роли')
        self.choice_window.geometry('400x300')
        self.choice_window.configure(background='#fafafa')

        label = ttk.Label(self.choice_window, text="Добро пожаловать в приложение Global Nomad!", font=("Montserrat", 15), background="#FAFAFA", wraplength=250)
        label.pack(pady=50)

        user_button = Button(self.choice_window, text="Пользователь", command=self.choice_role_user, width=20)
        user_button.pack(pady=10)

        admin_button = Button(self.choice_window, text="Администратор", width=20, command=self.choice_role_admin)
        admin_button.pack(pady=10)

        self.choice_window.mainloop()

    # Функция для проверки формата электронной почты
    def is_valid_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    # Функция для проверки пароля
    def is_valid_password(self, password):
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        return re.match(password_regex, password) is not None

    # Функция регистрации (в базу данных)
    def register_user(self):
        email = self.entry_login_reg.get()
        password = self.entry_password_reg.get()

        if not self.is_valid_email(email):
            messagebox.showerror("Ошибка", "Введите "
                                           "корректный адрес электронной почты.")
            return


        if not self.is_valid_password(password):
            messagebox.showerror("Ошибка",
                                    "Пароль должен содержать минимум 8 символов, "
                                     "включая заглавные и строчные буквы, цифры и специальные символы.")
            return
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)",
                               (email, password))
            conn.commit()
            messagebox.showinfo("Регистрация", "Пользователь успешно зарегистрирован!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Пользователь с таким email уже существует.")
        finally:
            conn.close()

    def on_entry_click_reg_login(self, event):
        if self.entry_login_reg.get() == "Email пользователя":
            self.entry_login_reg.delete(0, END)
            self.entry_login_reg.config(foreground="black")

    def on_entry_click_reg_password(self, event):
        if self.entry_password_reg.get() == "Пароль":
            self.entry_password_reg.delete(0, END)
            self.entry_password_reg.config(foreground="black")

    # Окно регистрации пользователя
    def registration(self):
        self.window_registration = Toplevel()
        self.window_registration.title("Global Nomad регистрация")
        self.window_registration.geometry("952x682+70+60")
        self.window_registration.resizable(False, False)
        self.window_registration.config(background="#FAFAFA")



        title_lb_reg = ttk.Label(self.window_registration, text='Global Nomad', background="#FAFAFA",
                                 font=('Montserrat Alternates', 64))
        title_lb_reg.pack(anchor='center', pady=140)
        label1_reg = ttk.Label(self.window_registration, text="Зарегистрируйтесь для входа",
                               background="#FAFAFA", font=("Montserrat", 12), foreground="#625D5D")
        label1_reg.place(x=350, y=250)

        # стиль для Entry
        style_reg = themed_style.ThemedStyle(self.window_registration)
        style_reg.theme_use("clam")
        style_reg.configure("TEntry", padding=10)

        # Ввод логина
        self.entry_login_reg = ttk.Entry(self.window_registration, width=30)
        self.entry_login_reg.place(x=290, y=330)
        self.entry_login_reg.insert(0, "Email пользователя")
        self.entry_login_reg.config(font=("Montserrat", 12), foreground="#625D5D")
        self.entry_login_reg.bind("<FocusIn>", self.on_entry_click_reg_login)
        # Ввод пароля
        self.entry_password_reg = ttk.Entry(self.window_registration, width=30)
        self.entry_password_reg.place(x=290, y=400)
        self.entry_password_reg.insert(0, "Пароль")
        self.entry_password_reg.config(font=("Montserrat", 12), foreground="#625D5D")
        self.entry_password_reg.bind("<FocusIn>", self.on_entry_click_reg_password)
        # кнопка для регистрации
        btn_reg = Button(self.window_registration, text="Регистрация", bg='#162013', width=20, fg="#FFFFFF",
                         font=("Montserrat", 12), command=self.register_user)
        btn_reg.place(x=360, y=500, height=45)

        label2_registration = ttk.Label(self.window_registration, text="Регистрируясь, вы принимаете наши Условия",
                                        background="#FAFAFA",
                                        font=("Montserrat", 12), foreground="#625D5D")
        label2_registration.place(x=280, y=598)

        label3_registration = ttk.Label(self.window_registration, text="и Политику использования данных",
                                        background="#FAFAFA",
                                        font=("Montserrat", 12), foreground="#625D5D")
        label3_registration.place(x=318, y=625)

    # Окно авторизации пользователя
    def choice_role_user(self):
        self.choice_window.destroy()
        self.main_root = Tk()
        self.main_root.title("Global Nomad")
        self.main_root.geometry('952x682+70+60')
        self.main_root.resizable(False, False)
        self.main_root.config(background="#FAFAFA")

        self.background_image = PhotoImage(file="img/bcg.png")
        self.set_background_image(self.main_root)

        title_lb = ttk.Label(self.main_root, text='Global Nomad', background="#FAFAFA", font=('Montserrat Alternates', 64))
        title_lb.pack(anchor='center', pady=140)
        label1 = ttk.Label(self.main_root, text="Введите данные для входа", background="#FAFAFA", font=("Montserrat", 12), foreground="#625D5D")
        label1.place(x=350, y=250)

        style = themed_style.ThemedStyle(self.main_root)
        style.theme_use("clam")
        style.configure("TEntry", padding=10)

        self.entry_login = ttk.Entry(self.main_root, width=30)
        self.entry_login.place(x=290, y=330)
        self.entry_login.insert(0, "Email пользователя")
        self.entry_login.config(font=("Montserrat", 12), foreground="#625D5D")
        self.entry_login.bind("<FocusIn>", self.on_entry_click_authorization_login)

        self.entry_password = ttk.Entry(self.main_root, width=30)
        self.entry_password.place(x=290, y=400)
        self.entry_password.insert(0, "Пароль")
        self.entry_password.config(font=("Montserrat", 12), foreground="#625D5D")
        self.entry_password.bind("<FocusIn>", self.on_entry_click_authorization_password)

        btn_enter = Button(self.main_root, text="Войти", bg='#162013', width=20, fg="#FFFFFF", font=("Montserrat", 12), command=self.travel_packages)
        btn_enter.place(x=360, y=500, height=45)

        # кнопка регистрации
        btn_registr = Button(self.main_root, text="Регистрация", width=15, fg="#000000",
                             font=("Montserrat", 12), bg="#FAFAFA",
                             command=self.registration)
        btn_registr.place(x=15, y=10)
        btn_registr['borderwidth'] = 0

    def on_entry_click_authorization_login(self, event):
        if self.entry_login.get() == "Email пользователя":
            self.entry_login.delete(0, END)
            self.entry_login.config(foreground="black")

    def on_entry_click_authorization_password(self, event):
        if self.entry_password.get() == "Пароль":
            self.entry_password.delete(0, END)
            self.entry_password.config(foreground="black")

    # Добавление данных о путевке в базу данных
    def add_travel_data(self):
        selected_direction_name = self.travel_packages_choice_combobox.get()
        selected_date = self.calendar.get_date()
        selected_payment_method_name = self.payment_method_combobox.get()

        if selected_date and selected_direction_name and selected_payment_method_name:
            try:

                conn = self.db.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT direction_id FROM direction WHERE name_direction=?",
                               (selected_direction_name,))
                direction_id_row = cursor.fetchone()
                cursor.execute("SELECT id_payment_method FROM payment_methods WHERE name_payment_method=?",
                               (selected_payment_method_name,))
                payment_method_row = cursor.fetchone()  # Идентификатор метода оплаты
                conn.close()

                if direction_id_row and payment_method_row:
                    direction_id = direction_id_row[0]
                    payment_method_id = payment_method_row[0]

                    conn = self.db.connect()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO packages (user_id, direction_id, date, id_payment_method) VALUES (?, ?, ?, ?)",
                        (self.current_user_uid, direction_id, selected_date, payment_method_id))
                    conn.commit()
                    conn.close()
                    showinfo(title="Путевки", message="Путевка выбрана")
                else:
                    showerror(title="Ошибка", message="Направление не найдено в базе данных.")
            except Exception as e:
                showwarning(title="Предупреждение", message=f"Ошибка при оформлении путевки: {e}")
        else:
            showerror(title="Ошибка", message="Все данные должны быть выбраны")

    # Функция для обновления описания путевки
    def update_description(self, event):
        selected_direction_name = self.travel_packages_choice_combobox.get()
        if selected_direction_name:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT description FROM direction WHERE name_direction=?",
                           (selected_direction_name,))
            description = cursor.fetchone()
            conn.close()
            if description:
                self.description_label.config(text=description[0])  # Обновляем текст описания
            else:
                self.description_label.config(text="Описание не найдено.")

    # Окно выбора направлений
    def travel_packages(self):
        login = self.entry_login.get()
        password = self.entry_password.get()
        if login and password and len(login) >= 5 and 8 <= len(password) <= 20:
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (login, password))
                user = cursor.fetchone()
                conn.close()
                if user:
                    self.current_user_uid = user[0]
                    showinfo(title='Вход', message='Успешный вход')
                    self.current_user_uid = user[0]
                    self.main_root.destroy()

                    self.window_travels = Tk()
                    self.window_travels.title("Global Nomad туристические путевки")
                    self.window_travels.geometry("952x682+70+60")
                    self.window_travels.resizable(False, False)
                    self.window_travels.config(background="#FAFAFA")

                    # кнопка для открытия окна профиля
                    profile_btn = Button(self.window_travels, text="Профиль", width=15, fg="#000000",
                                         font=("Montserrat", 12),
                                         bg="#FAFAFA", command=self.profile)
                    profile_btn.place(x=800, y=17)
                    profile_btn['borderwidth'] = 0

                    global_label = ttk.Label(self.window_travels, text="Global Nomad", font=('Montserrat Alternates', 12),
                                             background="#FAFAFA")
                    global_label.pack(anchor="nw", pady=20, padx=15)

                    travel_lb1 = ttk.Label(self.window_travels, text="Выбирайте путевки", font=("Montserrat", 35),
                                           background="#FAFAFA")
                    travel_lb1.pack(anchor="nw", pady=80, padx=15)
                    travel_lb2 = ttk.Label(self.window_travels, text="для души!", font=("Montserrat", 35),
                                           background="#FAFAFA")
                    travel_lb2.place(x=15, y=200)

                    travel_lb3 = ttk.Label(self.window_travels, text="у нас собраны лучшие направления",
                                           background="#FAFAFA",
                                           font=("Montserrat", 12), foreground="#625D5D")
                    travel_lb3.place(x=15, y=275)
                    travel_lb4 = ttk.Label(self.window_travels, text="и удобные даты, чтобы каждый мог понять,",
                                           background="#FAFAFA", font=("Montserrat", 12), foreground="#625D5D")
                    travel_lb4.place(x=15, y=300)
                    travel_lb5 = ttk.Label(self.window_travels, text="что путешествию есть время - всегда.",
                                           background="#FAFAFA", font=("Montserrat", 12), foreground="#625D5D")
                    travel_lb5.place(x=15, y=325)

                    # Добавление Label для отображения описания
                    self.description_label = ttk.Label(self.window_travels, text="", background="#FAFAFA",
                                                  font=("Montserrat", 12), wraplength=360)
                    self.description_label.place(x=15, y=380)

                    # выбор направлений
                    travel_packages_choice = ttk.Label(self.window_travels, text="Направления", background="#FAFAFA",
                                                       font=("Montserrat", 12))
                    travel_packages_choice.place(x=800, y=170)

                    conn = self.db.connect()
                    cursor = conn.cursor()
                    cursor.execute("SELECT name_direction FROM direction")
                    directions = cursor.fetchall()
                    conn.close()

                    # из списка кортежей в простой список
                    packages = [direction[0] for direction in directions]

                    self.travel_packages_choice_combobox = ttk.Combobox(self.window_travels, values=packages,
                                                                   state="readonly",
                                                                   justify="left", background="#fafafa", height=40)
                    self.travel_packages_choice_combobox.place(x=785, y=200)

                    # Привязка события выбора направления к функции обновления описания
                    self.travel_packages_choice_combobox.bind("<<ComboboxSelected>>", self.update_description)

                    # выбор дат
                    travel_packages_date = ttk.Label(self.window_travels, text="Даты", background="#FAFAFA",
                                                     font=("Montserrat", 12))
                    travel_packages_date.place(x=873, y=250)
                    self.calendar = Calendar(self.window_travels, selectmode='day', year=datetime.now().year,
                                        month=datetime.now().month)
                    self.calendar.place(x=680, y=280)

                    # выбор методов оплаты
                    payment_method_label = ttk.Label(self.window_travels, text="Способы оплаты",
                                                     background="#FAFAFA",
                                                     font=("Montserrat", 12))
                    payment_method_label.place(x=790, y=490)

                    conn = self.db.connect()
                    cursor = conn.cursor()
                    cursor.execute("SELECT name_payment_method FROM payment_methods")
                    payment_methods = cursor.fetchall()
                    conn.close()

                    # из списка кортежей в простой список
                    payment_methods_list = [method[0] for method in payment_methods]

                    self.payment_method_combobox = ttk.Combobox(self.window_travels,
                                                           values=payment_methods_list, state="readonly",
                                                           justify="left", background="#fafafa", height=40)
                    self.payment_method_combobox.place(x=785, y=520)

                    # кнопка для добавления даты и направления
                    choice = Button(self.window_travels, text="Выбрать", bg='#162013', width=20, fg="#FFFFFF",
                                    font=("Montserrat", 12), command=self.add_travel_data)
                    choice.place(height=45, x=720, y=570)

                    phone_number = Label(self.window_travels, text='Для уточнения стоимости обращаться по телефону +7 900 800 77 32',
                                         background='#fafafa', font=("Montserrat", 10))
                    phone_number.place(x=480, y= 630)


                else:
                    showerror(title="Ошибка", message="Неверный логин или пароль.")
            except Exception as e:
                showwarning(title="Предупреждение", message="Ошибка при входе в систему: " + str(e))
        else:
            showerror(title="Ошибка", message="Логин или пароль не соответствуют требованиям.")

    # Функция экспорта данных
    def export_to_pdf(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        pdfmetrics.registerFont(TTFont('Montserrat-Regular', 'fonts/Montserrat-Regular.ttf'))
        cursor.execute("SELECT email FROM users WHERE user_id=?", (self.current_user_uid,))
        user_data = cursor.fetchone()

        cursor.execute("SELECT date, direction_id, id_payment_method FROM packages WHERE user_id=?",
                       (self.current_user_uid,))
        packages_list = cursor.fetchall()

        if user_data:
            user_info = user_data[0]
        else:
            messagebox.showerror("Ошибка", "Не удалось получить данные пользователя.")
            conn.close()

        pdf_filename = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                    filetypes=[("PDF files", ".pdf"), ("All files", ".*")],
                                                    title="Сохранить PDF как")
        if not pdf_filename:
            conn.close()
            return
        pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)
        styles = getSampleStyleSheet()
        styles['Title'].fontName = 'Montserrat-Regular'
        styles['Heading2'].fontName = 'Montserrat-Regular'
        styles['BodyText'].fontName = 'Montserrat-Regular'

        elements = []

        elements.append(Paragraph(f"Данные пользователя: {user_info}", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Ваши выбранные путевки:", styles['Heading2']))
        elements.append(Spacer(1, 12))

        if packages_list:
            for package in packages_list:
                date, direction_id, id_payment_method = package
                # Получение названия направления
                cursor.execute("SELECT name_direction FROM direction WHERE direction_id=?", (direction_id,))
                direction_name = cursor.fetchone()
                direction_name = direction_name[0] if direction_name else "Неизвестное направление"

                # Получение названия способа оплаты
                cursor.execute(
                    "SELECT name_payment_method FROM payment_methods WHERE id_payment_method=?",
                    (id_payment_method,))
                payment_method_name = cursor.fetchone()
                payment_method_name = payment_method_name[0] if payment_method_name else "Неизвестный способ оплаты"

                elements.append(
                    Paragraph(
                        f"Дата: {date}, Направление: {direction_name}, Способ оплаты: {payment_method_name}",
                        styles['BodyText']))
                elements.append(Spacer(1, 12))
        else:
            elements.append(Paragraph("Путевок нет", styles['BodyText']))

        pdf.build(elements)
        messagebox.showinfo("Экспорт в PDF", f"Данные пользователя успешно экспортированы в {pdf_filename}")
        conn.close()

    # Окно профиля
    def profile(self):
        self.window_profile = Toplevel()
        self.window_profile.title("Global Nomad профиль пользователя")
        self.window_profile.geometry("952x682+70+60")
        self.window_profile.resizable(False, False)
        self.window_profile.config(background="#FAFAFA")

        self.background_image = PhotoImage(file="img/bcg.png")
        self.set_background_image(self.window_profile)

        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE user_id=?", (self.current_user_uid,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            global_label_profile = ttk.Label(self.window_profile, text="Global Nomad",
                                             font=('Montserrat Alternates', 12), background="#FAFAFA")
            global_label_profile.pack(anchor="nw", pady=20, padx=15)

            greeting_lb = ttk.Label(self.window_profile, text="Здравствуй, глобальный кочевник!",
                                    font=("Montserrat", 25), background="#FAFAFA")
            greeting_lb.pack(anchor="nw", pady=80, padx=15)

            user_packages_lb = ttk.Label(self.window_profile, text="Ваши выбранные путевки",
                                         background="#FAFAFA", font=("Montserrat", 12),
                                         foreground="#625D5D")
            user_packages_lb.place(x=15, y=200)

            # Отображение путевок пользователя
            self.packages_listbox = Listbox(self.window_profile, width=80, height=10, font=("Montserrat", 12))
            self.packages_listbox.place(y=240, x=15)

            # Получаем данных о путевках пользователя
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT date, direction_id, id_payment_method FROM packages WHERE user_id=?",
                           (self.current_user_uid,))
            packages_list = cursor.fetchall()
            conn.close()

            if packages_list:
                for package in packages_list:
                    date, direction_id, id_payment_method = package

                    conn = self.db.connect()
                    cursor = conn.cursor()
                    cursor.execute("SELECT name_direction FROM direction WHERE direction_id=?",
                                   (direction_id,))
                    direction_name = cursor.fetchone()
                    cursor.execute(
                        "SELECT name_payment_method FROM payment_methods WHERE id_payment_method=?",
                        (id_payment_method,))
                    payment_method_name = cursor.fetchone()
                    conn.close()
                    direction_name = direction_name[0] if direction_name else "Неизвестное направление"
                    payment_method_name = payment_method_name[0] if payment_method_name else "Неизвестный метод оплаты"
                    self.packages_listbox.insert(END,
                                            f"Дата: {date}, Направление: {direction_name}, Способ оплаты: {payment_method_name}")
            else:
                self.packages_listbox.insert(END, "Путевок нет")

            # Кнопка для экспорта данных в PDF
            export_pdf_btn = Button(self.window_profile, text="Экспорт билета в PDF", command=self.export_to_pdf,
                                    bg='#162013',
                                    fg="#FFFFFF", font=("Montserrat", 12))
            export_pdf_btn.place(x=15, y=600)

    # Окно авторизации администратора
    def choice_role_admin(self):
        self.choice_window.destroy()
        self.admin_root = Tk()
        self.admin_root.title("Global Nomad")
        self.admin_root.geometry('952x682+70+60')
        self.admin_root.resizable(False, False)
        self.admin_root.config(background="#FAFAFA")

        self.background_image = PhotoImage(file="img/bcg.png")
        self.set_background_image(self.admin_root)

        title_lb = ttk.Label(self.admin_root, text='Global Nomad', background="#FAFAFA",
                             font=('Montserrat Alternates', 64))
        title_lb.pack(anchor='center', pady=140)
        label1 = ttk.Label(self.admin_root, text="Введите данные для входа", background="#FAFAFA",
                           font=("Montserrat", 12), foreground="#625D5D")
        label1.place(x=350, y=250)

        style = themed_style.ThemedStyle(self.admin_root)
        style.theme_use("clam")
        style.configure("TEntry", padding=10)

        self.entry_login_admin = ttk.Entry(self.admin_root, width=30)
        self.entry_login_admin.place(x=290, y=330)
        self.entry_login_admin.insert(0, "Логин администратора")
        self.entry_login_admin.config(font=("Montserrat", 12), foreground="#625D5D")
        self.entry_login_admin.bind("<FocusIn>", self.on_entry_click_admin_login)

        self.entry_password_admin = ttk.Entry(self.admin_root, width=30)
        self.entry_password_admin.place(x=290, y=400)
        self.entry_password_admin.insert(0, "Пароль")
        self.entry_password_admin.config(font=("Montserrat", 12), foreground="#625D5D")
        self.entry_password_admin.bind("<FocusIn>", self.on_entry_click_admin_password)

        btn_enter_admin = Button(self.admin_root, text="Войти", bg='#162013', width=20, fg="#FFFFFF",
                                 font=("Montserrat", 12), command=self.administrator_work_window)
        btn_enter_admin.place(x=360, y=500, height=45)

    def on_entry_click_admin_login(self, event):
        if self.entry_login_admin.get() == "Логин администратора":
            self.entry_login_admin.delete(0, END)
            self.entry_login_admin.config(foreground="black")

    def on_entry_click_admin_password(self, event):
        if self.entry_password_admin.get() == "Пароль":
            self.entry_password_admin.delete(0, END)
            self.entry_password_admin.config(foreground="black")

    # Проверка для входа в окно администрирования
    def administrator_work_window(self):
        login_admin = self.entry_login_admin.get().strip()
        password_admin = self.entry_password_admin.get().strip()
        if login_admin and password_admin:
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM administrator WHERE admin_login=? AND admin_password=?",
                               (login_admin, password_admin))
                admin = cursor.fetchone()
                conn.close()

                if admin:
                    self.current_admin_uid = admin[0]  # Сохраняем id администратора
                    showinfo(title='Вход', message='Успешный вход')
                    self.admin_root.destroy()
                    self.admin_work()
                else:
                    showerror(title='Предупреждение', message='Неверный логин или пароль администратора')
            except Exception as e:
                showerror(title="Ошибка", message=f"Ошибка при входе в систему: {str(e)}")
        else:
            showerror(title="Ошибка", message="Логин или пароль не соответствуют требованиям.")

    # Отображение списка пользователей
    def display_users(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, email FROM users")
        users = cursor.fetchall()
        conn.close()

        self.user_listbox.delete(0, END)  # Очистка списка перед добавлением новых данных
        for user in users:
            self.user_listbox.insert(END, f"№ пользователя: {user[0]}, Email: {user[1]}")

    # Функция для добавления нового направления
    def add_direction(self):
        direction_name = self.entry_direction.get()
        direction_description = self.entry_description.get()
        if direction_name and direction_description:
            conn = self.db.connect()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO direction (name_direction, description, created_by) VALUES (?, ?, ?)",
                               (direction_name, direction_description, self.current_admin_uid))
                conn.commit()
                showinfo("Успех", "Направление успешно добавлено!")
                self.display_directions()  # Обновляем список направлений
            except sqlite3.IntegrityError:
                showerror("Ошибка", "Направление с таким именем уже существует.")
            finally:
                conn.close()
        else:
            showerror("Ошибка", "Введите название и описание направления.")

    # Функция для отображения направлений
    def display_directions(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT direction_id, name_direction FROM direction")
        directions = cursor.fetchall()
        conn.close()

        self.direction_listbox.delete(0, END)  # Очистка списка перед добавлением новых данных
        for direction in directions:
            self.direction_listbox.insert(END, f"№: {direction[0]}, Направление: {direction[1]}")

    # Окно администрирования
    def admin_work(self):
        self.admin_window = Tk()
        self.admin_window.title('Окно администрирования')
        self.admin_window.geometry('1000x720')
        self.admin_window.resizable(False, False)
        self.admin_window.config(background='#fafafa')


        title_lb = ttk.Label(self.admin_window, text='Global Nomad - Администрирование', background="#FAFAFA",
                             font=('Montserrat Alternates', 24))
        title_lb.pack(anchor='center', pady=20)

        # Список пользователей
        self.user_listbox = Listbox(self.admin_window, width=40, height=15, font=("Montserrat", 12))
        self.user_listbox.place(x=15, y=80)

        # Кнопка для отображения пользователей
        btn_show_users = Button(self.admin_window, text="Показать пользователей", command=self.display_users,
                                bg='#162013', fg="#FFFFFF", font=("Montserrat", 12))
        btn_show_users.place(x=15, y=450)

        # Список направлений
        self.direction_listbox = Listbox(self.admin_window, width=40, height=15, font=("Montserrat", 12))
        self.direction_listbox.place(x=530, y=80)

        # Кнопка для отображения направлений
        btn_show_directions = Button(self.admin_window, text="Показать направления", command=self.display_directions,
                                     bg='#162013', fg="#FFFFFF", font=("Montserrat", 12))
        btn_show_directions.place(x=530, y=450)

        # Поле для добавления нового направления
        self.entry_direction = ttk.Entry(self.admin_window, width=30)
        self.entry_direction.place(x=530, y=510)
        self.entry_direction.insert(0, "Введите новое направление")
        self.entry_direction.config(font=("Montserrat", 12), foreground="#625D5D")
        self.entry_direction.bind("<FocusIn>", self.on_entry_add_direction_click)

        # Поле для добавления описания нового направления
        self.entry_description = ttk.Entry(self.admin_window, width=30)
        self.entry_description.place(x=530, y=565)
        self.entry_description.insert(0, "Введите описание")
        self.entry_description.config(font=("Montserrat", 12), foreground="#625D5D")
        self.entry_description.bind("<FocusIn>", self.on_entry_description_click)

        # Кнопка для добавления нового направления
        btn_add_direction = Button(self.admin_window, text="Добавить направление", command=self.add_direction,
                                   bg='#162013', fg="#FFFFFF", font=("Montserrat", 12))
        btn_add_direction.place(x=530, y=630)

    def on_entry_add_direction_click(self, event):
        if self.entry_direction.get() == "Введите новое направление":
            self.entry_direction.delete(0, END)
            self.entry_direction.config(foreground="black")

    def on_entry_description_click(self, event):
        if self.entry_description.get() == "Введите описание":
            self.entry_description.delete(0, END)
            self.entry_description.config(foreground="black")

if __name__ == "__main__":
    app = UserInterface()
    app.run()
