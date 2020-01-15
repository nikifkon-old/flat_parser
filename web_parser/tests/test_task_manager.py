from collections.abc import Iterable


def test_create_task(manager, custom_task, task_data):
    task_label = f"{task_data['name']} url: {task_data['url']}"
    task = manager.create_task(custom_task, *task_data.values())

    assert manager.tasks[task_label] == task
    assert task.name == task_data['name']
    assert task.url == task_data['url']

def test_create_tasks(manager, custom_task):
    name = 'test_name'
    urls = ['https://google.com', 'https://gmail.com', 'https://yandex.ru']

    tasks = manager.create_tasks(custom_task, name, urls)

    assert isinstance(tasks, Iterable)
    task_list = [t for t in tasks]
    assert len(task_list) == 3
    for task, url in zip(task_list, urls):
        assert task.url == url
        assert task.name == name
