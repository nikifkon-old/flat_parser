from collections.abc import Iterable

import pytest
from flat_parser.web_parser.parser import Task
from flat_parser.web_parser.tests.conftest import ExampleTask


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


def test_create_tasks(custom_task_class):
    prev_data = [{'address': 'test'}, {}]
    tasks = custom_task_class.create_tasks_with_prev_data('test_name', 'test_url',
                                                          prev_data=prev_data)
    assert isinstance(tasks, Iterable)
    assert all(isinstance(task, custom_task_class) for task in tasks)


class TaskWithPresaveHook(ExampleTask):
    def presave_hook(self, data):
        return {'test': 'test'}

    def save_data(self, data):
        assert data == {'test': 'test'}


def test_presave_hook(task_data):
    task = TaskWithPresaveHook(*task_data.values())
    task.run()
