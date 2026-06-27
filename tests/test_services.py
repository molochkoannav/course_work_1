import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src.services import filters_transactions_by_persons
from src.services import search_by_phone_number
from src.services import search_by_phrases

sys.path.append(str(Path(__file__).parent.parent))


class TestSearchByPhrases(unittest.TestCase):

    @patch("src.services.pd.read_excel")
    def test_successful_search(self, mock_read_excel):
        """Тест успешного поиска транзакций по фразе."""
        mock_df = pd.DataFrame(
            {"Описание": ["Перевод денег", "Покупка товара", "Перевод на карту"], "Сумма": [100, 200, 300]}
        )
        mock_read_excel.return_value = mock_df

        with patch("src.services.tabulate") as mock_tabulate:
            mock_tabulate.return_value = "Table"
            result = search_by_phrases("перевод")

            self.assertEqual(result, "Table")

    @patch("src.services.pd.read_excel")
    def test_no_results(self, mock_read_excel):
        """Тест поиска фразы, которая не встречается в транзакциях"""
        mock_df = pd.DataFrame({"Описание": ["Покупка товара", "Оплата услуг"], "Сумма": [100, 200]})
        mock_read_excel.return_value = mock_df

        result = search_by_phrases("перевод")

        self.assertEqual(result, [])

    @patch("src.services.pd.read_excel")
    def test_file_not_found(self, mock_read_excel):
        """Тест FileNotFoundError"""
        mock_read_excel.side_effect = FileNotFoundError()

        result = search_by_phrases("перевод")

        self.assertEqual(result, [])

    @patch("src.services.pd.read_excel")
    def test_exception_handling(self, mock_read_excel):
        """Тест обработки исключений"""
        mock_read_excel.side_effect = Exception("Test error")

        result = search_by_phrases("перевод")

        self.assertEqual(result, [])


class TestSearchByPhoneNumber(unittest.TestCase):

    @patch("src.services.pd.read_excel")
    @patch("src.services.normalize")
    def test_successful_search(self, mock_normalize, mock_read_excel):
        """Тест пойска по номеру телефона"""
        mock_normalize.return_value = "79991234567"
        mock_df = pd.DataFrame({"Описание": ["Перевод на номер 79991234567", "Покупка"], "Сумма": [100, 200]})
        mock_read_excel.return_value = mock_df

        with patch("src.services.tabulate") as mock_tabulate:
            mock_tabulate.return_value = "Table"
            result = search_by_phone_number("+7 999 123-45-67")

            self.assertEqual(result, "Table")
            mock_normalize.assert_called_once_with("+7 999 123-45-67")

    @patch("src.services.pd.read_excel")
    @patch("src.services.normalize")
    def test_no_results(self, mock_normalize, mock_read_excel):
        """Тест поиска по номеру телефона, которого нет"""
        mock_normalize.return_value = "79990000000"
        mock_df = pd.DataFrame({"Описание": ["Перевод на номер 79991234567"], "Сумма": [100]})
        mock_read_excel.return_value = mock_df

        result = search_by_phone_number("+7 999 000-00-00")

        self.assertEqual(result, [])

    @patch("src.services.pd.read_excel")
    @patch("src.services.normalize")
    def test_file_not_found(self, mock_normalize, mock_read_excel):
        """Тест с проверкой ошибки чтения файла"""
        mock_normalize.return_value = "79991234567"
        mock_read_excel.side_effect = FileNotFoundError()

        result = search_by_phone_number("+7 999 123-45-67")

        self.assertEqual(result, [])


class TestFiltersTransactionsByPersons(unittest.TestCase):

    @patch("src.services.pd.read_excel")
    def test_successful_filter(self, mock_read_excel):
        """Тест с поиском по категории переводы по имени"""
        mock_df = pd.DataFrame(
            {
                "Категория": ["Переводы", "Переводы", "Покупки"],
                "Описание": ["Перевод Ивану", "Перевод Петру", "Покупка товара"],
                "Сумма": [100, 200, 300],
            }
        )
        mock_read_excel.return_value = mock_df

        with patch("src.services.tabulate") as mock_tabulate:
            mock_tabulate.return_value = "Table"
            result = filters_transactions_by_persons("иван")

            self.assertEqual(result, "Table")

    @patch("src.services.pd.read_excel")
    def test_no_transactions_found(self, mock_read_excel):
        """ТЕст с поиском по категории по имении которого нет"""
        mock_df = pd.DataFrame(
            {
                "Категория": ["Переводы", "Покупки"],
                "Описание": ["Перевод Петру", "Покупка товара"],
                "Сумма": [100, 200],
            }
        )
        mock_read_excel.return_value = mock_df

        result = filters_transactions_by_persons("иван")

        self.assertEqual(result, [])

    @patch("src.services.pd.read_excel")
    def test_wrong_category(self, mock_read_excel):
        """Тест с проверкой не той категории"""
        mock_df = pd.DataFrame(
            {"Категория": ["Покупки", "Платежи"], "Описание": ["Перевод Ивану", "Перевод Петру"], "Сумма": [100, 200]}
        )
        mock_read_excel.return_value = mock_df

        result = filters_transactions_by_persons("иван")

        self.assertEqual(result, [])

    @patch("src.services.pd.read_excel")
    def test_file_not_found(self, mock_read_excel):
        """Тест с проверкой отсутствия файла"""
        mock_read_excel.side_effect = FileNotFoundError()

        result = filters_transactions_by_persons("иван")

        self.assertEqual(result, [])

    @patch("src.services.pd.read_excel")
    def test_exception_handling(self, mock_read_excel):
        """Тест с проверкой ошибки при чтении файла"""
        mock_read_excel.side_effect = Exception("Test error")

        result = filters_transactions_by_persons("иван")

        self.assertEqual(result, [])
