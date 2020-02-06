import os
import csv
import signal
from random import choice
from selenium import webdriver


def pool_initializer():
    """Ignore CTRL+C in the worker process."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class StopTaskException(Exception):
    pass


class Driver(webdriver.Chrome):
    def __init__(self, *args, mobile=False, options=None, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.useragent_list_path = os.path.join(current_dir, "mobile_useragents.txt")

        if options is None:
            options = webdriver.ChromeOptions()
        if mobile:
            options.add_argument("user-agent=%s" % self.get_random_useragent())
        options.add_argument('log-level=3')
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
    data = None

    def __init__(self, name, url, driver_kwargs=None, driver_options=None):
        self.name = name
        self.url = url
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

    def presave_hook(self, data):
        """ Hook for modify parsed data """
        return data

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

    def save_list_to_csv(self, data):
        for row in data:
            self.save_data_to_csv(row)

    def save_data_to_csv(self, data):
        self.data = data
        need_header = False
        if not os.path.exists(self.output_file):
            need_header = True
        with open(self.output_file, 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            if need_header:
                writer.writerow(data.keys())
            writer.writerow(data.values())

    def run(self):
        self.status = "running"
        driver, _ = self.open_driver()
        driver.get(self.url)
        try:
            self.prepare(driver)
            data = self.parse(driver)
            full_data = self.presave_hook(data)
            returned_data = self.save_data(full_data)
            self.status = "successed"
            return returned_data
        except StopTaskException:
            self.status = "failed"
        finally:
            print(f"{repr(self)} finished")
            self.close_driver(driver)

    def __repr__(self):
        return "<%s: name=%s, url=%s, status=%s>" % (
            self.__class__.__name__, self.name, self.url, self.status)


class TaskManager():
    tasks = {}

    def create_task(self, task_class, name, url, *args, **kwargs):
        task_label = f'{name} url: {url}'
        task = task_class(name, url, *args, **kwargs)
        self.tasks[task_label] = task
        return task

    def create_tasks(self, task_class, name, urls, *args, **kwargs):
        for url in urls:
            task = self.create_task(task_class, name, url, *args, **kwargs)
            yield task

    def __repr__(self):
        return "<%s>" % self.__class__.__name__
