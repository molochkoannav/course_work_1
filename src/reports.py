import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Callable, Any
import pandas as pd

from pathlib import Path

current_file = Path(__file__)
project_root = current_file.parent.parent
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

log_file_rs = log_dir / "reports.log"

logging.getLogger("urllib3").setLevel(logging.WARNING)
logger_rs = logging.getLogger("reports")
logger_rs.setLevel(logging.DEBUG)


file_handler_rs = logging.FileHandler(log_file_rs, mode="w", encoding="utf-8")
file_handler_rs.setLevel(logging.DEBUG)


formatter = logging.Formatter("%(asctime)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler_rs.setFormatter(formatter)


logger_rs.addHandler(file_handler_rs)
logger_rs.propagate = False


def report_decorator(filename: Optional[str] = None):
    """ Декоратор для функций-отчетов, который сохраняет результат в JSON файл """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"report_{timestamp}.json"
            else:
                output_filename = filename
            try:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    if isinstance(result, pd.DataFrame):
                        pretty_result = {
                            "metadata": getattr(result, 'attrs', {}),
                            "data": result.to_dict(orient='records'),
                            "statistics": {
                                "total_rows": len(result),
                                "total_columns": len(result.columns),
                                "columns_list": list(result.columns)
                            }
                        }
                        json.dump(pretty_result, f, ensure_ascii=False, indent=4, default=str)
                    else:
                        json.dump(result, f, ensure_ascii=False, indent=4, default=str)
                logger_rs.info(f"Отчет успешно сохранен в файл: {output_filename}")
            except Exception as e:
                logger_rs.error(f"Ошибка при сохранении отчета: {e}")
                raise

            return result

        return wrapper

    return decorator

@report_decorator()
def spending_by_category(df: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """ Функция для создания отчета о тратах по категории """
    logger_rs.info(f" найдено {len(df)} строк")
    required_columns = ['Дата платежа', 'Категория', 'Сумма операции', 'Номер карты', 'Валюта операции', 'MCC', 'Описание']

    for col in required_columns:
        if col not in df.columns:
            logger_rs.info(f"DataFrame не содержит столбец '{col}")
            raise ValueError(f"DataFrame должен содержать столбец '{col}'")

    df_copy = df.copy()

    if not pd.api.types.is_datetime64_any_dtype(df_copy['Дата платежа']):
        logger_rs.info(f"'Дата платежа' не является типом даты")
        df_copy['Дата платежа'] = pd.to_datetime(df_copy['Дата платежа'], dayfirst=True)

    if date is None:
        target_date = datetime.now()
    else:
        if isinstance(date, str):
            target_date = pd.to_datetime(date, dayfirst=True)
        else:
            target_date = date

    start_date = target_date - timedelta(days=90)

    logger_rs.info(f"Анализ трат по категории '{category}' за период с {start_date.date()} по {target_date.date()}")

    mask = (
            (df_copy['Дата платежа'] >= start_date) &
            (df_copy['Дата платежа'] <= target_date) &
            (df_copy['Категория'] == category)
    )

    filtered_df = df_copy[mask].copy()

    if len(filtered_df) == 0:
        logger_rs.warning(f"Не найдено транзакций по категории '{category}' за указанный период")
        return pd.DataFrame(columns=['Месяц', 'Сумма трат', 'Количество операций'])

    if (filtered_df['Сумма операции'] < 0).any():
        filtered_df['Сумма трат'] = filtered_df['Сумма операции'].abs()
    else:
        filtered_df['Сумма трат'] = filtered_df['Сумма операции']

    filtered_df['Месяц'] = filtered_df['Дата платежа'].dt.to_period('M')

    monthly_report = filtered_df.groupby('Месяц').agg(
        Сумма_трат=('Сумма трат', 'sum'),
        Количество_операций=('Сумма трат', 'count'),
        Средний_чек=('Сумма трат', 'mean')
    ).round(2).reset_index()

    monthly_report['Месяц'] = monthly_report['Месяц'].astype(str)

    total_amount = monthly_report['Сумма_трат'].sum()
    total_operations = monthly_report['Количество_операций'].sum()

    logger_rs.info(
        f"Найдено транзакций: {total_operations}, "
        f"общая сумма: {total_amount:.2f}, "
        f"за {len(monthly_report)} месяцев"
    )

    monthly_report.attrs['Начало периода'] = start_date
    monthly_report.attrs['Конец периода'] = target_date
    monthly_report.attrs['Категория'] = category
    monthly_report.attrs['Общая сумма платежа'] = total_amount

    return monthly_report