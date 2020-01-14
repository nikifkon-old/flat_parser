from collections.abc import Iterable

from web_parser.parser import TaskManager
from web_parser.tests.test_task import ExampleTask


def test_create_task():
    name = 'test_name'
    url = 'https://google.com'
    task_label = f'{name} url: {url}'
    manager = TaskManager()

    task = manager.create_task(ExampleTask, url, name)
    assert manager.tasks[task_label] == task
    assert task.name == name
    assert task.url == url

def test_create_tasks():
    name = 'test_name'
    urls = ['https://google.com', 'https://gmail.com', 'https://yandex.ru']
    manager = TaskManager()

    tasks = manager.create_tasks(ExampleTask, urls, name)

    assert isinstance(tasks, Iterable)
    task_list = [t for t in tasks]
    assert len(task_list) == 3
    for task, url in zip(task_list, urls):
        assert task.url == url
        assert task.name == name
