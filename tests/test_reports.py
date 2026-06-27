import json
import os
import tempfile
from datetime import datetime
from datetime import timedelta

import pandas as pd

from src.reports import report_decorator
from src.reports import spending_by_category


def test_spending_by_category_successful_report_generation():
    """Тест успешной генерации отчета"""
    base_date = datetime.now()
    test_data = pd.DataFrame(
        {
            "Дата платежа": [
                base_date - timedelta(days=30),
                base_date - timedelta(days=60),
                base_date - timedelta(days=90),
                base_date - timedelta(days=120),
            ],
            "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты", "Супермаркеты"],
            "Сумма операции": [-1500.50, -2000.00, -1000.00, -500.00],
            "Номер карты": ["1234"] * 4,
            "Валюта операции": ["RUB"] * 4,
            "MCC": [5411] * 4,
            "Описание": ["test"] * 4,
        }
    )

    result = spending_by_category(test_data, "Супермаркеты")

    assert isinstance(result, pd.DataFrame)
    assert "Месяц" in result.columns
    assert "Сумма_трат" in result.columns
    assert "Количество_операций" in result.columns
    assert "Средний_чек" in result.columns
    assert "Начало периода" in result.attrs
    assert "Конец периода" in result.attrs
    assert result.attrs["Категория"] == "Супермаркеты"


def test_spending_by_category_empty_result():
    """Тест для категории без транзакций"""
    base_date = datetime.now()
    test_data = pd.DataFrame(
        {
            "Дата платежа": [base_date],
            "Категория": ["Продукты"],
            "Сумма операции": [-1000],
            "Номер карты": ["1234"],
            "Валюта операции": ["RUB"],
            "MCC": [5411],
            "Описание": ["test"],
        }
    )

    result = spending_by_category(test_data, "Несуществующая категория")

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert len(result.columns) == 3


def test_spending_by_category_with_date_string():
    """Тест с параметром date в виде строки"""
    base_date = datetime.now()
    test_data = pd.DataFrame(
        {
            "Дата платежа": [base_date - timedelta(days=30)],
            "Категория": ["Продукты"],
            "Сумма операции": [-1000],
            "Номер карты": ["1234"],
            "Валюта операции": ["RUB"],
            "MCC": [5411],
            "Описание": ["test"],
        }
    )

    date_str = (datetime.now() - timedelta(days=30)).strftime("%d.%m.%Y")
    result = spending_by_category(test_data, "Продукты", date=date_str)

    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_without_date():
    """Тест без указания даты (используется текущая дата)"""
    base_date = datetime.now()
    test_data = pd.DataFrame(
        {
            "Дата платежа": [base_date - timedelta(days=10)],
            "Категория": ["Супермаркеты"],
            "Сумма операции": [-1000],
            "Номер карты": ["1234"],
            "Валюта операции": ["RUB"],
            "MCC": [5411],
            "Описание": ["test"],
        }
    )

    result = spending_by_category(test_data, "Супермаркеты")

    assert isinstance(result, pd.DataFrame)
    assert not result.empty


def test_spending_by_category_negative_amounts():
    """Тест обработки отрицательных сумм"""
    base_date = datetime.now()
    test_data = pd.DataFrame(
        {
            "Дата платежа": [base_date - timedelta(days=30)],
            "Категория": ["Супермаркеты"],
            "Сумма операции": [-1500.50],
            "Номер карты": ["1234"],
            "Валюта операции": ["RUB"],
            "MCC": [5411],
            "Описание": ["test"],
        }
    )

    result = spending_by_category(test_data, "Супермаркеты")

    assert (result["Сумма_трат"] >= 0).all()
    assert result["Сумма_трат"].iloc[0] == 1500.50


def test_spending_by_category_missing_column():
    """Тест отсутствия обязательного столбца"""
    invalid_df = pd.DataFrame({"Неверный столбец": [1, 2, 3]})

    try:
        spending_by_category(invalid_df, "Продукты")
        assert False, "Должно быть вызвано исключение ValueError"
    except ValueError as e:
        assert "DataFrame должен содержать столбец" in str(e)


def test_spending_by_category_monthly_aggregation():
    """Тест агрегации по месяцам"""
    base_date = datetime.now()
    test_data = pd.DataFrame(
        {
            "Дата платежа": [
                base_date - timedelta(days=10),
                base_date - timedelta(days=20),
                base_date - timedelta(days=50),
                base_date - timedelta(days=80),
            ],
            "Категория": ["Супермаркеты"] * 4,
            "Сумма операции": [-1000, -2000, -3000, -4000],
            "Номер карты": ["1234"] * 4,
            "Валюта операции": ["RUB"] * 4,
            "MCC": [5411] * 4,
            "Описание": ["test"] * 4,
        }
    )

    result = spending_by_category(test_data, "Супермаркеты")

    assert len(result) <= 4
    if not result.empty:
        total_ops = result["Количество_операций"].sum()
        total_amount = result["Сумма_трат"].sum()
        assert total_ops == 4
        assert total_amount == 10000


def test_decorator_without_filename():
    """Тест декоратора"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        try:

            @report_decorator()
            def sample_function():
                return {"test": "data", "value": 123}

            result = sample_function()

            files = os.listdir(temp_dir)
            assert len(files) == 1
            assert files[0].startswith("report_")
            assert files[0].endswith(".json")

            with open(files[0], "r", encoding="utf-8") as f:
                saved_data = json.load(f)

            assert saved_data == {"test": "data", "value": 123}
            assert result == {"test": "data", "value": 123}

        finally:
            os.chdir(original_dir)
