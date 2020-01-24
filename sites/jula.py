import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from flat_parser.web_parser.parser import Task, TaskManager, StopTaskException


class GettingJulaFlatInfo(Task):
    def parse(self, driver):
        container = driver.find_element_by_xpath("//section[@class='product_section']//div[@data-component='Board']/ul")
        links_elements = container.find_elements_by_xpath("./li[@class='product_item']/a")
        links = [element.get_attribute("href") for element in links_elements]

        data = self.parse_items(links)
        return data

    def parse_items(self, links):
        manager = TaskManager()
        tasks = manager.create_tasks(ParseJulaItem, "pasre_jula_item", links)
        data = []
        for task in tasks:
            data.append(task.run())
        return data

    def save_data(self, data):
        return data


class ParseJulaItem(Task):
    debug_file = "jula_debug.log"

    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options, **kwargs)

    def prepare(self, driver):
        try:
            dl = driver.find_element_by_xpath("//li[@data-test-block='Attributes']//dl[@data-test-component='DescriptionList']")
            load_more_btn = dl.find_element_by_xpath("./dd[last()]/button")
            load_more_btn.click()
        except NoSuchElementException:
            with open(self.debug_file, 'a', encoding='utf-8') as file:
                file.write(f'Unable to find decription at {self.url}')
            raise StopTaskException()

    def parse(self, driver):
        data = {}
        price_blank = '\u205f'
        price_text = driver.find_element_by_xpath("//span[@data-test-component='Price']").text
        price_mo = re.compile(r'(?P<price>(\d+%s?)+)' % price_blank)
        price = re.search(price_mo, price_text).group('price')
        data["price"] = price

        address = driver.find_element_by_xpath("//li[@data-test-component='ProductMap']//span").text
        data["address"] = address
        # modify address
        dl = driver.find_element_by_xpath("//li[@data-test-block='Attributes']//dl[@data-test-component='DescriptionList']")

        prop_list = [
            ('floor', 'Этаж'),
            ('floor_num', 'Этажность дома'),
            ('total_area', 'Общая площадь'),
            ('kitchen_area', 'Площадь кухни')
        ]
        for var_name, label in prop_list:
            data[var_name] = self.get_dd_by_dt_text(dl, label)

        return data

    def get_dd_by_dt_text(self, dl, text):
        try:
            return dl.find_element_by_xpath(f".//dt[.='{text}']/following-sibling::dd").text
        except NoSuchElementException:
            with open(self.debug_file, 'a', encoding='utf-8') as file:
                file.write(f'Unable to find {text} in {self.url}\n')
            return None

    def save_data(self, data):
        return data
