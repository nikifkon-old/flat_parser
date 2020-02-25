import pytest
from flat_parser.sites.google_maps import GoogleMapsParser


def test_init():
    task = GoogleMapsParser('test_name', 'test_url',
                            output_file='test_output.csv', prev_data={})
    assert task.name == 'test_name'
    assert task.url == 'test_url'
    assert task.output_file == 'test_output.csv'
    assert task.prev_data == {}
    assert task.address is None
    assert not task._refreshed


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
      'post_office_time': '17', 'metro_time': '6'})
])
def test_runs(prev_data, expected_result):
    task = GoogleMapsParser('test_name', 'https://google.com/maps',
                            prev_data=prev_data, output_file="data/test.csv")
    assert expected_result == task.run()
