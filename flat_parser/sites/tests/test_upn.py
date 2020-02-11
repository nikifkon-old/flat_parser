import pytest
from flat_parser.sites.upn import GettingUPNFlatInfo


@pytest.mark.parametrize('data, expected', [
    ({
        'address': 'Екатеринбург, Уктус, Кошевого 32',
        'areas': '23.4 / 16 / 5',
        'floors': ''
    }, {
        'address': 'Кошевого 32',
        'total_area': '23.4',
        'kitchen_area': '5',
    }),
    ({
        'address': 'Екатеринбург, Уктус, Кошевого 32',
        'areas': '23.4 / 16 / 5',
        'price': '123.123',
        'floors': '1 / 5'
    }, {
        'address': 'Кошевого 32',
        'total_area': '23.4',
        'kitchen_area': '5',
        'price': '123123',
        'floor': '1',
        'floor_count': '5'
    })
])
def test_clean_data(data, expected):
    task = GettingUPNFlatInfo("test", "test_url")
    assert task.clean_data(data) == expected


@pytest.mark.parametrize('passed, expected', [
    (2, 2),
    (None, 1)
])
def test_init(passed, expected):
    task = GettingUPNFlatInfo("test", "test", page_count=passed)
    assert task.page_count == expected
