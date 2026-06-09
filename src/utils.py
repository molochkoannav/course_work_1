from datetime import datetime
from enum import unique

import pandas as pd
from pandas import DataFrame as Dataframe


def get_user_time():
    """ Функция возвращает «Доброе утро» / «Добрый день» /
    «Добрый вечер» / «Доброй ночи» в зависимости от текущего времени """

    user_date_time = datetime.now().hour
    if user_date_time < 12 and user_date_time >= 6:
        return "Доброе утро"
    elif user_date_time < 18 and user_date_time >= 12:
        return "Добрый день"
    elif user_date_time < 23 and user_date_time >= 18:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def get_date_period(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S")-> list[str]:
    """Функция возвращает диапазон от указанной даты и времени до начала месяца"""

    user_date_time = datetime.strptime(date_time, date_format)
    month_beginning = user_date_time.replace(day=1)

    return [
        month_beginning.strftime("%d.%m.%Y %H:%M:%S"),
        user_date_time.strftime("%d.%m.%Y %H:%M:%S")
    ]



def get_read_excel_file(file_path: str, date_period: list[str])-> pd.DataFrame:
    """Функция возвращает данные из файла Excel на период указанных дат"""
    df = pd.read_excel(file_path, sheet_name="Отчет по операциям")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    start_date = datetime.strptime(date_period[0],"%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(date_period[1],"%d.%m.%Y %H:%M:%S")
    df_period = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]


    return df_period


def get_filtred_info(data: pd.DataFrame) -> list[dict]:
    """Функция возвращает последние 4 цифры карты, общую сумму расходов и кешбек"""
    cards = []


    data = data.copy()
    data["Номер карты"] = data["Номер карты"].fillna("")
    unique_cards = data[data["Номер карты"] != ""]["Номер карты"].unique()

    for card in unique_cards:
        card_data = data[(data["Номер карты"] == card) & (data["Сумма операции"] < 0)]
        total_spent = abs(card_data["Сумма операции"].fillna(0).sum())




        cashback = round(total_spent * 0.01, 2)

        cards.append({
            "last_digits": card[-4:],
            "total_spent": float(total_spent),
            "cashback": float(cashback)
        })

    return cards

def get_top_five(data: pd.DataFrame) -> list[dict]:
    """Функция возвращает 5 самых дорогих операций"""
    # top_five = data[data["Сумма операции"] < 0].sort_values(by="Сумма операции", ascending=False).head(5)
    # top_five = top_five[["Номер карты", "Описание операции", "Сумма операции"]]
    # top_five["Номер карты"] = top_five["Номер карты"].apply(lambda x: x[-4:])
    # top_five["Сумма операции"] = top_five["Сумма операции"].apply(lambda x: abs(x))
    # return top_five.to_dict(orient="records")



