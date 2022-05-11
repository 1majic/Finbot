class WalletNotFound(Exception):
    """Указанный кошелек не найден"""
    def __init__(self, message="Такого кошелька нет"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class EmptyExpenses(Exception):
    """Нет измененний за указанный промежуток"""
    def __init__(self, message="Нет записей о расходах/доходах за указанный промежуток"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NotCorrectWalletName(Exception):
    """Некорректное название кошелька"""
    def __init__(self, message="Некорректное название кошелька"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class EmailAlreadyReg(Exception):
    """Пользователь с таким Email уже зарегистрирован"""
    def __init__(self, message="Пользователь с таким Email уже зарегистрирован"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class EmailIncorrect(Exception):
    """Пользователь с таким Email уже зарегистрирован"""
    def __init__(self, message="Введите валидный Email"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class EmptyWalletList(Exception):
    """Список кошельков - пуст"""
    def __init__(self, message="Список кошельков - пуст"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class IncorrectCommand(Exception):
    """Некорректно задана команда"""
    def __init__(self, message="Некорректная команда"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class WalletNameAlreadyUsed(Exception):
    """Кошелек с тамим именем уже есть"""
    def __init__(self, message="Кошелек с тамим именем уже есть"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
