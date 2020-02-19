import pytest
from flat_parser.sites.upn import GettingUPNFlatInfo


@pytest.mark.parametrize('tr_text, expected', [
    (
        ['УПН', '1 комната в 1 кв.', 'Екатеринбург, Кольцово, Авиаторов 11',
         '11 / 11 / -', '1 / 3', '490.000', 'МС', '1962', 'Кирпич', 'Чистая продажа', ''],
        {
            'address': 'Авиаторов 11',
            'total_area': 11,
            'kitchen_area': 0,
            'floor': 1,
            'floor_count': 3,
            'price': 490000
        }),
    (
        ['УПН', '1 комната в 4 кв.', 'Екатеринбург, Уктус, Шишимская 17', '- / 7.9 / -',
         '- / 5', '495.000', 'БР', '1978', 'Панель', 'Чистая продажа', ''],
        {
            'address': 'Шишимская 17',
            'total_area': 0,
            'kitchen_area': 0,
            'floor': None,
            'floor_count': 5,
            'price': 495000
        }),
    (
        ['УПН', '1 комната в 4 кв.', 'Екатеринбург, Уктус, Шишимская 17',
         '- / 7.9 / -', '-', '495.000', 'БР', '1978', 'Панель', 'Чистая продажа', ''],
        {
            'address': 'Шишимская 17',
            'total_area': 0,
            'kitchen_area': 0,
            'floor': None,
            'floor_count': None,
            'price': 495000
        }),
    (
        ['', '1 комната в 20 кв.', '', '58 / 7.9 / -', '4 / 5',
         '495.000', 'БР', '1978', 'Панель', 'Чистая продажа', ''],
        None),
    (
        ['УПН', '1 комната в 4 кв.', 'Екатеринбург, Уктус, Шишимская 17',
         '- / 7.9 / -', '-', '-', 'БР', '1978', 'Панель', 'Чистая продажа', ''],
        None
    )
])
def test_clean_data(tr_text, expected):
    task = GettingUPNFlatInfo("test", "test_url")
    data = task.tr_namedturple(*tr_text)._asdict()
    assert task.clean_data(data) == expected


@pytest.mark.parametrize('passed, expected', [
    (2, 2),
    (None, 1)
])
def test_init(passed, expected):
    task = GettingUPNFlatInfo("test", "test", page_count=passed)
    assert task.page_count == expected
