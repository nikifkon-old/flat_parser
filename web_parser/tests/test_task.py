import pytest
from avito_parser.web_parser.parser import Task
from avito_parser.web_parser.tests.conftest import ExampleTask


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


NEW_DATA = {'test': 'test'}


class TaskWithPresaveHook(ExampleTask):
    def presave_hook(self, data):
        return NEW_DATA

    def save_data(self, data):
        assert data == NEW_DATA


def test_presave_hook(task_data, mocker):
    task = TaskWithPresaveHook(*task_data.values())
    task.run()


# TODO: test for statuses
