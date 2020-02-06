import re
import os
from time import sleep
from concurrent.futures import ProcessPoolExecutor
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from flat_parser.web_parser.parser import Task


class GettingAvitoFlatInfo(Task):
    """ Get list of items urls for parse """
    scroll_sleep_time = 0.4
    load_more_button_label = "Загрузить еще"
    output_file = 'flat_info.csv'
    debug_file = "flat_info_debug.log"
    max_count = 10

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
        count = 0
        while (last != new or load_more_button) and count < self.max_count:
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
            count += 1

    def parse(self, driver):
        result = []
        container = driver.find_element_by_xpath(".//*[@data-marker='items/list']")
        items = container.find_elements_by_xpath(".//*[@data-marker='item/link']/../..")
        items_data = []
        for item in items:
            url = item.find_element_by_xpath(".//a").get_attribute('href')
            items_data.append((item.text, url))
        with ProcessPoolExecutor(os.cpu_count()) as executor:
            result = executor.map(self.parse_item, items_data)
        return result

    def parse_item(self, data):
        item = data[0]
        url = data[1]
        price_mo = re.compile(r'(?P<price>(\d+ ?)+).руб\.')
        total_area_mo = re.compile(r'(?P<area>\d+(\.)?\d) м²')
        floor_mo = re.compile(r'(?P<floor>\d+)\/(?P<floor_num>\d+) эт.')
        metro_distance_mo = re.compile(r'(?P<distance>\d+(,\d+)?) км')

        price = re.search(price_mo, item)
        if price is not None:
            price = price.group('price')
        total_area = re.search(total_area_mo, item)
        if total_area is not None:
            total_area = total_area.group('area')
        floor = re.search(floor_mo, item)
        if floor is not None:
            floor = floor.group('floor')
        floor_num = re.search(floor_mo, item)
        if floor_num is not None:
            floor_num = floor_num.group('floor_num')

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
            "metro_distance": metro_distance,
            "link": url
        }
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
            try:
                address = item.split('\n')[-2]
            except:
                address = None
            with open(self.debug_file, 'a', encoding='utf-8') as file:
                file.write(('[Warning] Address dont match re.'
                            'We set address to `%s`,'
                            'text: %s \n') % (address, item))
        else:
            address = address.group()
            if '\n' in address:
                address = address.split('\n')[0]
        return address.strip()

    def save_data(self, data):
        self.save_list_to_csv(data)
