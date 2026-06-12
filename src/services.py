import re
from typing import List, Dict

import pandas as pd
from pathlib import Path
import logging
from tabulate import tabulate

from src.utils import normalize

current_file = Path(__file__)
project_root = current_file.parent.parent
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

log_file_sv = log_dir / "services.log"

logging.getLogger("urllib3").setLevel(logging.WARNING)
logger_sv = logging.getLogger("services")
logger_sv.setLevel(logging.DEBUG)


file_handler_sv = logging.FileHandler(log_file_sv, mode="w", encoding="utf-8")
file_handler_sv.setLevel(logging.DEBUG)


formatter = logging.Formatter("%(asctime)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler_sv.setFormatter(formatter)


logger_sv.addHandler(file_handler_sv)
logger_sv.propagate = False


def search_by_phrases(user_input: str) -> list[dict]:
    """Функция возвращает список транзакций по введенному пользователем запросу"""
    try:
        logger_sv.info("Запуск поиска")
        pd_excel = pd.read_excel("data/operations.xlsx")
        logger_sv.info(f"Успешно прочитано {len(pd_excel)} строк")

        user_input = user_input.lower()

        mask = pd_excel["Описание"].str.lower().str.contains(user_input, na=False)
        filtered_transaction = pd_excel[mask]

        if len(filtered_transaction) > 0:
            logger_sv.info(f"Успешно отфильтровано {len(filtered_transaction)} строк")
            json_records = filtered_transaction.to_dict(orient="records")
            result = tabulate(json_records, headers="keys", tablefmt="pretty")
            logger_sv.info(f"Результат выведен в консоль в виде таблицы для улучшения читаемости")
            return result
        else:
            logger_sv.info(f"Нет строк содержащих требуемое описание")
            return []

    except FileNotFoundError as e:
        logger_sv.error(f"Файл для чтения не найден. Произошла ошибка {e}")
        return []
    except Exception as e:
        logger_sv.error(f"Возникла ошибка {e}")
        return []


def search_by_phone_number(user_input: str) -> List[Dict]:
    """Функция возвращает список транзакций по номеру телефона"""
    try:
        search_normalized_number = normalize(user_input)
        logger_sv.info(f"Запуск поиска по номеру: {search_normalized_number}")

        pd_excel = pd.read_excel("data/operations.xlsx")
        logger_sv.info(f"Успешно прочитано {len(pd_excel)} строк")

        pattern = re.escape(search_normalized_number)
        mask = pd_excel["Описание"].astype(str).apply(
            lambda x: bool(re.search(pattern, x))
        )
        filtered_transaction = pd_excel[mask]

        if len(filtered_transaction) > 0:
            logger_sv.info(f"Успешно отфильтровано {len(filtered_transaction)} строк")
            json_records = filtered_transaction.to_dict(orient="records")
            result = tabulate(json_records, headers="keys", tablefmt="pretty")
            logger_sv.info(f"Результат выведен в консоль в виде таблицы для улучшения читаемости")
            return result
        else:
            logger_sv.info("Нет строк содержащих требуемое описание")
            return []

    except FileNotFoundError:
        logger_sv.error("Файл data/operations.xlsx не найден")
        return []
    except Exception as e:
        logger_sv.error(f"Ошибка при поиске: {str(e)}")
        return []


def filters_transactions_by_persons(user_input: str) -> List[Dict]:
    try:
        logger_sv.info("Запуск поиска")
        df = pd.read_excel("data/operations.xlsx")


        pattern = re.escape(user_input.title())
        filtered = df[
            (df["Категория"] == "Переводы") &
            (df["Описание"].astype(str).str.contains(pattern, case=False, na=False))
            ]

        if filtered.empty:
            logger_sv.info("Транзакции не найдены")
            return []

        logger_sv.info(f"Найдено {len(filtered)} транзакций")
        json_records = filtered.to_dict(orient="records")
        result = tabulate(json_records, headers="keys", tablefmt="pretty")
        logger_sv.info(f"Результат выведен в консоль в виде таблицы для улучшения читаемости")
        return result

    except FileNotFoundError:
        logger_sv.error("Файл data/operations.xlsx не найден")
        return []
    except Exception as e:
        logger_sv.error(f"Ошибка: {e}")
        return []


