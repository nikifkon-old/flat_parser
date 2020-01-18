from avito_parser.main import GettingHouseInfo


def check_data(data):
    assert data
    assert data.get('build_year')
    assert data.get('lift_count')
    assert data.get('general_area')
    assert data.get('foundation_type')
    assert data.get('wall_material')
    assert data.get('coating_type')
    assert data.get('house_area')
    assert data.get('basement_area')


def test_classmethod(prev_data):
    tasks = GettingHouseInfo.create_tasks_by_prev_data(prev_data)
    assert len(tasks) == len(prev_data)
    i = 0
    task = tasks[i]
    assert task.prev_data == prev_data[i]


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
