import os
import sys
from unittest.mock import patch
from src.views import main_info
import pandas as pd
from datetime import datetime
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestViews:
    @patch('src.views.get_stocks_info')
    @patch('src.views.get_stocks')
    @patch('src.views.get_currency_rates')
    @patch('src.views.get_read_file')
    @patch('src.views.get_top_five')
    @patch('src.views.get_filtred_info')
    @patch('src.views.get_read_excel_file')
    @patch('src.views.get_date_period')
    @patch('src.views.get_user_time')
    def test_main_info_success(self,
        mock_get_user_time,
        mock_get_date_period,
        mock_get_read_excel_file,
        mock_get_filtred_info,
        mock_get_top_five,
        mock_get_read_file,
        mock_get_currency_rates,
        mock_get_stocks,
        mock_get_stocks_info):
        """Тест успешного выполнения функции main_info"""
        mock_get_user_time.return_value = "Добрый день!"
        mock_get_date_period.return_value = "2021-12-01:2021-12-08"

        mock_excel_data = pd.DataFrame([
                {
                    "Дата операции": datetime(2021, 12, 8, 15, 45),
                    "Дата платежа": datetime(2021, 12, 8, 15, 45),
                    "Номер карты": "*1234",
                    "Статус": "OK",
                    "Сумма операции": -1500.50,
                    "Валюта операции": "RUB",
                    "Сумма платежа": -1500.50,
                    "Валюта платежа": "RUB",
                    "Кешбэк": 0,
                    "Категория": "Супермаркеты",
                    "MCC": 5411,
                    "Описание": "Покупка в магазине",
                    "Бонусы (включая кешбэк)": 30,
                    "Округление на «Инвесткопилку»": 0,
                    "Сумма операции с округлением": 1501.00
                },
                {
                    "Дата операции": datetime(2021, 12, 5, 15, 45),
                    "Дата платежа": datetime(2021, 12, 5, 15, 45),
                    "Номер карты": "*5678",
                    "Статус": "OK",
                    "Сумма операции": -3500.00,
                    "Валюта операции": "RUB",
                    "Сумма платежа": -3500.00,
                    "Валюта платежа": "RUB",
                    "Кешбэк": 0,
                    "Категория": "Электроника",
                    "MCC": 5732,
                    "Описание": "Покупка техники",
                    "Бонусы (включая кешбэк)": 0,
                    "Округление на «Инвесткопилку»": 0.00,
                    "Сумма операции с округлением": 3500.00
                }
        ])
        mock_get_read_excel_file.return_value = mock_excel_data
        mock_get_filtred_info.return_value = [
            {"last_digits": "1234", "total_spent": 1500.50, "cashback": 15.00},
            {"last_digits": "5678", "total_spent": 3500.00, "cashback": 35.00}
        ]
        mock_get_top_five.return_value = [
            {"date": "08.12.2021", "amount": 3500.00, "category": "Электроника",
             "description": "Покупка техники"},
            {"date": "05.12.2021", "amount": 1500.50, "category": "Супермаркеты",
             "description": "Покупка в магазине"}
        ]
        mock_get_read_file.return_value = {
            "currencies": ["USD", "EUR"],
            "stocks": ["AAPL", "GOOGL"]
        }
        mock_get_currency_rates.return_value = {"USD": 50, "EUR": 100}

        mock_get_stocks.return_value = ["AAPL", "GOOGL"]
        mock_get_stocks_info.return_value = {"AAPL": 175.50, "GOOGL": 135.20}

        result = main_info("2021-12-08 15:45:00")
        result_dict = json.loads(result)

        assert result_dict["greetings"] == "Добрый день!"
        assert len(result_dict["cards"]) == 2
        assert len(result_dict["top_transactions"]) == 2
        assert result_dict["currency_rates"]["USD"] == 50
        assert result_dict["stock_prices"]["AAPL"] == 175.50

        mock_get_read_excel_file.assert_called_once()
        mock_get_filtred_info.assert_called_once()
        mock_get_top_five.assert_called_once()

