import loggings
from aiogram import Bot, Dispatcher, executor, types

import authorization
import exceptions
import wallets
import db
import expenses

loggings.lets_logging("info", "\n\nЗапуск")
API_TOKEN = "1592423126:AAHQvZ1hQbHrKu3mwprW8uWEmWefRr9bB-A"

if API_TOKEN == "1592423126:AAHQvZ1hQbHrKu3mwprW8uWEmWefRr9bB-A":
    print("http://t.me/ODFinancebbBot")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

Log = False

illegal_wallet_names = "'/^(?![_.])(?!.*[-_.]{2})+(?<![-_.])$/" + '"' + 'всех все общий баланс'


# Декораторы для проверки авторизации пользователя
def is_login(func):
    async def wrapper(message: types.Message):
        if Log is False:
            await start(message)
        else:
            await func(message)

    return wrapper


def no_login(func):
    async def wrapper(message: types.Message):
        if Log is False:
            await func(message)
        else:
            await message.answer("Вы уже вошли в учетную запись")

    return wrapper


@dp.message_handler(commands=['start'])
@no_login
async def start(message: types.Message):
    """Начальная команда для авторизации пользователя"""
    if Log is False:
        await message.answer('Для входа/регистрации введите:\n/login "email" "пароль"\n /reg "email" "пароль" \n')


@dp.message_handler(lambda message: message.text.lower().startswith("/login "))
@no_login
async def login(message: types.Message):
    """Авторизация пользователя"""
    try:
        global Log
        text = message.text.split()
        if len(text) != 3:
            raise exceptions.IncorrectCommand
        email = text[1]
        password = text[2]
        checked = authorization.check_user(password, email)
        if checked:
            Log = True
            db.init_db(email)
            await message.answer('Успешно')
            loggings.lets_logging('info', f'Пользователь {email} - вошел')
            await send_help(message)
        else:
            await message.answer('Некорректные данные')
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{e}"')
        await message.answer(f"{str(e)}")


@dp.message_handler(lambda message: message.text.lower().startswith("/reg "))
@no_login
async def register(message: types.Message):
    """Регистрация пользователя"""
    try:
        global Log
        text = message.text.split()
        if len(text) != 3:
            raise exceptions.IncorrectCommand
        email = text[1]
        password = text[2]
        checked = authorization.add_user(password, email)
        if checked:
            await message.answer("Пользователь с таким Email уже зарегистрирован")
        else:
            Log = True
            db.init_db(email)
            await message.answer('Успешно')
            loggings.lets_logging('info', f'Пользователь {email} - вошел')
            await send_help(message)
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{e}"')
        await message.answer(f"{str(e)}")


@dp.message_handler(commands=['help'])
@is_login
async def send_help(message: types.Message):
    """Отправляет помощь по боту"""
    await message.answer(
        'Команды:\n\n'
        '<b>"Список кошельков"</b> - выводит список всех кошельков\n\n'
        '<b>"Общий баланс"</b> - выводит балансы всех кошельков и их сумму\n\n'
        '<b>"Добавить/Удалить кошелек (название)"</b> - Добавить или удалить кошелек\n\n'
        '<b>"Добавить в (название кошелька) доход/расход (сумма) (комментарий)"</b> - Добавляет расход или доход в '
        'указанный кошелек\n\n '
        '<b>"Показать изменения за день/месяц/год/(дд.месяц.год) на всех/(название кошелька)"</b> - Показывает все '
        'операции за указанный промежуток',
        parse_mode=types.ParseMode.HTML)


@dp.message_handler(lambda message: message.text.lower().startswith("общий баланс"))
@is_login
async def all_balances(message: types.Message):
    """Показывает общий баланс и баланс каждого кошелька отдельно"""
    try:
        loggings.lets_logging('info', 'Вызвана команда "общий баланс"')
        result = wallets.all_balances()
        if result == exceptions.EmptyWalletList:
            raise result
        balance, result = result[1], result[0]
        await message.answer('\n\n'.join(result), parse_mode=types.ParseMode.HTML)
        await message.answer(f'Общий баланс по всем кошелькам: <b>{str(round(balance))}р</b>',
                             parse_mode=types.ParseMode.HTML)
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{str(e)}"')
        await message.answer(f"{str(e)}")


@dp.message_handler(lambda message: message.text.lower().startswith("добавить кошелек"))
@is_login
async def add_wallet(message: types.Message):
    """Добавляет кошелек в базу данных"""
    try:
        loggings.lets_logging('info', 'Вызвана команда "добавить кошелек"')
        text = message.text.split()
        wallet_name = text[2]
        if wallet_name in illegal_wallet_names:
            raise exceptions.NotCorrectWalletName
        wallet = wallets.add_wallet(wallet_name)
        if wallet is None:
            raise exceptions.WalletNameAlreadyUsed
        else:
            await message.answer(f'Кошелек "<b>{wallet.name}</b>" создан в {db.deparse_date(str(wallet.date))}',
                                 parse_mode=types.ParseMode.HTML)
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{e}"')
        await message.answer(f"{str(e)}")


@dp.message_handler(lambda message: message.text.lower().startswith("удалить кошелек"))
@is_login
async def del_wallet(message: types.Message):
    """Удаляет кошелек из базы данных"""
    try:
        loggings.lets_logging('info', 'Вызвана команда "удалить кошелек"')
        text = message.text.split()
        if len(text) != 3:
            raise exceptions.IncorrectCommand
        wallet_name = text[2]
        wallet = wallets.delete_wallet(wallet_name)
        if ('no such table' in str(wallet)) or ('syntax error' in str(wallet)):
            raise exceptions.WalletNotFound
        else:
            await message.answer(f'Кошелек "<b>{wallet_name}</b>" удален', parse_mode=types.ParseMode.HTML)
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{e}"')
        await message.answer(f"{str(e)}")


@dp.message_handler(lambda message: message.text.lower().startswith("список кошельков"))
@is_login
async def wallet_list(message: types.Message):
    """Отображает список всех кошельков у данного пользователя"""
    try:
        loggings.lets_logging('info', 'Вызвана команда "список кошелько"')
        all_wallets = '\n'.join(db.wallet_list())
        if not all_wallets:
            raise exceptions.EmptyWalletList
        await message.answer(f"Список всех кошельков:\n\n{all_wallets}")
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{e}"')
        await message.answer(f"{str(e)}")


@dp.message_handler(lambda message: message.text.lower().startswith("добавить в "))
@is_login
async def add_expense(message: types.Message):
    """Добавляет доход/расход в базу данных"""
    try:
        loggings.lets_logging('info', 'Вызвана команда "добавить доход/расход"')
        text = message.text.split()
        if len(text) < 6:
            raise exceptions.IncorrectCommand
        wallet_name = text[2]
        exp_type = text[3]
        amount = text[4]
        comment = ' '.join(text[5:])
        expensive = expenses.add_expense(wallet_name, exp_type.lower(), amount, comment)
        if expensive == exceptions.WalletNotFound:
            raise exceptions.WalletNotFound
        await message.answer(f'В "<b>{expensive.wallet}</b>" добавлен {expensive.type} {expensive.amount}',
                             parse_mode=types.ParseMode.HTML)
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{e}"')
        await message.answer(f"{str(e)}")


@dp.message_handler(lambda message: message.text.lower().startswith("показать изменения за день "))
@is_login
async def show_expenses_day(message: types.Message):
    """Показывает все изменения кошелька/всех кошельков за день"""
    try:
        loggings.lets_logging('info', 'Вызвана команда "показать изменения за день"')
        text = message.text.split()
        if len(text) != 6:
            raise exceptions.IncorrectCommand
        wallet_name = text[5]
        result = db.get_expenses_day(wallet_name)
        if 'no such table' in str(result):
            raise exceptions.WalletNotFound
        elif result:
            await message.answer('\n\n'.join(result), parse_mode=types.ParseMode.HTML)
        else:
            raise exceptions.EmptyExpenses
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{e}"')
        await message.answer(f"{str(e)}")


@dp.message_handler(lambda message: message.text.lower().startswith("показать изменения за месяц "))
@is_login
async def show_expenses_month(message: types.Message):
    """Показывает все изменения кошелька/всех кошельков за месяц"""
    try:
        loggings.lets_logging('info', 'Вызвана команда "показать изменения за месяц"')
        text = message.text.split()
        if len(text) != 6:
            raise exceptions.IncorrectCommand
        wallet_name = text[5]
        result = db.get_expenses_month(wallet_name)
        if 'no such table' in str(result):
            raise exceptions.WalletNotFound
        if result:
            await message.answer('\n\n'.join(result), parse_mode=types.ParseMode.HTML)
        else:
            raise exceptions.EmptyExpenses
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{e}"')
        await message.answer(f"{str(e)}")


@dp.message_handler(lambda message: message.text.lower().startswith("показать изменения за год "))
@is_login
async def show_expenses_year(message: types.Message):
    """Показывает все изменения кошелька/всех кошельков за год"""
    try:
        loggings.lets_logging('info', 'Вызвана команда "показать изменения за год"')
        text = message.text.split()
        if len(text) != 6:
            raise exceptions.IncorrectCommand
        wallet_name = text[5]
        result = db.get_expenses_year(wallet_name)
        if 'no such table' in str(result):
            raise exceptions.WalletNotFound
        if result:
            await message.answer('\n\n'.join(result), parse_mode=types.ParseMode.HTML)
        else:
            raise exceptions.EmptyExpenses
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{e}"')
        await message.answer(f"{str(e)}")


@dp.message_handler(lambda message: message.text.lower().startswith("показать изменения за "))
@is_login
async def show_expenses_date(message: types.Message):
    """Показывает все изменения кошелька/всех кошельков за определенный день"""
    try:
        loggings.lets_logging('info', 'Вызвана команда "показать изменения за дату"')
        text = message.text.split()
        if len(text) != 6:
            raise exceptions.IncorrectCommand
        date = text[3]
        wallet_name = text[5]
        result = db.get_expenses_date(date, wallet_name)
        if 'no such table' in str(result):
            raise exceptions.WalletNotFound
        if result:
            await message.answer('\n\n'.join(result), parse_mode=types.ParseMode.HTML)
        else:
            raise exceptions.EmptyExpenses
    except Exception as e:
        loggings.lets_logging('warning', f'Ошибка:{e}"')
        await message.answer(f"{str(e)}")


@dp.message_handler()
@is_login
async def unrecognized_command(message: types.Message):
    await message.answer("Неопознанная команда. Наберите <b>/help</b> для отображения списка команд.",
                         parse_mode=types.ParseMode.HTML)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
