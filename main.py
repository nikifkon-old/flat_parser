import re
import os
import json
from time import sleep, time
from concurrent.futures import ProcessPoolExecutor
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from web_parser.parser import Task, TaskManager

URL = "https://m.avito.ru/ekaterinburg/kvartiry/prodam/vtorichka"


class GettingFlatInfo(Task):
    """ Get list of items urls for parse """
    scroll_sleep_time = 0.4
    load_more_button_label = "Загрузить еще"
    file_path = 'flat_info.json'
    debug_file = "flat_info_debug.log"

    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options, **kwargs)

    def prepare(self, driver):
        last = driver.execute_script("return document.body.scrollHeight")
        new = None
        load_more_button = None
        while last != new or load_more_button:
            try:
                load_more_button = driver.find_element_by_xpath("//div[.='%s']//span"
                                                                % self.load_more_button_label)
                load_more_button.click()
            except NoSuchElementException:
                load_more_button = None
            last = new
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(self.scroll_sleep_time)
            new = driver.execute_script("return document.body.scrollHeight")

    def parse(self, driver):
        result = []
        container = driver.find_element_by_xpath(".//*[@data-marker='items/list']")
        items = container.find_elements_by_xpath(".//*[@data-marker='item/link']")
        items_text = [item.text for item in items]
        with ProcessPoolExecutor(os.cpu_count()) as executor:
            result = executor.map(self.parse_item, items_text)
        return list(result)

    def parse_item(self, item):
        price_mo = re.compile(r'(\d+ )+руб.')
        total_area_mo = re.compile(r'\d+(\.)?\d м²')
        floor_mo = re.compile(r'(?P<floor>\d+)\/\d+ эт.')

        street_name = r'((\d{1,3}(\s|-)){0,1}\w+\s?){1,3}'
        street_types = r'(бульвар|б-р|ул|улица|пер|ш|пр-т|nул|пр-кт)\.?'
        address_mo = re.compile(r'((%s\s?%s)|(%s\s?%s)), \d+\w?'
                                % (street_types, street_name, street_name, street_types))

        price = re.search(price_mo, item).group()
        total_area = re.search(total_area_mo, item).group()
        floor = re.search(floor_mo, item).group('floor')

        address = re.search(address_mo, item)
        if address is None:
            address = item.split('\n')[-2]
            with open(self.debug_file, 'a', encoding='utf-8') as file:
                file.write(f'Error while parsing item(address) is None): '\
                           f'{repr(item)}\n')
        else:
            address = address.group()

        row = {
            "price": price,
            "address": address,
            "total_area": total_area,
            "floor": floor
        }
        return row

    def save_data(self, data):
        with open(self.file_path, 'a', encoding='utf-8') as file:
            for item in data:
                if item is not None:
                    json.dump(item, file, ensure_ascii=False, indent=4)
                    file.write(',\n')

    def get_links(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read().split('\n')
        except FileNotFoundError:
            print('File with parse result dont found: %s' % self.file_path)
            return list()


def main():
    start_time = time()
    manager = TaskManager()
    getting_links_task = GettingFlatInfo("get_flat_info", [URL])
    manager.add_task(getting_links_task)

    manager.run_by_name("get_flat_info")

    print(f"Time: {round(time() - start_time, 2)} sec.")


if __name__ == '__main__':
    main()
