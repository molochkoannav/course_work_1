import re
import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import requests
import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent))

from src.utils import (
    get_user_time,
    get_date_period,
    get_read_excel_file,
    get_filtred_info,
    get_top_five,
    get_read_file,
    get_currency_rates,
    get_stocks,
    get_stocks_info, normalize
)


class TestUtils(unittest.TestCase):
    """Тесты для утилитарных функций"""

    @patch('src.utils.datetime')
    def test_get_user_time_morning(self, mock_datetime):
        """Тест: утро (6:00 - 11:59)"""
        mock_now = MagicMock()
        mock_now.hour = 8
        mock_datetime.now.return_value = mock_now
        result = get_user_time()
        self.assertEqual(result, "Доброе утро")

    @patch('src.utils.datetime')
    def test_get_user_time_afternoon(self, mock_datetime):
        """Тест: день (12:00 - 17:59)"""
        mock_now = MagicMock()
        mock_now.hour = 14
        mock_datetime.now.return_value = mock_now
        result = get_user_time()
        self.assertEqual(result, "Добрый день")

    @patch('src.utils.datetime')
    def test_get_user_time_evening(self, mock_datetime):
        """Тест: вечер (18:00 - 22:59)"""
        mock_now = MagicMock()
        mock_now.hour = 20
        mock_datetime.now.return_value = mock_now
        result = get_user_time()
        self.assertEqual(result, "Добрый вечер")

    @patch('src.utils.datetime')
    def test_get_user_time_night(self, mock_datetime):
        """Тест: ночь (23:00 - 5:59)"""
        mock_now = MagicMock()
        mock_now.hour = 1
        mock_datetime.now.return_value = mock_now
        result = get_user_time()
        self.assertEqual(result, "Доброй ночи")

    def test_get_date_period(self):
        """Тест получения периода от начала месяца до указанной даты"""
        date_time = "2021-12-08 10:30:00"
        result = get_date_period(date_time)

        expected_start = "01.12.2021 10:30:00"
        expected_end = "08.12.2021 10:30:00"

        self.assertEqual(result[0], expected_start)
        self.assertEqual(result[1], expected_end)
        self.assertEqual(len(result), 2)

    def test_get_date_period_different_format(self):
        """Тест получения периода с указанным форматом"""
        date_time = "08.12.2021 10:30:00"
        date_format = "%d.%m.%Y %H:%M:%S"
        result = get_date_period(date_time, date_format)

        self.assertEqual(result[0], "01.12.2021 10:30:00")
        self.assertEqual(result[1], "08.12.2021 10:30:00")

    @patch('pandas.read_excel')
    def test_get_read_excel_file(self, mock_read_excel):
        """ Тест чтения Excel файла и фильтрации его по датам"""
        test_data = pd.DataFrame({
            "Дата операции": ["01.12.2021", "10.12.2021", "20.12.2021", "15.12.2021"],
            "Сумма": [100, 200, 300, 400]
        })
        test_data["Дата операции"] = pd.to_datetime(test_data["Дата операции"], dayfirst=True)

        mock_read_excel.return_value = test_data

        date_period = ["01.12.2021 00:00:00", "15.12.2021 23:59:59"]
        result = get_read_excel_file("test.xlsx", date_period)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)

    @patch('pandas.read_excel')
    def test_get_read_excel_file_empty_result(self, mock_read_excel):
        """Тест чтения Excel файла без данных в указанном периоде"""
        test_data = pd.DataFrame({
            "Дата операции": ["01.01.2021", "02.01.2021"],
            "Сумма": [100, 200]
        })
        test_data["Дата операции"] = pd.to_datetime(test_data["Дата операции"], dayfirst=True)

        mock_read_excel.return_value = test_data

        date_period = ["01.12.2021 00:00:00", "08.12.2021 23:59:59"]
        result = get_read_excel_file("test.xlsx", date_period)

        self.assertEqual(len(result), 0)

    def test_get_filtred_info_no_negative_amounts(self):
        """Тест фильтрации только с отрицательными суммами"""
        test_data = pd.DataFrame({
            "Номер карты": ["1234567890123456", "1234567890123456"],
            "Сумма операции": [100, -200],
            "Описание": ["Пополнение", "Покупка"]
        })

        result = get_filtred_info(test_data)

        self.assertEqual(result[0]["total_spent"], 200.0)

    def test_get_top_five(self):
        """Тест получения топ 5 самых дорогих операций"""
        test_data = pd.DataFrame({
            "Дата платежа": ["2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05", "2024-03-06"],
            "Сумма операции": [-1000, -500, -2000, -50, -3000, -150],
            "Категория": ["Кат1", "Кат2", "Кат3", "Кат4", "Кат5", "Кат6"],
            "Описание": ["Описание1", "Описание2", "Описание3", "Описание4", "Описание5", "Описание6"]
        })

        result = get_top_five(test_data)

        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["amount"], 3000)
        self.assertEqual(result[1]["amount"], 2000)
        self.assertEqual(result[2]["amount"], 1000)
        self.assertEqual(result[3]["amount"], 500)
        self.assertEqual(result[4]["amount"], 150)

    def test_get_top_five_positive_amounts_excluded(self):
        """Тест: положительные суммы исключаются"""
        test_data = pd.DataFrame({
            "Дата платежа": ["2024-03-01", "2024-03-02"],
            "Сумма операции": [1000, -500],
            "Категория": ["Кат1", "Кат2"],
            "Описание": ["Описание1", "Описание2"]
        })

        result = get_top_five(test_data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["amount"], 500)

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_get_read_file_success(self, mock_file):
        """Тест успешного чтения JSON файла"""
        result = get_read_file("test.json")

        self.assertEqual(result, {"key": "value"})
        mock_file.assert_called_once_with("test.json", "r", encoding="utf-8")

    @patch('builtins.open', new_callable=mock_open)
    def test_get_read_file_file_not_found(self, mock_file):
        """Тест: файл не найден"""
        mock_file.side_effect = FileNotFoundError

        result = get_read_file("nonexistent.json")

        self.assertEqual(result, {})

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_get_read_file_invalid_json(self, mock_file):
        """Тест: некорректный JSON"""
        result = get_read_file("invalid.json")

        self.assertEqual(result, {})

    @patch('builtins.open', new_callable=mock_open, read_data='["array"]')
    def test_get_read_file_not_dict(self, mock_file):
        """Тест: JSON не является словарем"""
        result = get_read_file("array.json")

        self.assertEqual(result, {})

    @patch('requests.get')
    def test_get_currency_rates_success(self, mock_get):
        """Тест успешного получения курсов валют"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Valute": {
                "USD": {"Value": 50},
                "EUR": {"Value": 100}
            }
        }
        mock_get.return_value = mock_response

        data = {"user_currencies": ["USD", "EUR"]}
        result = get_currency_rates(data)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["currency"], "USD")
        self.assertEqual(result[0]["rate"], 50)
        self.assertEqual(result[1]["currency"], "EUR")
        self.assertEqual(result[1]["rate"], 100)

    @patch('requests.get')
    def test_get_currency_rates_request_error(self, mock_get):
        """Тест ошибки при запросе курсов валют"""
        mock_get.side_effect = requests.RequestException("Network error")

        data = {"user_currencies": ["USD", "EUR"]}
        result = get_currency_rates(data)

        self.assertEqual(result, [])

    def test_get_currency_rates_missing_currencies(self):
        """Тест: отсутствуют валюты в данных"""
        data = {"user_currencies": []}
        result = get_currency_rates(data)

        self.assertEqual(result, [])

    def test_get_currency_rates_insufficient_currencies(self):
        """Тест: недостаточно валют"""
        data = {"user_currencies": ["USD"]}
        result = get_currency_rates(data)

        self.assertEqual(result, [])

    def test_get_stocks_string_input(self):
        """Тест получения тикеров из строки"""
        data = {"user_stocks": "AAPL, GOOGL, MSFT"}
        result = get_stocks(data)

        self.assertEqual(result, ["AAPL", "GOOGL", "MSFT"])

    def test_get_stocks_list_input(self):
        """Тест получения тикеров из списка"""
        data = {"user_stocks": ["AAPL", "GOOGL", "MSFT"]}
        result = get_stocks(data)

        self.assertEqual(result, ["AAPL", "GOOGL", "MSFT"])

    def test_get_stocks_empty(self):
        """Тест: пустой список тикеров"""
        data = {"user_stocks": []}
        result = get_stocks(data)

        self.assertEqual(result, [])

    def test_get_stocks_missing_key(self):
        """Тест: отсутствует ключ user_stocks"""
        data = {}
        result = get_stocks(data)

        self.assertEqual(result, [])

    @patch('requests.get')
    def test_get_stocks_info_success(self, mock_get):
        """Тест успешного получения информации об акциях"""
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {"price": "150.50"}

        mock_response2 = MagicMock()
        mock_response2.json.return_value = {"price": "250.75"}

        mock_get.side_effect = [mock_response1, mock_response2]

        stocks = ["AAPL", "GOOGL"]
        result = get_stocks_info(stocks)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["stock"], "AAPL")
        self.assertEqual(result[0]["price"], 150.50)
        self.assertEqual(result[1]["stock"], "GOOGL")
        self.assertEqual(result[1]["price"], 250.75)

    @patch('requests.get')
    def test_get_stocks_info_request_error(self, mock_get):
        """Тест ошибки при запросе информации об акциях"""
        mock_get.side_effect = requests.RequestException("Network error")

        stocks = ["AAPL"]
        result = get_stocks_info(stocks)

        self.assertEqual(result, [])

    @patch('requests.get')
    def test_get_stocks_info_key_error(self, mock_get):
        """Тест отсутствия ключа price в ответе"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "Invalid symbol"}
        mock_get.return_value = mock_response

        stocks = ["INVALID"]
        result = get_stocks_info(stocks)

        self.assertEqual(result, [])

    @patch('requests.get')
    def test_get_stocks_info_empty_list(self, mock_get):
        """Тест с пустым списком акций"""
        result = get_stocks_info([])

        self.assertEqual(result, [])
        mock_get.assert_not_called()


class TestNormalize:

    @pytest.mark.parametrize("input_str,expected", [
        ("921112233", "+7 921 11-22-33"),
        ("79955555555", "+7 995 555-55-5"),
        ("89813334455", "+7 981 333-44-55"),
    ])
    def test_normalize_phone_numbers(self, input_str, expected):
        """Тест проверяет преобразование номеров телефонов"""
        assert normalize(input_str) == expected

    @pytest.mark.parametrize("input_str,expected_length", [
        ("921112233", 15),
        ("79955555555", 15),
        ("89813334455", 16),
    ])
    def test_normalize_output_length(self, input_str, expected_length):
        """Тест проверяет длину выходной строки"""
        result = normalize(input_str)
        assert len(result) == expected_length

    @pytest.mark.parametrize("input_str", [
        "921112233",
        "79955555555",
        "89813334455",
    ])
    def test_normalize_returns_string(self, input_str):
        """Тест проверяет что функция возвращает строку"""
        result = normalize(input_str)
        assert isinstance(result, str)

