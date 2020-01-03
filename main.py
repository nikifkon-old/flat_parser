from web_parser.parser import Task, TaskManager

URL = ""


class GettingPageUrlList(Task):
    def parse(self, bs):
        pass

    def save_data(self, data):
        pass


def main():
    tm = TaskManager()
    t1 = GettingPageUrlList("get_urls", URL)
    tm.add_task(t1)

    tm.run_all()

if __name__ == '__main__':
    main()
