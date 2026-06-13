import pandas as pd

from config import EXCEL_FILE_PATH
from src.reports import spending_by_category
from src.services import filters_transactions_by_persons
from src.services import search_by_phone_number
from src.services import search_by_phrases
from src.utils import get_user_time
from src.utils import unique_categories
from src.views import main_info


def main() -> None:
    """Главная функция программы для работы с банковскими транзакциями"""
    print("\nПривет! Добро пожаловать в программу работы с банковскими транзакциями")

    while True:
        print("1. Перейти на главную страницу")
        print("2. Перейти к поиску транзакций")
        print("3. Выгрузить отчет о тратах по категориям")
        user_input = input("Введите номер пункта для продолжения работы: ")
        if user_input == "1":
            print("Перехожу на главную страницу...")
            print(get_user_time())

            input_date = input("Введите дату и время в формате YYYY-MM-DD HH:MM:SS: ")

            try:
                from datetime import datetime

                datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
                transactions = main_info(input_date)
                print(transactions)
            except ValueError:
                print("Неверный формат даты!")
                continue
            break
        elif user_input == "2":
            print("Перехожу к поиску транзакций...")
            print(get_user_time())
            while True:
                print("1. Для поиска по слову или фразе в графе 'Описание'")
                print("2. Для поиска по номеру телефона")
                print("3. Для поиска переводов физическим лицам")
                user_input = input("Введите номер пункта для продолжения работы: ")
                if user_input == "1":
                    print("Выбран поиск по слову или фразе в графе 'Описание'")
                    user_input = input("Введите слово или фразу для поиска в графе описание: ").title()
                    transactions = search_by_phrases(user_input)
                    print(transactions)
                    break
                elif user_input == "2":
                    print("Выбран поиск по номеру телефона")
                    user_input = input("Введите номер телефона для поиска: ")
                    transactions = search_by_phone_number(user_input)
                    print(transactions)
                    break
                elif user_input == "3":
                    print("Выбран поиск переводов физическим лицам")
                    user_input = input("Введите имя и фамилию с . для поиска: ")
                    transactions = filters_transactions_by_persons(user_input)
                    print(transactions)
                    break
                else:
                    print("Неверный ввод! Попробуйте еще раз")
            break
        elif user_input == "3":
            print("Перехожу к поиску транзакций по категории...")
            print(get_user_time())
            df = pd.read_excel(EXCEL_FILE_PATH)
            list_categories = unique_categories(df)
            print(f"Предложенные категории для поиска: {list_categories}")
            user_input = input("Введите название категории для поиска: ").title()
            date = input("Введите дату в формате DD.MM.YYYY: ")
            transactions = spending_by_category(df, user_input, date)
            print(transactions)
            break
        else:
            print("Неверный ввод! Попробуйте еще раз")
            print()


if __name__ == "__main__":
    main()
