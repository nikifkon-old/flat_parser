from flat_parser.main import get_prev_data


def test_get_prev_data_dont_exist():
    path = 'tests/test_prev_data_dont_exist.csv'
    assert get_prev_data(path) is None


def test_get_prev_data_empty():
    path = 'tests/test_prev_data_empty.csv'
    assert get_prev_data(path) is None


def test_get_prev_data_success():
    path = 'tests/test_prev_data_success.csv'
    assert get_prev_data(path)
