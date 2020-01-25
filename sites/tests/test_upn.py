import pytest
from flat_parser.sites.upn import GettingUPNFlatInfo


@pytest.mark.parametrize('data, expected', [
    ({
        'address': 'Екатеринбург, Уктус, Кошевого 32',
        'areas': '23.4 / 16 / 5'
    },
    {
        'address': 'Кошевого 32',
        'total_area': '23.4',
        'kitchen_area': '5'
    })
])
def test_clean_data(data, expected):
    task = GettingUPNFlatInfo("test", "test_url")
    assert task.clean_data(data) == expected
