from flat_parser.web_parser.parser import Task


class GoogleMapsParser(Task):
    """
    A parser that gets time need to reach (by feet or by auto)
    to certain places (to a main post office or neer metro station)
    from https://google.com/maps. And finally, writes the data to csv file
    """
    metro_station_addresses = []
    main_post_office_address = ''

    def __init__(self, *args, prev_data=None, **kwargs):
        valid = self.validate_prev_data(prev_data)
        if valid:
            self.prev_data = prev_data
        else:
            pass
        super().__init__(*args, **kwargs)

    @classmethod
    def create_task_from_prev_data(cls, prev_data, *args, **kwargs):
        name = "google_maps"
        url = "https://google.com/maps"
        return cls(name, url, *args, prev_data=prev_data, **kwargs)

    @classmethod
    def create_tasks_from_prev_data(cls, prev_data, *args, **kwargs):
        for data in prev_data:
            yield cls.create_task_from_prev_data(*args, prev_data=data, **kwargs)

    def validate_prev_data(self, prev_data):
        pass

    def pasrse(self):
        pass

    def save_data(self):
        pass
