class Parser:
    headers = None

    def __init__(self, url):
        self.url = url

    def get_html(self):
        pass

    def parse_html(self):
        pass


class Task(Parser):
    status = "" # pending, running, successed, failed

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def parse(self, bs):
        """ Abstract method received html as once argument,
        and returns data used in `save_data` method """
        pass

    def save_data(self, data):
        """ Abstract method received data from `parse` method,
        and saves it in to a file """
        pass
    
    def run(self):
        pass


class TaskManager():
    pending_tasks = []
    running_tasks = []
    finished_tasks = []

    def add_task(self, task):
        pass

    def run_all(self):
        pass

    def run_by_name(self, name):
        pass
