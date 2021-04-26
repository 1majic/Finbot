from typing import Dict

import sqlite3
import wallets
import exceptions
from loggings import lets_logging


def init_db(user):
    """Инициализирует БД"""
    global conn
    global cursor
    conn = sqlite3.connect(f"db/{user}.db")
    cursor = conn.cursor()
    lets_logging("info", f"База данных {user} инициализирована")


def insert(table: str, column_values: Dict):
    """Вставляет значения операции в таблицу БД"""
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def wallet_list():
    """Возвращает список всех существующих кошельков пользователя"""
    cursor.execute('SELECT name from sqlite_master where type= "table"')
    tuples_wallet = cursor.fetchall()
    walls = []
    for i in tuples_wallet:
        walls.append(i[0])
    return walls


def check_wallet(wallet):
    """Проверка наличия кошелька в базе"""
    if wallet in wallet_list():
        return True
    return exceptions.WalletNotFound


def new_table(name):
    """Создание нового кошелька(таблицы)"""
    cursor.execute(f"""CREATE TABLE {name}(
    amount FLOAT ,
    type TEXT ,
    comment TEXT ,
    date TEXT)""")
    lets_logging("info", f"Создана новая таблица - {name}")
    conn.commit()


def get_comes(wallet, exp_type):
    """Возвращает сумму операций определенного вида(доход/расход)"""
    cursor.execute(f'SELECT sum(amount) from {wallet} where type="{exp_type.lower()}"')
    return cursor.fetchall()[0]


def get_expenses_day(wallet):
    """Получение списка операций за текущий день"""
    date = wallets.current_date()
    try:
        if 'все' in wallet:
            all_wallets_expenses = []
            for i in wallet_list():
                cursor.execute(f"SELECT * FROM {i} WHERE date(date)='{date}'")
                ftc = exp_reader(list(cursor.fetchall()))
                if not ftc:
                    continue
                all_wallets_expenses.append('💼<b>' + i + '</b>:\n' + parse_message(ftc))
            return all_wallets_expenses
        else:
            cursor.execute(f"SELECT * FROM {wallet} WHERE date(date)='{date}'")
            ftc = exp_reader(list(cursor.fetchall()))
            return [parse_message(ftc)]
    except Exception as e:
        return e


def get_expenses_month(wallet):
    """Получение списка операций за текущий месяц"""
    date = wallets.current_date()
    first_day_of_month = f'{date.year:04d}-{date.month:02d}-01'
    if 'все' in wallet:
        all_wallets_expenses = []
        for i in wallet_list():
            cursor.execute(f"SELECT * FROM {i} WHERE date(date)>='{first_day_of_month}'")
            ftc = exp_reader(list(cursor.fetchall()))
            if not ftc:
                continue
            all_wallets_expenses.append('💼<b>' + i + '</b>:\n' + parse_message(ftc))
        return all_wallets_expenses
    else:
        cursor.execute(f"SELECT * FROM {wallet} WHERE date(date)>='{first_day_of_month}'")
        ftc = exp_reader(list(cursor.fetchall()))
        return [parse_message(ftc)]


def get_expenses_year(wallet):
    """Получение списка операций за текущий год"""
    date = wallets.current_date()
    first_month = f'{date.year:04d}-01-01'
    if 'все' in wallet:
        all_wallets_expenses = []
        for i in wallet_list():
            cursor.execute(f"SELECT * FROM {i} WHERE date(date)>='{first_month}'")
            ftc = exp_reader(list(cursor.fetchall()))
            if not ftc:
                continue
            all_wallets_expenses.append('💼<b>' + i + '</b>:\n' + parse_message(ftc))
        return all_wallets_expenses
    else:
        cursor.execute(f"SELECT * FROM {wallet} WHERE date(date)>='{first_month}'")
        ftc = exp_reader(list(cursor.fetchall()))
        return [parse_message(ftc)]


def get_expenses_date(date, wallet):
    """Получение списка операций за определенный день"""
    date = parse_date(date)
    if 'все' in wallet:
        all_wallets_expenses = []
        for i in wallet_list():
            cursor.execute(f"SELECT * FROM {i} WHERE date(date)='{date}'")
            ftc = exp_reader(list(cursor.fetchall()))
            if not ftc:
                continue
            all_wallets_expenses.append(i + ':\n' + parse_message(ftc))
        return all_wallets_expenses
    else:
        cursor.execute(f"SELECT * FROM {wallet} WHERE date(date)='{date}'")
        ftc = exp_reader(list(cursor.fetchall()))
        if ftc:
            return [parse_message(ftc)]
        return ftc


def parse_message(text):
    """Преобразует вид операций в более читаемый вид"""
    all_operations = []
    for i in sorted(text, reverse=True, key=lambda x: x[-1]):
        amount, exp_type, comment, date = i
        if exp_type == 'доход':
            all_operations.append(f'    +{amount} в {date}: {comment}')
        else:
            all_operations.append(f'    -{amount} в {date}: {comment}')
    return '\n'.join(all_operations)


def parse_date(date):
    """Преобразует дату в формат понятный SQLite"""
    date = date.split('.')
    return f'{date[-1]}-{date[-2]}-{date[-3]}'


def deparse_date(date):
    """Преобразует дату из SQLite формата в обычный"""
    date = date.split('-')
    return f'{date[-1]}.{date[-2]}.{date[-3]}'


def delete_wallet(wallet: str):
    """Удаляет кошелек(таблицу) из БД"""
    try:
        cursor.execute(f'DROP TABLE {wallet}')
    except Exception as e:
        return e


def exp_reader(lst_of_exp):
    """Помогает преобразовать вид операций в более приятный вид"""
    result = []
    for i in lst_of_exp[::]:
        date = deparse_date(i[-1])
        result.append((i[:3] + (date,)))
    return result
