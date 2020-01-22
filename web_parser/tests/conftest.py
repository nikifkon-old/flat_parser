import pytest
from flat_parser.web_parser.parser import Task, TaskManager


@pytest.fixture
def task_data():
    url = "https://google.com"
    name = "test"
    return {'name': name, 'url': url}

@pytest.fixture
def base_task(task_data):
    return Task(*task_data.values())

class ExampleTask(Task):
    test_data = "test"

    def prepare(self, driver):
        assert driver

    def parse(self, driver):
        assert driver
        return self.test_data

    def save_data(self, data):
        assert data == self.test_data

@pytest.fixture
def custom_task():
    return ExampleTask

@pytest.fixture
def task(custom_task, task_data):
    return custom_task(*task_data.values())

@pytest.fixture
def manager():
    return TaskManager()
