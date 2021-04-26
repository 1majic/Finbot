import sqlite3
from typing import Dict

import exceptions
import wallets

conn = sqlite3.connect("db/users.db")
cursor = conn.cursor()

current_user = ''


def check_user(password: str, email: str):
    cursor.execute(f"SELECT * FROM users WHERE email='{email}' and password='{password}'")
    check = cursor.fetchall()
    return check


def add_user(password: str, email: str):
    cursor.execute(f"SELECT * FROM users WHERE email='{email}'")
    if cursor.fetchall():
        return exceptions.EmailAlreadyReg
    insert("users", {
        "email": email,
        "password": password,
        "date": wallets.current_date()
    })


def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()
