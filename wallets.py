import datetime
import db
from typing import NamedTuple, Optional

import exceptions


class Wallet(NamedTuple):
    """Стурктура добавленного кошелька в БД"""
    name: str
    date: Optional[str]


def add_wallet(name: str):
    """Добавление нового кошелька в базу данных"""
    all_wallets = db.wallet_list()
    wallet = name
    if wallet in all_wallets:
        return None
    db.new_table(name)
    return Wallet(name=name,
                  date=str(current_date()))


def all_balances():
    """Получение балансов всех кошельков и приведение их в читаемый вид"""
    walls = {}
    current_balance = 0
    result = []
    all_wallets = db.wallet_list()
    if not all_wallets:
        return exceptions.EmptyWalletList
    for i in all_wallets:
        income, outcome = get_balance(i)
        if not income:
            income = 0
        if not outcome:
            outcome = 0
        walls[i] = f'{income} {outcome}'
    for walls, values in walls.items():
        income, outcome = values.split()
        current_balance += float(income) - float(outcome)
        result.append(
            f'💼<b>{walls}</b>: {str(round(float(income) - float(outcome)))}р\n{" " * 10}Доход: {income}р\n'
            f'{" " * 10}Расход: {outcome}р')
    return result, current_balance


def delete_wallet(wallet_name):
    """Ссылка на функцию для удаления кошелька из БД"""
    return db.delete_wallet(wallet_name)


def get_balance(wallet):
    """Получение значений общего дохода и расхода у кошелька"""
    income = db.get_comes(wallet, 'Доход')[0]
    outcome = db.get_comes(wallet, 'Расход')[0]
    return income, outcome


def current_date():
    """Получение текущий даты"""
    current = datetime.datetime.today().date()
    return current
