import json
import logging
import requests
from datetime import datetime
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
import re

load_dotenv()
API_KEY = os.getenv("API_KEY")



current_file = Path(__file__)
project_root = current_file.parent.parent
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

log_file_ut = log_dir / "utils.log"

logging.getLogger("urllib3").setLevel(logging.WARNING)
logger_ut = logging.getLogger("utils")
logger_ut.setLevel(logging.DEBUG)


file_handler_ut = logging.FileHandler(log_file_ut, mode="w", encoding="utf-8")
file_handler_ut.setLevel(logging.DEBUG)


formatter = logging.Formatter("%(asctime)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler_ut.setFormatter(formatter)


logger_ut.addHandler(file_handler_ut)
logger_ut.propagate = False

def get_user_time():
    """ Функция возвращает «Доброе утро» / «Добрый день» /
    «Добрый вечер» / «Доброй ночи» в зависимости от текущего времени """
    logger_ut.info("Запуск функции get_user_time")
    user_date_time = datetime.now().hour
    if user_date_time < 12 and user_date_time >= 6:
        logger_ut.info("Функция get_user_time отработала")
        return "Доброе утро"
    elif user_date_time < 18 and user_date_time >= 12:
        logger_ut.info("Функция get_user_time отработала")
        return "Добрый день"
    elif user_date_time < 23 and user_date_time >= 18:
        logger_ut.info("Функция get_user_time отработала")
        return "Добрый вечер"
    else:
        logger_ut.info("Функция get_user_time отработала")
        return "Доброй ночи"

def get_date_period(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S")-> list[str]:
    """Функция возвращает диапазон от указанной даты и времени до начала месяца"""
    logger_ut.info("Функция get_date_period запущена")
    user_date_time = datetime.strptime(date_time, date_format)
    month_beginning = user_date_time.replace(day=1)
    logger_ut.info("Функция get_date_period отработала")
    return [
        month_beginning.strftime("%d.%m.%Y %H:%M:%S"),
        user_date_time.strftime("%d.%m.%Y %H:%M:%S")
    ]



def get_read_excel_file(file_path: str, date_period: list[str])-> pd.DataFrame:
    """Функция возвращает данные из файла Excel на период указанных дат"""
    logger_ut.info("Функция get_read_excel_file запущена")
    try:
        df = pd.read_excel(file_path, sheet_name="Отчет по операциям")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
        start_date = datetime.strptime(date_period[0],"%d.%m.%Y %H:%M:%S")
        end_date = datetime.strptime(date_period[1],"%d.%m.%Y %H:%M:%S")
        df_period = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
        logger_ut.info("Функция get_read_excel_file отработала")

        return df_period
    except Exception as e:
        logger_ut.error(f"Ошибка при чтении файла: {e}")
        return  pd.DataFrame()


def get_filtred_info(data: pd.DataFrame) -> list[dict]:
    """Функция возвращает последние 4 цифры карты, общую сумму расходов и кэшбэк"""
    logger_ut.info("Функция get_filtred_info запущена")
    cards = []
    data = data.copy()
    data["Номер карты"] = data["Номер карты"].fillna("")
    unique_cards = data[data["Номер карты"] != ""]["Номер карты"].unique()
    logger_ut.info("Функция get_filtred_info отфильтровала данные")
    for card in unique_cards:
        card_data = data[(data["Номер карты"] == card) & (data["Сумма операции"] < 0)]
        total_spent = round(abs(card_data["Сумма операции"].fillna(0).sum()), 2)
        cashback = round(total_spent * 0.01, 2)

        cards.append({
            "last_digits": card[-4:],
            "total_spent": float(total_spent),
            "cashback": float(cashback)
        })
    logger_ut.info("Функция get_filtred_info отработала")
    return cards

def get_top_five(data: pd.DataFrame) -> list[dict]:
    """Функция возвращает 5 самых дорогих операций"""
    logger_ut.info("Функция get_top_five запущена")
    top_transactions =[]
    data = data.copy()
    data_sort = data[(data["Сумма операции"] < 0)].sort_values(by="Сумма операции", ascending=True)
    for index, row in data_sort.iterrows():
        top_transactions.append({"date": row["Дата платежа"],
                                 "amount": abs(row["Сумма операции"]),
                                 "category": row["Категория"],
                                 "description": row["Описание"]})
    logger_ut.info("Функция get_top_five отработала")
    return top_transactions[:5]

def get_read_file(file_path: str)-> dict:
    """Функция для чтения данных из файла json"""
    logger_ut.info("Функция get_read_file запущена")
    try:
        logger_ut.info("Функция get_read_file читает файл")
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                logger_ut.info("Функция get_read_file отработала")
                return data
            else:
                logger_ut.info("Функция get_read_file отработала, но в переданных данных не словарь")
                return {}
    except FileNotFoundError:
        logger_ut.error("Функция get_read_file отработала, но файл не найден")
        return {}
    except json.decoder.JSONDecodeError:
        logger_ut.error("Функция get_read_file отработала, но файл не является валидным json")
        return {}
    except ValueError:
        logger_ut.error("Функция get_read_file отработала, но файл не является валидным json")
        return {}

def get_currency_rates(data: dict)-> list[dict]:
    """Функция для получения курса валют"""
    logger_ut.info("Функция get_currency_rates запущена")
    try:
        logger_ut.info("Функция get_currency_rates пробует отправить запрос")
        currencies = data.get("user_currencies", "")
        if not currencies or len(currencies) < 2:
            logger_ut.error("Недостаточно валют для обработки")
            return []

        user_currencies_usd = currencies[0]
        user_currencies_eur = currencies[1]
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        response = requests.get(url)
        response.raise_for_status()
        data_json = response.json()
        data_rates = []
        if response.status_code == 200:
            data_rates.append({"currency": user_currencies_usd, "rate": round(data_json["Valute"]["USD"]["Value"], 2)})
            data_rates.append({"currency": user_currencies_eur, "rate": round(data_json["Valute"]["EUR"]["Value"], 2)})
            logger_ut.info(f"Функция get_currency_rates отработала с кодом {response.status_code}")

        return data_rates
    except requests.RequestException as e:
        logger_ut.error(f"Функция get_currency_rates отработала с ошибкой {e} ")
        return []
    except (ValueError, TypeError, AttributeError) as e:
        logger_ut.error(f"Функция get_currency_rates отработала с ошибкой {e}")
        return []


def get_stocks(data: dict) -> list:
    """Функция для получения списка тикеров акций из входных данных"""
    logger_ut.info("Функция get_stocks запущена")

    stocks = data.get("user_stocks", [])
    if isinstance(stocks, str):
        stocks = [s.strip() for s in stocks.split(",") if s.strip()]
    logger_ut.info(f"Получены тикеры: {stocks}")
    return stocks


def get_stocks_info(data: list) -> list[dict]:
    """Функция для получения информации о ценах акций"""
    logger_ut.info("Функция get_stocks_info запущена")
    try:
        all_results = []
        for d in data:
            url = f"https://api.twelvedata.com/price?symbol={d}&apikey={API_KEY}"
            response = requests.get(url)
            result = response.json()
            all_results.append({"stock": d, "price": round(float(result["price"]), 2)})
            logger_ut.info("Функция get_stocks_info отработала")

        return all_results

    except requests.RequestException as e:
        logger_ut.error(f"Функция get_stocks_info отработала с ошибкой {e}")
        return []
    except KeyError as e:
        logger_ut.error(f"Отсутствует необходимый ключ в данных: {e}")
        return []
    except Exception as e:
        logger_ut.error(f"Функция get_stocks_info отработала с ошибкой {e}")
        return []


def normalize(user_input: str) -> str:
    """Функция переводит введенный номер телефона в формат для поиска (+7 XXX XX-XX-XX)"""
    logger_ut.info("Функция normalize запущена")
    digits = re.sub(r'\D', '', user_input)

    if digits.startswith('8') and len(digits) == 11:
        return f"+7 {digits[1:4]} {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"

    elif digits.startswith('7') and len(digits) == 11:
        return f"+7 {digits[1:4]} {digits[4:7]}-{digits[7:9]}-{digits[9:10]}"

    elif len(digits) == 10 and digits.startswith('9'):
        return f"+7 {digits[0:3]} {digits[3:5]}-{digits[5:7]}-{digits[7:9]}"

    elif len(digits) == 10:
        return f"+7 {digits[0:3]} {digits[3:5]}-{digits[5:7]}-{digits[7:9]}"

    elif len(digits) < 10 and digits.startswith('9'):
        return f"+7 {digits[0:3]} {digits[3:5]}-{digits[5:7]}-{digits[7:9]}"

    else:
        last_10 = digits[-10:]
        return f"+7 {last_10[0:3]} {last_10[3:5]}-{last_10[5:7]}-{last_10[7:9]}"

