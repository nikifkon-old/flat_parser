from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from flat_parser.web_parser.parser import StopTaskException, Task
from flat_parser.utils.normolize import normolize_address_for_domaekb


NBSP = " "
HOUSE_INFO_URL = "https://domaekb.ru/search?adres="


class DomaekbParser(Task):
    def __init__(self, *args, output_file=None, **kwargs):
        if output_file is not None:
            self.output_file = output_file
        capa = DesiredCapabilities.CHROME
        capa['pageLoadStrategy'] = "none"
        driver_kwargs = {
            "desired_capabilities": capa
        }

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options,
                         driver_kwargs=driver_kwargs, **kwargs)

    @classmethod
    def create_task_from_address(cls, prev_data, **kwargs):
        name = "getting_house_info"
        address = prev_data.get('address')
        url = HOUSE_INFO_URL + normolize_address_for_domaekb(address)
        return cls(name, url, prev_data=prev_data, **kwargs)

    @classmethod
    def create_tasks_from_addresses(cls, prev_datas, **kwargs):
        for prev_data in prev_datas:
            yield cls.create_task_from_address(prev_data, **kwargs)

    def prepare(self, driver):
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_all_elements_located(
                (By.XPATH,
                 "//div[@class='region region-content']//table[2]//thead//th")
            ))
        except NoSuchElementException:
            self.logger.error('No data table at %s', driver.current_url)
            raise StopTaskException()
        driver.execute_script("window.stop();")

    def parse(self, driver):
        # find house
        try:
            table = driver.find_element_by_xpath(
                "//div[@class='region region-content']//table[2]")
            td_element = table.find_element_by_xpath(
                ".//td[@class='views-field views-field-field-address'][1]")
            link = td_element.find_element_by_xpath("./a")
            link.click()
        except NoSuchElementException:
            self.logger.error('No address found at %s', driver.current_url)
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
        items.append(
            ('public_area',
             f'Общая площадь помещений, входящих в состав общего имущества, кв.м:{NBSP}'))
        items.append(
            ('land_area', f'Площадь земельного участка, входящего в состав общего имущества'
                          f' в многоквартирном доме, кв.м:{NBSP}'))
        items.append(('foundation_type', f'Тип фундамента:{NBSP}'))
        items.append(('house_type', f'Материал несущих стен:{NBSP}'))
        items.append(('coating_type', f'Тип перекрытий:{NBSP}'))
        items.append(('house_area', f'Общая площадь МКД, кв.м:'))
        items.append(
            ('playground', f'Элементы благоустройства (детская площадка):{NBSP}'))
        items.append(
            ('sport_ground', f'Элементы благоустройства (спортивная площадка):{NBSP}'))

        for name, label in items:
            data[name] = self.get_table_item(container, label)
        return data

    def get_table_item(self, container, text):
        try:
            item = container.find_element_by_xpath(
                f".//div[.='{text}']/../div[2]")
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
