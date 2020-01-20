import pytest
from avito_parser.main import GettingHouseInfo


@pytest.fixture
def prev_data():
    return [
        {'test': 'test', 'url': 'https://domaekb.ru/search?adres=%D0%A5%D1%80%D0%BE%D0%BC%D1%86%D0%BE%D0%B2%D1%81%D0%BA%D0%B0%D1%8F+%D1%83%D0%BB.%2C+1'},
        {'test': 'test', 'url': 'https://domaekb.ru/search?adres=%D1%83%D0%BB.+%D0%9D%D0%B0%D1%87%D0%B4%D0%B8%D0%B2%D0%B0+%D0%9E%D0%BD%D1%83%D1%84%D1%80%D0%B8%D0%B5%D0%B2%D0%B0%2C+8'},
    ]


@pytest.fixture
def urls_cases():
    return {
        "ok": "https://domaekb.ru/search?adres=%D0%A5%D1%80%D0%BE%D0%BC%D1%86%D0%BE%D0%B2%D1%81%D0%BA%D0%B0%D1%8F+%D1%83%D0%BB.%2C+1",
        "many": "https://domaekb.ru/search?adres=%D1%83%D0%BB.+%D0%9D%D0%B0%D1%87%D0%B4%D0%B8%D0%B2%D0%B0+%D0%9E%D0%BD%D1%83%D1%84%D1%80%D0%B8%D0%B5%D0%B2%D0%B0%2C+8",
        "fail": "https://domaekb.ru/search?adres=%D0%A3%D1%80%D0%B0%D0%BB%D0%BC%D0%B0%D1%88%2C+1",
    }


class GettingHouseInfoLog(GettingHouseInfo):
    def save_data(self, data):
        super().save_data(data)
        return data


@pytest.fixture
def create_house_info_task(urls_cases):
    def create_task(case):
        try:
            url = urls_cases[case]
        except KeyError:
            assert False, "Invalid url case"
        name = "test_task"
        return GettingHouseInfoLog(name, url)
    return create_task
