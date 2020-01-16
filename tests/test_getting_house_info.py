from avito_parser.main import GettingHouseInfo


def test_classmethod():
    prev_data = [
        {'test': 'test', 'url': 'https://google.com'},
        {'test': 'test', 'url': 'https://gmail.com'},
    ]
    tasks = GettingHouseInfo.create_tasks_by_prev_data(prev_data)
    assert len(tasks) == len(prev_data)
