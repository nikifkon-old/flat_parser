from collections.abc import Iterator
import pytest
from flat_parser.sites.tests.conftest import GettingHouseInfoLog
from flat_parser.sites.domaekb import HOUSE_INFO_URL


def check_data(data):
    assert data
    assert data.get('build_year')
    assert 0 <= data.get('build_year') < 300
    assert data.get('lift_count')
    assert data.get('public_area')
    assert data.get('foundation_type')
    assert data.get('house_type')
    assert data.get('coating_type')
    assert data.get('house_area')
    assert data.get('playground')
    assert data.get('sport_ground')
    data['land_area']
    assert data.get('porch_count')
    assert data.get('people_count')
    assert data.get('url') is None


def test_classmethod(prev_data):
    tasks = GettingHouseInfoLog.create_tasks_by_prev_data(prev_data)
    assert len(tasks) == len(prev_data)
    i = 0
    task = tasks[i]
    assert task.prev_data == prev_data[i]

    data = task.run()
    task.prev_data.pop('url')
    assert set(task.prev_data).issubset(set(data))


def test_create_task_from_address():
    address = 'пр Академика Сахарова , 2'
    task = GettingHouseInfoLog.create_task_from_address(address)
    assert task
    assert HOUSE_INFO_URL in task.url


def test_create_tasks_from_addresses():
    addresses = ['пр Академика Сахарова , 2', 'пр Академика Сахарова , 2']
    tasks = GettingHouseInfoLog.create_tasks_from_addresses(addresses)
    assert tasks
    assert isinstance(tasks, Iterator)
    assert len(list(tasks)) == len(addresses)


@pytest.mark.parametrize('address, expected', [
    ('Первомайская улица., 79', 'Первомайская ул., 79'),
    ('ул. Начдива Онуфриева, 24к2', 'ул. Начдива Онуфриева, 24/2'),
    ('проспект Академика Сахарова , 2', 'пр-кт Академика Сахарова , 2'),
    ('пр-т Академика Сахарова , 2', 'пр-кт Академика Сахарова , 2'),
    ('пр Академика Сахарова , 2', 'пр-кт Академика Сахарова , 2')
])
def test_get_searchable_address(create_house_info_task, address, expected):
    task = create_house_info_task("ok")
    assert expected == task.get_searchable_address(address)


def test_ok(create_house_info_task):
    task = create_house_info_task("ok")
    data = task.run()
    task.status == "successed"
    check_data(data)


def test_many(create_house_info_task):
    task = create_house_info_task("many")
    data = task.run()
    task.status == "successed"
    check_data(data)


def test_fail(create_house_info_task):
    task = create_house_info_task("fail")
    task.run()
    assert task.status == 'failed'
