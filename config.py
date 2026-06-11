from pathlib import Path
from typing import Any

# Базовые пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Пути к файлам
EXCEL_FILE_PATH = str(DATA_DIR / "operations.xlsx")
JSON_SETTINGS_PATH = str(DATA_DIR / "user_settings.json")
