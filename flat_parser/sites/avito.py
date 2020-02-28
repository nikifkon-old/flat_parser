import os
import re
from concurrent.futures import ProcessPoolExecutor
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from flat_parser.utils.data import get_meter_price
from flat_parser.web_parser.parser import Task
from flat_parser.utils.log import setup_logging


class AvitoParser(Task):
    """ Get list of items urls for parse """
    scroll_sleep_time = 0.5

    def __init__(self, *args, scroll_count=None, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver_kwargs = {
            'mobile': True
        }
        self.scroll_count = scroll_count or 1
        super().__init__(*args, driver_options=options,
                         driver_kwargs=driver_kwargs, **kwargs)

    def prepare(self, driver):
        last = driver.execute_script("return document.body.scrollHeight")
        new = None
        load_more_button = None
        count = 0
        load_more_button_label = "Загрузить еще"

        while (last != new or load_more_button) and count < self.scroll_count:
            try:
                load_more_button = driver.find_element_by_xpath(
                    f"//div[.='{load_more_button_label}']//span")
                load_more_button.click()
            except NoSuchElementException:
                load_more_button = None
            last = new
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight)")
            sleep(self.scroll_sleep_time)
            new = driver.execute_script("return document.body.scrollHeight")
            count += 1

    def parse(self, driver):
        container = driver.find_element_by_xpath(
            ".//*[@data-marker='items/list']")
        items = container.find_elements_by_xpath(
            ".//*[@data-marker='item/link']/../..")
        args = []
        for item in items:
            url = item.find_element_by_xpath(".//a").get_attribute('href')
            args.append((item.text, url))
        return self.run_multi_proccess(self.parse_item, args)

    def run_multi_proccess(self, func, args):
        result = []
        with ProcessPoolExecutor(os.cpu_count()) as executor:
            setup_logging()
            result = executor.map(func, args)
        return result

    def parse_item(self, args):
        string, url = args
        row = self.parse_string(string)
        row["link"] = url
        row["meter_price"] = get_meter_price(row)
        return row

    def parse_string(self, string):
        price_mo = re.compile(r'(?P<price>(\d+ ?)+).₽')
        total_area_mo = re.compile(r'(?P<area>\d+(\.)?\d) м²')
        floor_mo = re.compile(r'(?P<floor>\d+)\/(?P<floor_num>\d+) эт.')

        price = re.search(price_mo, string)
        if price is not None:
            price = price.group('price')
            price = price.replace(' ', '')
        total_area = re.search(total_area_mo, string)
        if total_area is not None:
            total_area = total_area.group('area')
        floor = re.search(floor_mo, string)
        if floor is not None:
            floor = floor.group('floor')
        floor_num = re.search(floor_mo, string)
        if floor_num is not None:
            floor_num = floor_num.group('floor_num')

        row = {
            "price": price,
            "total_area": total_area,
            "floor": floor,
            "floor_num": floor_num,
        }
        row["address"] = self.get_address(string)
        return row

    def get_address(self, item):
        street_name = r'((\d{1,3}(\s|-)){0,1}(?!км\b)\b\w+\s?){1,3}'
        street_types = r'(бульвар|б-р|ул|улица|пер|ш|пр-т|nул|пр-кт)\.?'
        house_number = r'\d+\/?(\s?\w?\.?\s?\d?)'
        address_mo = re.compile(r'((%s\s?%s)|(%s\s?%s)),\s?(?P<number>%s)'
                                % (street_types, street_name,
                                   street_name, street_types,
                                   house_number))

        address = re.search(address_mo, item)
        if address is None:
            self.logger.warning('Item string: %s dont match address re', item)
            try:
                address = item.split('\n')[-2]
                self.logger.warning('Setting address to %s', address)
            except KeyError:
                address = None
                self.logger.error('Item string: %s dont container enouth \\n section'
                                  'to auto set address', item)
        else:
            address = address.group()
            if '\n' in address:
                address = address.split('\n')[0]
        return address.strip()

    def save_data(self, data):
        self.save_list_to_csv(data)
