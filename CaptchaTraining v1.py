import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import time
import mysql.connector
from mysql.connector import Error

class CaptchaGame:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.root.title("Captcha Training")
        self.root.geometry("600x600")
        self.root.resizable(False, False)  # Make the window non-resizable

        # Load the background image using PIL
        self.background_image = Image.open(r"D:\Captcha Training\back.png")  # Replace with the path to your background image
        self.background_image = self.background_image.resize((600, 600))
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Create a canvas for the background image
        self.canvas = tk.Canvas(self.root, width=600, height=600)
        self.canvas.pack(fill="both", expand=True)

        # Set the background image on the canvas
        self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        # Center the window
        self.root.update_idletasks()
        width = 600
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Set the window icon
        self.set_window_icon()

        self.attempts = 0
        self.max_attempts = 5
        self.code = ""
        self.start_time = None
        self.game_over = False
        self.total_time = 15  # Total time for all rounds

        # Create text and entry widgets on the canvas
        self.label = self.canvas.create_text(300, 120, text="Нажмите Enter, чтобы начать", font=("Helvetica", 24, "bold"), fill="#ffffff")

        # Create a transparent entry widget
        self.entry_var = tk.StringVar()
        self.entry = self.canvas.create_text(300, 300, text="", font=("Helvetica", 24), fill="#ffffff", anchor="center")
        self.entry_var.trace("w", lambda name, index, mode, var=self.entry_var: self.update_entry_text())

        self.result_label = self.canvas.create_text(300, 380, text="", font=("Helvetica", 18), fill="#ffffff")
        self.timer_label = self.canvas.create_text(300, 500, text="", font=("Helvetica", 18), fill="#ffffff")

        # Bind the Enter key to the root window
        self.root.bind("<Return>", self.start_or_check_code)
        self.root.bind("<Key>", self.on_key_press)

    def set_window_icon(self):
        # Set the window icon using iconbitmap
        self.root.iconbitmap(r"D:\Captcha Training\icon.ico")  # Replace with the path to your 32x32 or 16x16 icon file

    def generate_code(self):
        return str(random.randint(1000, 9999))

    def start_game(self):
        self.attempts = 0
        self.game_over = False
        self.start_time = time.time()
        self.next_round()
        self.update_timer()

    def next_round(self):
        if self.attempts < self.max_attempts and not self.game_over:
            self.code = self.generate_code()
            self.canvas.itemconfig(self.label, text=self.code)
            self.entry_var.set("")
            self.canvas.itemconfig(self.result_label, text="")
            self.root.focus_set()
        else:
            self.game_over = True
            self.canvas.itemconfig(self.result_label, text="Игра окончена! Нажмите Enter, чтобы начать заново.", fill="#ffffff")
            self.save_result()

    def check_code(self):
        if not self.game_over:
            user_input = self.entry_var.get()
            elapsed_time = time.time() - self.start_time
            if user_input == "":
                self.canvas.itemconfig(self.result_label, text="Введите число на экране", fill="#e74c3c")
            elif elapsed_time <= self.total_time:
                if user_input == self.code:
                    self.canvas.itemconfig(self.result_label, text="Правильно!", fill="#2ecc71")
                    self.attempts += 1
                    self.root.after(500, self.next_round)  # Add a 0.5-second delay before the next round
                else:
                    self.canvas.itemconfig(self.result_label, text="Введите правильно число", fill="#e74c3c")
            else:
                self.canvas.itemconfig(self.result_label, text="Время вышло! Игра окончена.", fill="#e74c3c")
                self.game_over = True
                self.save_result()

    def start_or_check_code(self, event):
        if self.game_over or self.start_time is None:
            self.start_game()
        else:
            self.check_code()

    def update_timer(self):
        if not self.game_over:
            elapsed_time = time.time() - self.start_time
            remaining_time = max(0, self.total_time - elapsed_time)
            self.canvas.itemconfig(self.timer_label, text=f"Осталось времени: {int(remaining_time)} сек.")
            if remaining_time > 0:
                self.root.after(1000, self.update_timer)
            else:
                self.canvas.itemconfig(self.result_label, text="Время вышло! Игра окончена.", fill="#e74c3c")
                self.game_over = True
                self.save_result()

    def update_entry_text(self):
        self.canvas.itemconfig(self.entry, text=self.entry_var.get())

    def on_key_press(self, event):
        if event.char.isdigit() or event.keysym == "BackSpace":
            current_text = self.entry_var.get()
            if event.keysym == "BackSpace":
                current_text = current_text[:-1]
            else:
                current_text += event.char
            self.entry_var.set(current_text)

    def save_result(self):
        try:
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("USE captcha_game")
                cursor.execute("INSERT INTO Результат (user_id, score) VALUES (%s, %s)", (self.user_id, self.attempts))
                connection.commit()
        except Error as e:
            print(f"Error while saving result to MySQL: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port='3306',       # Замените на ваш хост
            user='root',   # Замените на ваше имя пользователя
            password='Tut181183' # Замените на ваш пароль
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS captcha_game")
        cursor.execute("USE captcha_game")
        print("Database 'captcha_game' created or already exists")
    except Error as e:
        print(f"Error while creating database: {e}")

def create_tables(connection):
    try:
        cursor = connection.cursor()

        # Create Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Пользователи (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')

        # Create Results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Результат (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                score INT,
                FOREIGN KEY (user_id) REFERENCES Пользователи(id)
            )
        ''')

        # Create Login and Password table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Логин_и_Пароль (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                login_time DATETIME NOT NULL
            )
        ''')

        connection.commit()
        print("Tables created successfully")
    except Error as e:
        print(f"Error while creating tables: {e}")

def open_login_register_window(root):
    login_window = tk.Toplevel(root)
    login_window.title("Авторизация/Регистрация")
    login_window.geometry("300x300")
    login_window.resizable(False, False)

    # Center the login window
    login_window.update_idletasks()
    width = 300
    height = 300
    x = (login_window.winfo_screenwidth() // 2) - (width // 2)
    y = (login_window.winfo_screenheight() // 2) - (height // 2)
    login_window.geometry(f'{width}x{height}+{x}+{y}')

    # Set the window icon
    login_window.iconbitmap(r"D:\Captcha Training\icon.ico")  # Replace with the path to your 32x32 or 16x16 icon file

    # Create login/register widgets
    tk.Label(login_window, text="Имя пользователя:", fg="black", bg=login_window.cget("bg")).pack(pady=5)
    username_entry = tk.Entry(login_window, fg="black", bg="white")
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Пароль:", fg="black", bg=login_window.cget("bg")).pack(pady=5)
    password_entry = tk.Entry(login_window, show="*", fg="black", bg="white")
    password_entry.pack(pady=5)

    message_label = tk.Label(login_window, text="", fg="green", bg=login_window.cget("bg"))
    message_label.pack(pady=5)

    def login():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            try:
                connection = create_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("USE captcha_game")
                    cursor.execute("SELECT id FROM Пользователи WHERE username = %s AND password = %s", (username, password))
                    result = cursor.fetchone()
                    if result:
                        user_id = result[0]
                        messagebox.showinfo("Авторизация", f"Вы вошли как {username}")
                        save_login_info(username)  # Передаем username вместо user_id
                        game = CaptchaGame(root, user_id)
                        root.deiconify()  # Show the main window
                        login_window.withdraw()  # Hide the login window
                    else:
                        message_label.config(text="Неверное имя пользователя или пароль", fg="red")
            except Error as e:
                print("Error while connecting to MySQL", e)
            finally:
                if connection:
                    cursor.close()
                    connection.close()
        else:
            message_label.config(text="Пожалуйста, введите имя пользователя и пароль", fg="red")

    def register():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            try:
                connection = create_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("USE captcha_game")
                    cursor.execute("INSERT INTO Пользователи (username, password) VALUES (%s, %s)", (username, password))
                    connection.commit()
                    message_label.config(text="Регистрация успешна", fg="green")
            except Error as e:
                print("Error while connecting to MySQL", e)
            finally:
                if connection:
                    cursor.close()
                    connection.close()
        else:
            message_label.config(text="Пожалуйста, введите имя пользователя и пароль", fg="red")

    tk.Button(login_window, text="Войти", command=login, fg="black", bg="white").pack(pady=5)
    tk.Button(login_window, text="Зарегистрироваться", command=register, fg="black", bg="white").pack(pady=5)

def save_login_info(username):
    try:
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("USE captcha_game")
            cursor.execute("INSERT INTO Логин_и_Пароль (username, login_time) VALUES (%s, %s)", (username, time.strftime('%Y-%m-%d %H:%M:%S')))
            connection.commit()
    except Error as e:
        print(f"Error while saving login info to MySQL: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    connection = create_connection()
    if connection:
        create_database(connection)
        create_tables(connection)
        connection.close()

    root = tk.Tk()
    root.withdraw()  # Hide the main window initially
    open_login_register_window(root)
    root.mainloop()
