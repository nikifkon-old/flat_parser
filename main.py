import re
import os
import csv
from datetime import datetime
from time import sleep, time
from concurrent.futures import ProcessPoolExecutor
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from avito_parser.web_parser.parser import Task, TaskManager, StopTaskException


URL = "https://m.avito.ru/ekaterinburg/kvartiry/prodam/vtorichka"
HOUSE_INFO_URL = "https://domaekb.ru/search?adres="
NBSP = " "


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
            # try:
            #     load_more_button = driver.find_element_by_xpath("//div[.='%s']//span"
            #                                                     % self.load_more_button_label)
            #     load_more_button.click()
            # except NoSuchElementException:
            #     load_more_button = None
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
        return result

    def parse_item(self, item):
        price_mo = re.compile(r'(?P<price>(\d+ ?)+) руб.')
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
        return self.with_house_info_url(row)

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
            number = address.group('number')
            mod_number = number.replace('к', '/')
            address = address.group().replace(number, mod_number)

            if '\n' in address:
                address = address.split('\n')[0]
        normal_address = address.replace('проспект', 'пр-кт').replace('пр-т', 'пр-кт').replace('улица', 'ул')
        return normal_address.strip()

    def with_house_info_url(self, row):
        address = row.get("address")
        if address:
            row['url'] = HOUSE_INFO_URL + address
        return row

    def get_house_info(self, address):
        """
        - улица или заменить на ул.

        """
        adrs = self.modify_address(address)
        url = HOUSE_INFO_URL + adrs
        house_info_task = GettingHouseInfo("get_house_info", [url])
        house_info_task.run()
        return house_info_task.data

    def save_data(self, data):
        return data
        # with open(self.file_path, 'a', encoding='utf-8') as file:
        #     for item in data:
        #         if item is not None:
        #             json.dump(item, file, ensure_ascii=False, indent=4)
        #             file.write(',\n')


class GettingHouseInfo(Task):
    debug_file = 'house_info_debug.log'
    warning_file = 'house_info_warning.log'
    output_file = 'info.csv'

    def __init__(self, *args, prev_data=None, **kwargs):
        self.prev_data = prev_data
        capa = DesiredCapabilities.CHROME
        capa['pageLoadStrategy'] = "none"
        driver_kwargs = {
            "desired_capabilities": capa
        }

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options, driver_kwargs=driver_kwargs, **kwargs)

    @classmethod
    def create_tasks_by_prev_data(cls, data):
        name = "getting_house_info"
        tasks = []
        for item in data:
            tasks.append(cls(name, item['url'], prev_data=item))
        return tasks

    def prepare(self, driver):
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='region region-content']//table[2]//thead//th")
            ))
        except NoSuchElementException:
            self.log_error()
            raise StopTaskException()
        driver.execute_script("window.stop();")

    def parse(self, driver):
        # find house
        try:
            table = driver.find_element_by_xpath("//div[@class='region region-content']//table[2]")
            td = table.find_element_by_xpath(".//td[@class='views-field views-field-field-address'][1]")
            link = td.find_element_by_xpath("./a")
        except NoSuchElementException:
            self.log_error()
            raise StopTaskException()

        link.click()

        # parse house info table
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//article/div")
        ))
        container = driver.find_element_by_xpath("//article/div")

        data = {}
        items = []
        items.append(('build_year', f'Год постройки:{NBSP}'))
        items.append(('lift_count', f'Количество лифтов, ед.:{NBSP}'))
        items.append(('porch_count', f'Количество подъездов, ед.:{NBSP}'))
        items.append(('people_count', f'Количество жителей:'))
        items.append(('public_area', f'Общая площадь помещений, входящих в состав общего имущества, кв.м:{NBSP}'))
        items.append(('land_area', f'Площадь земельного участка, входящего в состав общего имущества в многоквартирном доме, кв.м:{NBSP}'))
        items.append(('foundation_type', f'Тип фундамента:{NBSP}'))
        items.append(('house_type', f'Материал несущих стен:{NBSP}'))
        items.append(('coating_type', f'Тип перекрытий:{NBSP}'))
        items.append(('house_area', f'Общая площадь МКД, кв.м:'))
        items.append(('playground', f'Элементы благоустройства (детская площадка):{NBSP}'))
        items.append(('sport_ground', f'Элементы благоустройства (спортивная площадка):{NBSP}'))

        for name, label in items:
            data[name] = self.get_table_item(container, label)

        return data

    def get_table_item(self, container, text):
        try:
            item = container.find_element_by_xpath(f".//div[.='{text}']/../div[2]")
            return item.text
        except NoSuchElementException:
            return None

    def presave_hook(self, data):
        if self.prev_data:
            data.update(self.prev_data)
        year = data.get('build_year')
        if year is not None:
            data['build_year'] = datetime.now().year - int(year)
        if data.get('url'):
            data.pop('url')
        return data

    def save_data(self, data):
        need_header = False
        if not os.path.exists(self.output_file):
            need_header = True
        with open(self.output_file, 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            if need_header:
                writer.writerow(data.keys())
            writer.writerow(data.values())

    def log_error(self):
        with open(self.debug_file, 'a', encoding='utf-8') as file:
            file.write(f'Address not found in domaekb.ru {self.url}\n')


def run_task(task):
    task.run()


def main():
    start_time = time()
    manager = TaskManager()
    task = manager.create_task(GettingFlatInfo, "getting_flat_info", URL)
    data = task.run()

    tasks = GettingHouseInfo.create_tasks_by_prev_data(data)
    with ProcessPoolExecutor(os.cpu_count()) as executor:
        executor.map(run_task, tasks)

    print(f"Time: {round(time() - start_time, 2)} sec.")


if __name__ == '__main__':
    main()
