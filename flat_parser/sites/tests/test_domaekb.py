from collections.abc import Iterator
import pytest
from flat_parser.sites.tests.conftest import DomaekbParserLog
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
    data.get('land_area')
    assert data.get('porch_count')
    assert data.get('people_count')
    assert data.get('url') is None


def test_create_task_from_address():
    prev_data = {
        'test': 'test',
        'address': 'пр Академика Сахарова , 2'
    }

    task = DomaekbParserLog.create_task_from_address(prev_data)
    assert task
    assert HOUSE_INFO_URL in task.url


def test_create_tasks_from_addresses():
    prev_datas = [{
            'test': 'test',
            'address': 'пр Академика Сахарова , 2'
        },
        {
            'test': 'test',
            'address': 'пр Академика Сахарова , 2'
        },
        None
    ]
    tasks = DomaekbParserLog.create_tasks_from_addresses(prev_datas)
    assert tasks
    assert isinstance(tasks, Iterator)
    assert len(list(tasks)) == 2


def test_ok(create_house_info_task):
    task = create_house_info_task("ok")
    data = task.run()
    assert task.status == "successed"
    check_data(data)


def test_many(create_house_info_task):
    task = create_house_info_task("many")
    data = task.run()
    assert task.status == "successed"
    check_data(data)


def test_fail(create_house_info_task):
    task = create_house_info_task("fail")
    task.run()
    assert task.status == 'failed'
