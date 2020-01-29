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


def test_create_task_from_address():
    prev_data = {
        'test': 'test',
        'address': 'пр Академика Сахарова , 2'
    }

    task = GettingHouseInfoLog.create_task_from_address(prev_data)
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
    tasks = GettingHouseInfoLog.create_tasks_from_addresses(prev_datas)
    assert tasks
    assert isinstance(tasks, Iterator)
    assert len(list(tasks)) == 2


@pytest.mark.parametrize('address, expected', [
    ('Первомайская улица., 79', 'Первомайская ул., 79'),
    ('ул. Начдива Онуфриева, 24к2', 'ул. Начдива Онуфриева, 24/2'),
    ('проспект Академика Сахарова , 2', 'пр-кт Академика Сахарова , 2'),
    ('пр-т Академика Сахарова , 2', 'пр-кт Академика Сахарова , 2'),
    ('пр Академика Сахарова , 2', 'пр-кт Академика Сахарова , 2'),
    ('Россия, Екатеринбург, Бессарабская ул, 10А', 'Бессарабская ул, 10А'),
    ('Екатеринбург, Россия Байкальская ул, 35', 'Байкальская ул, 35'),
    ('Екатеринбург, Водоемная ул, 80 корпус 3', 'Водоемная ул, 80/3'),
    ('Аппаратная станция 6', 'Аппаратная 6'),
    ('Россия, Свердловская область, городской округ Екатеринбург, Екатеринбург, улица Данилы Зверева, 7в', 'ул Данилы Зверева, 7в'),
    ('Базовый переулок, 50', 'Базовый пер., 50'),
    ('ул Начдива Онуфриева, 32 ст1', 'ул Начдива Онуфриева, 32/1'),
    ('Россия, Свердловская область, Екатеринбург, Екатеринбург, ул. Краснолесье, 149, Свердловская обл., Россия', 'ул. Краснолесье, 149'),
    ('Екатеринбург, 139 улица Луначарского', '139 ул Луначарского'),
    ('ул Бажова, д103', 'ул Бажова, 103'),
    (None, None),
    ('', '')
])
def test_get_normalize_address(create_house_info_task, address, expected):
    task = create_house_info_task("ok")
    assert expected == task.get_normalize_address(address)


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
