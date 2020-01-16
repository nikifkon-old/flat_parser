import re
import os
import json
from time import sleep, time
from concurrent.futures import ProcessPoolExecutor
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from avito_parser.web_parser.parser import Task, TaskManager

URL = "https://m.avito.ru/ekaterinburg/kvartiry/prodam/vtorichka"
HOUSE_INFO_URL = "https://domaekb.ru/search?adres="


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
        # while last != new or load_more_button:
        #     # try:
        #     #     load_more_button = driver.find_element_by_xpath("//div[.='%s']//span"
        #     #                                                     % self.load_more_button_label)
        #     #     load_more_button.click()
        #     # except NoSuchElementException:
        #     #     load_more_button = None
        #     last = new
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        #     sleep(self.scroll_sleep_time)
        #     new = driver.execute_script("return document.body.scrollHeight")

    def parse(self, driver):
        result = []
        container = driver.find_element_by_xpath(".//*[@data-marker='items/list']")
        items = container.find_elements_by_xpath(".//*[@data-marker='item/link']")
        items_text = [item.text for item in items]
        with ProcessPoolExecutor(os.cpu_count()) as executor:
            result = executor.map(self.parse_item, items_text)
        return result

    def parse_item(self, item):
        price_mo = re.compile(r'(\d+ )+руб.')
        total_area_mo = re.compile(r'\d+(\.)?\d м²')
        floor_mo = re.compile(r'(?P<floor>\d+)\/\d+ эт.')

        street_name = r'((\d{1,3}(\s|-)){0,1}(?!км\b)\b\w+\s?){1,3}'
        street_types = r'(бульвар|б-р|ул|улица|пер|ш|пр-т|nул|пр-кт)\.?'
        house_number = r'\d+\/?(\s?\w?\.?\s?\d?)'
        address_mo = re.compile(r'((%s\s?%s)|(%s\s?%s)),\s?%s'
                                % (street_types,
                                   street_name,
                                   street_name,
                                   street_types,
                                   house_number))

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
            if '\n' in address:
                address = address.split('\n')[0]

        row = {
            "price": price,
            "address": address,
            "total_area": total_area,
            "floor": floor
        }
        # house_info = self.get_house_info(address)

        # if house_info is not None:
        #     row.update(house_info)
        return row

    def get_house_info(self, address):
        """
        - улица или заменить на ул.

        """
        adrs = self.modify_address(address)
        url = HOUSE_INFO_URL + adrs
        house_info_task = GettingHouseInfo("get_house_info", [url]) # FIXME: url is one
        house_info_task.run()
        return house_info_task.data

    def modify_address(self, address):
        return address

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


class GettingHouseInfo(Task):
    debug_file = 'house_info_debug.log'
    warning_file = 'house_info_warning.log'

    def __init__(self, *args, **kwargs):
        capa = DesiredCapabilities.CHROME
        capa['pageLoadStrategy'] = "none"
        driver_kwargs = {
            "desired_capabilities": capa
        }

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options, driver_kwargs=driver_kwargs, **kwargs)

    def prepare(self, driver):
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//div[@class='region region-content']//table[2]//thead//th")
        ))
        driver.execute_script("window.stop();")

    def parse(self, driver):
        table = driver.find_element_by_xpath("//div[@class='region region-content']//table[2]")
        tds = table.find_elements_by_xpath(".//td[@class='views-field views-field-field-address']")
        data = {
            'adr': [td.text for td in tds]
        }
        return data

    def save_data(self, data):
        self.data = data
        if data is None:
            with open(self.debug_file, 'a', encoding='utf-8') as file:
                file.write('Data is None in url: %s\n' % self.urls[0])
        elif len(data["adr"]) > 1:
            with open(self.warning_file, 'a', encoding='utf-8') as file:
                file.write('Many addresses in %s: %s\n' % (self.urls[0], data["adr"]))


def main():
    start_time = time()
    manager = TaskManager()
    task = manager.create_task(GettingFlatInfo, "getting_flat_info", URL)
    task.run()

    print(f"Time: {round(time() - start_time, 2)} sec.")


if __name__ == '__main__':
    main()
