import tkinter as tk
from tkinter import messagebox
import sqlite3


# Функции для работы с базой данных
def connect_db():
    return sqlite3.connect('bookstore.db')


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            genre TEXT,
            author TEXT,
            year_published INTEGER,
            pages INTEGER,
            medium TEXT,
            sales_count INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Catalog (
            book_id INTEGER PRIMARY KEY,
            retail_price REAL,
            FOREIGN KEY(book_id) REFERENCES Books(book_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Stores (
            book_id INTEGER PRIMARY KEY,
            wholesale_price REAL,
            in_stock INTEGER,
            sales_count INTEGER,
            FOREIGN KEY(book_id) REFERENCES Books(book_id)
        )
    ''')
    conn.commit()
    conn.close()


# Функции для управления книгами
def add_book(book, wholesale_price, retail_price):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Books (title, genre, author, year_published, pages, medium)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', book)
    book_id = cursor.lastrowid
    cursor.execute('''
        INSERT INTO Catalog (book_id, retail_price)
        VALUES (?, ?)
    ''', (book_id, retail_price))
    cursor.execute('''
        INSERT INTO Stores (book_id, wholesale_price, in_stock, sales_count)
        VALUES (?, ?, 0, 0)
    ''', (book_id, wholesale_price))
    conn.commit()
    conn.close()


def delete_book(book_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Books WHERE book_id = ?', (book_id,))
    cursor.execute('DELETE FROM Catalog WHERE book_id = ?', (book_id,))
    cursor.execute('DELETE FROM Stores WHERE book_id = ?', (book_id,))
    conn.commit()
    conn.close()


def get_books_by_genre(genre):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Books WHERE genre = ?', (genre,))
    books = cursor.fetchall()
    conn.close()
    return books


def get_books_by_author(author):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Books WHERE author = ?', (author,))
    books = cursor.fetchall()
    conn.close()
    return books


def get_top_selling_author():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT author, SUM(sales_count) as total_sales
        FROM Books
        GROUP BY author
        ORDER BY total_sales DESC
        LIMIT 1
    ''')
    author = cursor.fetchone()
    conn.close()
    return author


def get_out_of_stock_books():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Books.title
        FROM Books
        LEFT JOIN Stores ON Books.book_id = Stores.book_id
        WHERE Stores.in_stock = 0 OR Stores.in_stock IS NULL
    ''')
    books = cursor.fetchall()
    conn.close()
    return books


def get_total_revenue():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(Stores.sales_count * Catalog.retail_price) as total_revenue
        FROM Stores
        JOIN Catalog ON Stores.book_id = Catalog.book_id
    ''')
    revenue = cursor.fetchone()
    conn.close()
    return revenue


def get_book_max_price_difference():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Books.title, (Stores.wholesale_price - Catalog.retail_price) as price_difference
        FROM Books
        JOIN Catalog ON Books.book_id = Catalog.book_id
        JOIN Stores ON Books.book_id = Stores.book_id
        ORDER BY price_difference DESC
        LIMIT 1
    ''')
    book = cursor.fetchone()
    conn.close()
    return book


# Интерфейс
def show_books_by_genre_ui():
    def submit():
        genre = entry_genre.get()
        books = get_books_by_genre(genre)
        result_text.set('\n'.join([f"{book[1]}, {book[2]}, {book[3]}" for book in books]))

    genre_window = tk.Toplevel(root)
    genre_window.title("Поиск по жанру")
    genre_window.geometry("400x400")

    tk.Label(genre_window, text="Жанр").grid(row=0, column=0, padx=10, pady=10)
    entry_genre = tk.Entry(genre_window)
    entry_genre.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(genre_window, text="Ввести", command=submit).grid(row=1, column=1, pady=10)
    result_text = tk.StringVar()
    tk.Label(genre_window, textvariable=result_text).grid(row=2, column=0, columnspan=2, padx=10, pady=10)


def show_books_by_author_ui():
    def submit():
        author = entry_author.get()
        books = get_books_by_author(author)
        result_text.set('\n'.join([f"{book[1]}, {book[2]}, {book[3]}" for book in books]))

    author_window = tk.Toplevel(root)
    author_window.title("Поиск по автору")
    author_window.geometry("400x400")

    tk.Label(author_window, text="Имя Автора").grid(row=0, column=0, padx=10, pady=10)
    entry_author = tk.Entry(author_window)
    entry_author.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(author_window, text="Ввести", command=submit).grid(row=1, column=1, pady=10)
    result_text = tk.StringVar()
    tk.Label(author_window, textvariable=result_text).grid(row=2, column=0, columnspan=2, padx=10, pady=10)


def show_top_selling_author_ui():
    top_author = get_top_selling_author()
    result_text = f"Самый продаваемый автор: {top_author[0]}, Total Sales: {top_author[1]}"
    tk.messagebox.showinfo("Самый продаваемый автор", result_text)


def show_login_ui():
    def submit():
        username = entry_username.get()
        password = entry_password.get()
        if username == "admin" and password == "admin":
            tk.messagebox.showinfo("Верно", "Вы вошли")
            login_window.destroy()
            show_admin_ui()
        else:
            tk.messagebox.showerror("Ошибка", "Неверный логин или пароль")

    login_window = tk.Toplevel(root)
    login_window.title("Вход")
    login_window.geometry("300x200")

    tk.Label(login_window, text="Логин").grid(row=0, column=0, padx=10, pady=10)
    tk.Label(login_window, text="Пароль").grid(row=1, column=0, padx=10, pady=10)

    entry_username = tk.Entry(login_window)
    entry_password = tk.Entry(login_window, show="*")

    entry_username.grid(row=0, column=1, padx=10, pady=10)
    entry_password.grid(row=1, column=1, padx=10, pady=10)

    tk.Button(login_window, text="Войти", command=submit).grid(row=2, column=1, pady=10)


def show_admin_ui():
    tk.Button(root, text="Добавить книгу", command=add_book_ui, bg='green', fg='white').grid(row=2, column=0, padx=20, pady=20)
    tk.Button(root, text="Удалить книгу", command=delete_book_ui, bg='red', fg='white').grid(row=2, column=1, padx=20,
                                                                                            pady=20)
    tk.Button(root, text="Нет в наличии", command=show_out_of_stock_books_ui, bg='gray', fg='white').grid(row=2,column=2,padx=20,pady=20)
    tk.Button(root, text="Общая выручка", command=show_total_revenue_ui, bg='gray', fg='white').grid(row=2, column=3,padx=20, pady=20)
    tk.Button(root, text="Самый прибыльный экземпляр", command=show_book_max_price_difference_ui, bg='gray',fg='white').grid(row=2, column=4, padx=20, pady=20)


def add_book_ui():
    def submit():
        title = entry_title.get()
        genre = entry_genre.get()
        author = entry_author.get()
        year = entry_year.get()
        pages = entry_pages.get()
        medium = entry_medium.get()
        wholesale_price = float(entry_wholesale_price.get())
        retail_price = float(entry_retail_price.get())

        add_book((title, genre, author, year, pages, medium), wholesale_price, retail_price)
        messagebox.showinfo("Success", "Book added successfully")
        add_window.destroy()

    add_window = tk.Toplevel(root)
    add_window.title("Добавление книги")
    add_window.geometry("400x400")

    tk.Label(add_window, text="Название").grid(row=0, column=0, padx=10, pady=10)
    tk.Label(add_window, text="Жанр").grid(row=1, column=0, padx=10, pady=10)
    tk.Label(add_window, text="Автор").grid(row=2, column=0, padx=10, pady=10)
    tk.Label(add_window, text="Год выпуска").grid(row=3, column=0, padx=10, pady=10)
    tk.Label(add_window, text="Кол-во страниц").grid(row=4, column=0, padx=10, pady=10)
    tk.Label(add_window, text="Вид").grid(row=5, column=0, padx=10, pady=10)
    tk.Label(add_window, text="Цена закупки").grid(row=6, column=0, padx=10, pady=10)
    tk.Label(add_window, text="Цена продажи").grid(row=7, column=0, padx=10, pady=10)

    entry_title = tk.Entry(add_window)
    entry_genre = tk.Entry(add_window)
    entry_author = tk.Entry(add_window)
    entry_year = tk.Entry(add_window)
    entry_pages = tk.Entry(add_window)
    entry_medium = tk.Entry(add_window)
    entry_wholesale_price = tk.Entry(add_window)
    entry_retail_price = tk.Entry(add_window)

    entry_title.grid(row=0, column=1, padx=10, pady=10)
    entry_genre.grid(row=1, column=1, padx=10, pady=10)
    entry_author.grid(row=2, column=1, padx=10, pady=10)
    entry_year.grid(row=3, column=1, padx=10, pady=10)
    entry_pages.grid(row=4, column=1, padx=10, pady=10)
    entry_medium.grid(row=5, column=1, padx=10, pady=10)
    entry_wholesale_price.grid(row=6, column=1, padx=10, pady=10)
    entry_retail_price.grid(row=7, column=1, padx=10, pady=10)

    tk.Button(add_window, text="Ок", command=submit).grid(row=8, column=1, pady=10)


def delete_book_ui():
    def submit():
        book_id = entry_book_id.get()
        delete_book(book_id)
        messagebox.showinfo("Success", "Book deleted successfully")
        delete_window.destroy()

    delete_window = tk.Toplevel(root)
    delete_window.title("Удалить книгу")
    delete_window.geometry("300x200")

    tk.Label(delete_window, text="ID книги").grid(row=0, column=0, padx=10, pady=10)
    entry_book_id = tk.Entry(delete_window)
    entry_book_id.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(delete_window, text="ОК", command=submit).grid(row=1, column=1, pady=10)


def show_out_of_stock_books_ui():
    books = get_out_of_stock_books()
    result_text = '\n'.join([book[0] for book in books])
    tk.messagebox.showinfo("Нет в наличии", result_text)


def show_total_revenue_ui():
    revenue = get_total_revenue()
    result_text = f"Общая выручка: {revenue[0]:.2f}"
    tk.messagebox.showinfo("Общая выручка", result_text)


def show_book_max_price_difference_ui():
    book = get_book_max_price_difference()
    result_text = f"Самый выгодный экземпляр: {book[0]}, Выгода: {book[1]:.2f} Рублей"
    tk.messagebox.showinfo("Самый выгодный экземпляр", result_text)


# Инициализация приложения
root = tk.Tk()
root.title("Bookstore Management System")
root.geometry("800x600")

create_tables()

# Основные кнопки для всех пользователей
tk.Button(root, text="Поиск по жанру", command=show_books_by_genre_ui, bg='lightblue').grid(row=0, column=0, padx=20,pady=20)
tk.Button(root, text="Поиск по автору", command=show_books_by_author_ui, bg='lightblue').grid(row=0, column=1, padx=20,pady=20)
tk.Button(root, text="Самый продаваемый автор", command=show_top_selling_author_ui, bg='lightblue').grid(row=0, column=2,padx=20, pady=20)
tk.Button(root, text="Я работник магазины", command=show_login_ui, bg='lightgreen').grid(row=0, column=4, padx=20, pady=20)

root.mainloop()
