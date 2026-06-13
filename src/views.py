import json
from typing import Any
from typing import Dict
from src.utils import get_date_period, get_filtred_info, get_top_five, get_read_file, get_currency_rates, get_stocks, get_stocks_info
from src.utils import get_read_excel_file
from src.utils import get_user_time
from config import EXCEL_FILE_PATH,JSON_SETTINGS_PATH
import logging
from pathlib import Path

current_file = Path(__file__)
project_root = current_file.parent.parent
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

log_file_vs = log_dir / "views.log"

logging.getLogger("urllib3").setLevel(logging.WARNING)
logger_vs = logging.getLogger("views")
logger_vs.setLevel(logging.DEBUG)


file_handler_vs = logging.FileHandler(log_file_vs, mode="w", encoding="utf-8")
file_handler_vs.setLevel(logging.DEBUG)


formatter = logging.Formatter("%(asctime)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler_vs.setFormatter(formatter)


logger_vs.addHandler(file_handler_vs)
logger_vs.propagate = False


def main_info(date_time: str)-> Dict[str, Any]:
    """Главная функция, принимающая на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращающая JSON-ответ"""
    logger_vs.info("Запуск функции main_info")
    greetings = get_user_time()
    date_period = get_date_period(date_time)
    sort_by_date_transactions = get_read_excel_file(EXCEL_FILE_PATH,date_period)
    filter_cards_info = get_filtred_info(sort_by_date_transactions)
    filter_top_transactions = get_top_five(sort_by_date_transactions)
    currency_read = get_read_file(JSON_SETTINGS_PATH)
    currency_rates = get_currency_rates(currency_read)
    stock_data = get_stocks(currency_read)
    stock_prices = get_stocks_info(stock_data)
    logger_vs.info("Функция отработала")
    data_info = {"greetings": greetings,
                 "cards": filter_cards_info,
                 "top_transactions": filter_top_transactions,
                 "currency_rates": currency_rates,
                 "stock_prices": stock_prices}
    json_data_info = json.dumps(data_info, ensure_ascii=False, indent=4)
    return json_data_info


