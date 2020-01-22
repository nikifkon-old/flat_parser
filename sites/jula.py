import re
from flat_parser.web_parser.parser import Task
from flat_parser.web_parser.parser import TaskManager


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
    def prepare(self, driver):
        dl = driver.find_element_by_xpath("//li[@data-test-block='Attributes']//dl[@data-test-component='DescriptionList']")
        load_more_btn = dl.find_element_by_xpath("./dd[last()]/button")
        load_more_btn.click()

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
        return dl.find_element_by_xpath(f".//dt[.='{text}']/following-sibling::dd").text

    def save_data(self, data):
        return data
