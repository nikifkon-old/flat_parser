import os
import signal
from random import choice
from multiprocessing import Pool
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def pool_initializer():
    """Ignore CTRL+C in the worker process."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class Driver(webdriver.Chrome):
    def __init__(self, *args, options=None, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.useragent_list_path = os.path.join(current_dir, "mobile_useragents.txt")

        if options is None:
            options = webdriver.ChromeOptions()
        options.add_argument("user-agent=%s" % self.get_random_useragent())
        super().__init__(*args, options=options, **kwargs)

    def get_random_useragent(self):
        with open(self.useragent_list_path, 'r') as file:
            ua_list = file.read().splitlines()
            return choice(ua_list)


class Task():
    _drivers = {}
    statuses = [
        'pending', 'running', 'successed', 'failed'
    ]

    def __init__(self, name, urls, driver_kwargs=None, driver_options=None):
        self.name = name
        self.urls = urls
        self._status = "pending"

        if driver_kwargs is not None:
            self._driver_kwargs = driver_kwargs
        else:
            self._driver_kwargs = {}
        self._driver_options = driver_options

    def init_driver(self):
        return Driver(options=self._driver_options, **self._driver_kwargs)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new):
        if new in self.statuses:
            self._status = new
        else:
            raise Exception('Status %s is not in allowed statuses. '\
                            'Maybe you mean one of them: [%s]' % (new, ', '.join(self.statuses)))

    def open_driver(self):
        driver = self.init_driver()
        id_ = driver.session_id
        self._drivers[id_] = driver
        return driver, id_

    def close_driver(self, driver):
        driver.quit()
        id_ = driver.session_id
        del self._drivers[id_]

    def close_all(self):
        for driver in self._drivers.values():
            driver.quit()
            del driver

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
        self.status = "running"
        with Pool(os.cpu_count(), initializer=pool_initializer) as pool:
            try:
                pool.map(self.get_data, self.urls)
            except KeyboardInterrupt:
                pool.terminate()
                pool.join()
                self.close_all()

    def get_data(self, url):
        driver, _ = self.open_driver()
        driver.get(url)
        try:
            self.prepare(driver)
            data = self.parse(driver)
            self.save_data(data)
        except WebDriverException as exc:
            self.status = "failed"
            print(exc)
        finally:
            self.close_driver(driver)


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
