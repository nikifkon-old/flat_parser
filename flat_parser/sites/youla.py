import os
import re
from concurrent.futures import ProcessPoolExecutor
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from flat_parser.web_parser.parser import Task, StopTaskException
from flat_parser.data_modify.utils import get_meter_price


def run_task(task):
    return task.run()


class YoulaParser(Task):
    def __init__(self, *args, scroll_count=None, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        self.scroll_count = scroll_count or 1
        super().__init__(*args, driver_options=options, **kwargs)

    def prepare(self, driver):
        last = driver.execute_script("return document.body.scrollHeight")
        new = None
        count = 0
        wait = WebDriverWait(driver, 10)
        while last != new and count < self.scroll_count:
            last = new
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight)")
            loader_xpath = "//aside[@data-component='Paginator']//div[@class='loader-colored']"
            try:
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, loader_xpath)))
                wait.until(EC.invisibility_of_element_located(
                    (By.XPATH, loader_xpath)))
            except (NoSuchElementException, TimeoutException):
                break
            new = driver.execute_script("return document.body.scrollHeight")
            count += 1

    def parse(self, driver):
        container = driver.find_element_by_xpath(
            "//section[@class='product_section']//div[@data-component='Board']/ul")
        links_elements = container.find_elements_by_xpath(
            "./li[@class='product_item']/a")
        links = [element.get_attribute("href") for element in links_elements]

        data = self.parse_items(links)
        return data

    def parse_items(self, links):
        tasks = [YoulaItemParser("youla_item", link) for link in links]
        with ProcessPoolExecutor(os.cpu_count()) as executor:
            result = executor.map(run_task, tasks)
        return result

    def save_data(self, data):
        self.save_list_to_csv(data)


class YoulaItemParser(Task):
    debug_file = "data/jula_debug.log"

    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        capa = DesiredCapabilities.CHROME
        capa['pageLoadStrategy'] = "none"
        driver_kwargs = {
            "desired_capabilities": capa
        }
        super().__init__(*args, driver_options=options,
                         driver_kwargs=driver_kwargs, **kwargs)

    def prepare(self, driver):
        dl_xpath = "//li[@data-test-block='Attributes']//dl[@data-test-component='DescriptionList']"
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, dl_xpath)))
            driver.execute_script("window.stop();")
            dl_element = driver.find_element_by_xpath(dl_xpath)
            load_more_btn = dl_element.find_element_by_xpath("./dd[last()]/button")
            load_more_btn.click()
        except (NoSuchElementException, TimeoutException):
            with open(self.debug_file, 'a', encoding='utf-8') as file:
                file.write(f'Unable to find decription at {self.url}')
            raise StopTaskException()

    def get_price(self, driver):
        price_blank = '\u205f'
        price_mo = re.compile(r'(?P<price>(\d+%s?)+)' % price_blank)
        price_text = driver.find_element_by_xpath(
            "//span[@data-test-component='Price']").text
        price = re.search(price_mo, price_text)
        if price is not None:
            price = price.group('price')
            price_int = ''.join(price.split(price_blank))
            return price_int
        return ''

    def parse(self, driver):
        data = {}

        data["price"] = self.get_price(driver)
        address = driver.find_element_by_xpath(
            "//li[@data-test-component='ProductMap']//span")
        data["address"] = address.text

        dl_element = driver.find_element_by_xpath(
            "//li[@data-test-block='Attributes']//dl[@data-test-component='DescriptionList']")
        prop_list = [
            ('floor', 'Этаж'),
            ('floor_num', 'Этажность дома'),
            ('total_area', 'Общая площадь'),
            ('kitchen_area', 'Площадь кухни')
        ]
        for var_name, label in prop_list:
            data[var_name] = self.get_dd_by_dt_text(dl_element, label)
        return data

    def get_dd_by_dt_text(self, dl_element, text):
        try:
            return dl_element.find_element_by_xpath(f".//dt[.='{text}']/following-sibling::dd").text
        except NoSuchElementException:
            with open(self.debug_file, 'a', encoding='utf-8') as file:
                file.write(f'Unable to find {text} in {self.url}\n')
            return None

    def clean_data(self, data):
        if data is not None:
            m_sq = ' м²'
            total_area = data.get("total_area")
            kitchen_area = data.get("kitchen_area")
            if total_area:
                data["total_area"] = ''.join(total_area.split(m_sq))
            if kitchen_area:
                data["kitchen_area"] = ''.join(kitchen_area.split(m_sq))
        return data

    def save_data(self, data):
        data = self.clean_data(data)
        data["link"] = self.url
        data["meter_price"] = get_meter_price(data)
        self.data = data
        return data
