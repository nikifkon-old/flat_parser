import os
from functools import cached_property
from random import choice
from selenium import webdriver


class Driver(webdriver.Chrome):
    def __init__(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.useragent_list_path = os.path.join(current_dir, "mobile_useragents.txt")

        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        options.add_argument("user-agent=%s" % self.get_random_useragent())
        super().__init__(*args, options=options, **kwargs)

    def get_random_useragent(self):
        with open(self.useragent_list_path, 'r') as file:
            ua_list = file.read().splitlines()
            return choice(ua_list)

STATUSES = [
    'pending', 'running', 'successed', 'failed'
]

class Task():
    def __init__(self, name, urls):
        self.name = name
        self.urls = urls
        self._status = "pending"

    @cached_property
    def driver(self):
        return Driver()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new):
        if new in STATUSES:
            self._status = new
        else:
            raise Exception('Status %s is not in allowed statuses. '\
                            'Maybe you mean one of them: [%s]' % (new, ', '.join(STATUSES)))


    def prepare(self, driver):
        """ Abstract method called before `parse` wait for a loading
        """

    def parse(self, driver):
        """ Abstract method received webdriver as once argument,
        and returns data used in `save_data` method """
        raise NotImplementedError('parse method must be overrided')

    def save_data(self, data):
        """ Abstract method received data from `parse` method,
        and saves it in to a file """
        raise NotImplementedError('save_data method must be overrided')

    def run(self):
        for url in self.urls:
            self.driver.get(url)
            self.status = "running"
            try:
                self.prepare(self.driver)
                data = self.parse(self.driver)
                self.save_data(data)
            except Exception as error:
                pass
            finally:
                self.status = "successed" if error is None else "failed"
        self.driver.quit()


    def __repr__(self):
        return "<%s: name=%s, status=%s>" % (self.__class__.__name__, self.name, self.status)


class TaskManager():
    tasks = {}

    def add_task(self, task):
        self.tasks[task.name] = task

    def run_all(self):
        for task in self.tasks.values():
            task.run()

    def run_by_name(self, name):
        if name in self.tasks:
            self.tasks[name].run()
        else:
            raise Exception('Task with name: `%s` does not exist' % name)

    def __repr__(self):
        return "<%s>" % self.__class__.__name__
