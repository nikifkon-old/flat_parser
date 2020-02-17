import pytest
from flat_parser.sites.google_maps import GoogleMapsParser


def test_init():
    pass


def test_create_task():
    pass


def test_create_tasks():
    pass


@pytest.mark.parametrize('prev_data, address', [
    ({'test': '123'}, None),
    (None, None),
    ({}, None),
    ({'address': 'ул. Начдива Онуфриева, 24к2'}, 'ул. Начдива Онуфриева, 24/2'),
    ({'address': 'Июльская 41'}, 'Июльская 41')
])
def test_get_valid_google_address(prev_data, address):
    assert address == GoogleMapsParser._get_valid_google_address(prev_data)


@pytest.mark.parametrize('prev_data, expected_result', [
    ({'address': 'ул. Куйбышева, 63', 'rest': 'test'},
     {'address': 'ул. Куйбышева, 63', 'rest': 'test',
        'post_office_time': '6', 'metro_time': '6'})
])
def test_runs(prev_data, expected_result):
    task = GoogleMapsParser.create_task_from_prev_data(prev_data)
    assert expected_result == task.run()
