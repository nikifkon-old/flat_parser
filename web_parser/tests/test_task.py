import pytest
from web_parser.parser import Task


def test_taks_init(task_data):
    task1 = Task(*task_data.values())
    assert task1.name == task_data['name']
    assert task1.url == task_data['url']

def test_override_required(base_task):
    with pytest.raises(NotImplementedError):
        base_task.run()

def test_run(task, mocker):
    prepare = mocker.spy(task, 'prepare')
    parse = mocker.spy(task, 'parse')
    save_data = mocker.spy(task, 'save_data')
    task.run()

    prepare.assert_called_once()
    parse.assert_called_once()
    save_data.assert_called_once()

# TODO: test for statuses
