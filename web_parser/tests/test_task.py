import pytest
from web_parser.parser import Task


def test_taks_init():
    url = "https://google.com"
    name = "test"
    task = Task(name, url)
    assert task.name == name
    assert task.url == url

def test_override_required():
    url = "https://google.com"
    name = "test"
    task = Task(name, url)
    with pytest.raises(NotImplementedError):
        task.run()

TEST_DATA = "test"

class ExampleTask(Task):
    def prepare(self, driver):
        assert driver

    def parse(self, driver):
        assert driver
        return TEST_DATA

    def save_data(self, data):
        assert data == TEST_DATA


def test_run(mocker):
    url = "https://google.com"
    name = "test"
    task = ExampleTask(name, url)
    prepare = mocker.spy(task, 'prepare')
    parse = mocker.spy(task, 'parse')
    save_data = mocker.spy(task, 'save_data')
    task.run()

    prepare.assert_called_once()
    parse.assert_called_once()
    save_data.assert_called_once()

# TODO: test for statuses
