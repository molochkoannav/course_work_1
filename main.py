from src.services import search_by_phrases, search_by_phone_number, filters_transactions_by_persons
from src.views import main_info

if __name__ == "__main__":
    # print(main_info("2019-01-21 00:03:00"))
    # print(search_by_phrases("Перевод"))
    # print(search_by_phone_number("921112233"))
    # print(search_by_phone_number("79955555555"))
    # print(search_by_phone_number("89813334455"))
    print(filters_transactions_by_persons("Валерий А."))