import pytest
from flat_parser.data_modify.utils import get_meter_price


@pytest.mark.parametrize('data, meter_price', [
    ({'total_area': '50.3', 'price': str(4_000_205)}, str(79_526.93837))
])
def test_get_meter_price(data, meter_price):
    assert meter_price == get_meter_price(data)
