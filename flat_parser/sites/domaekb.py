import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from flat_parser.web_parser.parser import Task, StopTaskException


NBSP = " "
HOUSE_INFO_URL = "https://domaekb.ru/search?adres="


class GettingHouseInfo(Task):
    debug_file = 'house_info_debug.log'
    warning_file = 'house_info_warning.log'
    output_file = 'info.csv'

    def __init__(self, *args, output_file=None, prev_data=None, **kwargs):
        if output_file is not None:
            self.output_file = output_file
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
    def create_task_from_address(cls, prev_data):
        name = "getting_house_info"
        address = prev_data.get('address')
        url = HOUSE_INFO_URL + cls.get_normalize_address(address)
        return cls(name, url, prev_data=prev_data)

    @classmethod
    def create_tasks_from_addresses(cls, prev_datas, **kwargs):
        name = "getting_house_info"

        for prev_data in prev_datas:
            if prev_data:
                address = prev_data.get('address')
                url = HOUSE_INFO_URL + cls.get_normalize_address(address)
                yield cls(name, url, prev_data=prev_data, **kwargs)

    @staticmethod
    def get_normalize_address(address):
        if address is not None and address != '':
            address = re.sub('проспект', 'пр-кт', address)
            address = re.sub('пр-т', 'пр-кт', address)
            address = re.sub('пр ', 'пр-кт ', address)
            address = re.sub('улица', 'ул', address)
            address = re.sub('проспект', 'пр-кт', address)
            address = re.sub('переулок', 'пер.', address)
            address = re.sub('(, )?Россия,? ?', '', address)
            address = re.sub('(, )?Свердловская область,? ?', '', address)
            address = re.sub('(, )?Свердловская обл.,? ?', '', address)
            address = re.sub('(, )?городской округ Екатеринбург,? ?', '', address)
            address = re.sub('(, )?Екатеринбург,? ?', '', address)
            address = re.sub('станция ?', '', address)
            address = re.sub(', д', ', ', address)
            try:
                house_number = r'\d+\/?(\s?(корпус|ст|\w)?\.?\s?\d?)'
                number = re.search(house_number, address).group()
                slash_number = number
                if 'к' in number:
                    slash_number = re.sub(' ?к(орпус)? ?', '/', number)
                elif 'ст' in number:
                    slash_number = re.sub(' ?ст(анция)? ?', '/', number)
                address = address.replace(number, slash_number)
            except AttributeError:
                with open('house_info_debug.log', 'a', encoding='utf-8') as file:
                    file.write(f'Can not get number from address: {address}\n')

        return address

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
            link.click()
        except NoSuchElementException:
            self.log_error()
            raise StopTaskException()
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
            data = {**self.prev_data, **data}
        year = data.get('build_year')
        if year is not None:
            data['build_year'] = datetime.now().year - int(year)
        if data.get('url'):
            data.pop('url')
        return data

    def save_data(self, data):
        self.save_data_to_csv(data)

    def log_error(self):
        with open(self.debug_file, 'a', encoding='utf-8') as file:
            if self.prev_data:
                link = self.prev_data.get('link')
            else:
                link = ''
            file.write(f"Address not found in domaekb.ru {self.url} "
                       f"at {link}\n")
