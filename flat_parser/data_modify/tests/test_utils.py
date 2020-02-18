import pytest
from flat_parser.data_modify.utils import (
    get_meter_price, get_time_in_minutes_by_text
)


@pytest.mark.parametrize('data, meter_price', [
    ({'total_area': '50.3', 'price': str(4_000_205)}, str(79_526.93837))
])
def test_get_meter_price(data, meter_price):
    assert meter_price == get_meter_price(data)


@pytest.mark.parametrize('text, time', [
    ('', 0),
    (None, None),
    ('45 мин.', 45),
    ('1 ч. 20 мин.', 80),
    ('2 ч.', 120),
    ('1 д.', 1440),
    ('2 д. 2 ч. 10 мин.', 3010)
])
def test_get_time_in_minutes_by_text(text, time):
    assert time == get_time_in_minutes_by_text(text)
