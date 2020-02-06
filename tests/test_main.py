from flat_parser.main import get_prev_data


def test_get_prev_data_dont_exist():
    path = 'tests/test_prev_data_dont_exist.csv'
    data = get_prev_data(path)
    assert data is None


def test_get_prev_data_empty():
    path = 'tests/test_prev_data_empty.csv'
    data = get_prev_data(path)
    assert data == []


def test_get_prev_data_success():
    expected = [
        {'price': '3700000', 'address': 'Екатеринбург, 62/2 улица Уральская', 'floor': '4'},
        {'price': '3700001', 'address': 'Екатеринбург, 62/22 улица Уральская', 'floor': '5'},
    ]
    path = 'tests/test_prev_data_success.csv'
    data = get_prev_data(path)
    assert data is not None
    assert data == expected
