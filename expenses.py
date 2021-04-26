""" Работа с расходами — их добавление, удаление, статистики"""
from typing import NamedTuple

import db
import wallets


class Message(NamedTuple):
    """Структура распаршенного сообщения о новом расходе"""
    table: str
    amount: int
    comment: str


class Expense(NamedTuple):
    """Структура добавленного в БД нового расхода"""
    wallet: str
    type: str
    amount: int
    comment: str


def add_expense(wallet, exp_type, amount, comment) -> Expense:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    date = wallets.current_date()
    checked = db.check_wallet(wallet)
    if checked is True:
        db.insert(f"{wallet}", {
            "type": exp_type,
            "amount": amount,
            "comment": comment,
            "date": date
        })
        return Expense(wallet=wallet,
                       amount=amount,
                       comment=comment,
                       type=exp_type)
    return checked
