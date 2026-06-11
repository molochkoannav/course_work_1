import json
import logging
from typing import Any
from typing import Dict


from src.utils import get_date_period, get_filtred_info, get_top_five, get_read_file, get_currency_rates, get_stocks, get_stocks_info
from src.utils import get_read_excel_file
from src.utils import get_user_time


def main_info(date_time: str)-> Dict[str, Any]:
    """Главная функция, принимающая на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращающая JSON-ответ"""
    greetings = get_user_time()
    date_period = get_date_period(date_time)
    file_path = "data/operations.xlsx"
    file_path_json = "data/user_settings.json"
    sort_by_date_transactions = get_read_excel_file(file_path,date_period)
    filter_cards_info = get_filtred_info(sort_by_date_transactions)
    filter_top_transactions = get_top_five(sort_by_date_transactions)
    currency_read = get_read_file(file_path_json)
    currency_rates = get_currency_rates(currency_read)
    stock_data = get_stocks(currency_read)
    stock_prices = get_stocks_info(stock_data)
    data_info = {"greetings": greetings,
                 "cards": filter_cards_info,
                 "top_transactions": filter_top_transactions,
                 "currency_rates": currency_rates,
                 "stock_prices": stock_prices}
    json_data_info = json.dumps(data_info, ensure_ascii=False, indent=4)
    return json_data_info


