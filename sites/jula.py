import os
import re
from time import sleep
from concurrent.futures import ProcessPoolExecutor
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from flat_parser.web_parser.parser import Task, TaskManager, StopTaskException


def run_task(task):
    return task.run()


class GettingJulaFlatInfo(Task):
    scroll_sleep_time = 0.4
    max_count = 10

    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options, **kwargs)

    def prepare(self, driver):
        last = driver.execute_script("return document.body.scrollHeight")
        new = None
        count = 0
        while last != new and count < self.max_count:
            last = new
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(self.scroll_sleep_time)
            new = driver.execute_script("return document.body.scrollHeight")
            count += 1

    def parse(self, driver):
        container = driver.find_element_by_xpath("//section[@class='product_section']//div[@data-component='Board']/ul")
        links_elements = container.find_elements_by_xpath("./li[@class='product_item']/a")
        links = [element.get_attribute("href") for element in links_elements]

        data = self.parse_items(links)
        return data

    def parse_items(self, links):
        manager = TaskManager()
        tasks = manager.create_tasks(ParseJulaItem, "pasre_jula_item", links)
        with ProcessPoolExecutor(os.cpu_count()) as executor:
            result = executor.map(run_task, tasks)
        return result

    def save_data(self, data):
        return data


class ParseJulaItem(Task):
    debug_file = "jula_debug.log"

    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options, **kwargs)

    def prepare(self, driver):
        dl_xpath = "//li[@data-test-block='Attributes']//dl[@data-test-component='DescriptionList']"
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_all_elements_located((By.XPATH, dl_xpath)))
            dl = driver.find_element_by_xpath(dl_xpath)
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
        data["link"] = self.url
        return data
