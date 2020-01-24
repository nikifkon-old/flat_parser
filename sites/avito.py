import re
import os
from time import sleep
from concurrent.futures import ProcessPoolExecutor
from selenium import webdriver
from flat_parser.web_parser.parser import Task


class GettingAvitoFlatInfo(Task):
    """ Get list of items urls for parse """
    scroll_sleep_time = 0.4
    load_more_button_label = "Загрузить еще"
    file_path = 'flat_info.json'
    debug_file = "flat_info_debug.log"

    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver_kwargs = {
            'mobile': True
        }
        super().__init__(*args, driver_options=options, driver_kwargs=driver_kwargs, **kwargs)

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
        items = container.find_elements_by_xpath(".//*[@data-marker='item/link']/../..")
        items_text = [item.text for item in items]
        with ProcessPoolExecutor(os.cpu_count()) as executor:
            result = executor.map(self.parse_item, items_text)
        return result

    def parse_item(self, item):
        price_mo = re.compile(r'(?P<price>(\d+ ?)+).руб\.')
        total_area_mo = re.compile(r'(?P<area>\d+(\.)?\d) м²')
        floor_mo = re.compile(r'(?P<floor>\d+)\/(?P<floor_num>\d+) эт.')
        metro_distance_mo = re.compile(r'(?P<distance>\d+(,\d+)?) км')

        price = re.search(price_mo, item).group('price')
        total_area = re.search(total_area_mo, item).group('area')
        floor = re.search(floor_mo, item).group('floor')
        floor_num = re.search(floor_mo, item).group('floor_num')

        metro_distance = None
        metro_distance_match = re.search(metro_distance_mo, item)
        if metro_distance_match is not None:
            metro_distance = metro_distance_match.group('distance')

        address = self.get_address(item)

        row = {
            "price": price,
            "address": address,
            "total_area": total_area,
            "floor": floor,
            "floor_num": floor_num,
            "metro_distance": metro_distance
        }
        return row

    def get_address(self, item):
        street_name = r'((\d{1,3}(\s|-)){0,1}(?!км\b)\b\w+\s?){1,3}'
        street_types = r'(бульвар|б-р|ул|улица|пер|ш|пр-т|nул|пр-кт)\.?'
        house_number = r'\d+\/?(\s?\w?\.?\s?\d?)'
        address_mo = re.compile(r'((%s\s?%s)|(%s\s?%s)),\s?(?P<number>%s)'
                                % (street_types,
                                   street_name,
                                   street_name,
                                   street_types,
                                   house_number))

        address = re.search(address_mo, item)
        if address is None:
            address = item.split('\n')[-2]
            # with open(self.debug_file, 'a', encoding='utf-8') as file:
            #     file.write(f'Error while parsing item(address) is None): '\
            #                f'{repr(item)}\n')
        else:
            address = address.group()
            if '\n' in address:
                address = address.split('\n')[0]
        return address.strip()

    def save_data(self, data):
        return data
        # with open(self.file_path, 'a', encoding='utf-8') as file:
        #     for item in data:
        #         if item is not None:
        #             json.dump(item, file, ensure_ascii=False, indent=4)
        #             file.write(',\n')
