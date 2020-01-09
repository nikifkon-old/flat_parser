import json
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from web_parser.parser import Task, TaskManager

URL = "https://www.avito.ru/ekaterinburg/kvartiry/prodam/vtorichka"


class GettingPageUrlList(Task):
    """ Get list of items urls for parse """
    scroll_sleep_time = 0.5 # 0.3
    load_more_button_label = "Загрузить еще"
    file_path = 'links.txt'

    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options, **kwargs)

    def prepare(self, driver):
        last = driver.execute_script("return document.body.scrollHeight")
        new = None
        load_more_button = None
        while last != new or load_more_button:
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

    def parse(self, driver):
        container = driver.find_element_by_xpath(".//*[@data-marker='items/list']")
        links_elements = container.find_elements_by_xpath("//*[@data-marker='item/link']")
        links = [link.get_property("href") for link in links_elements]
        return links

    def save_data(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as file:
            for link in data:
                file.write(link + '\n')

    def get_links(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read().split('\n')
        except FileNotFoundError:
            print('File with parse result dont found: %s' % self.file_path)
            return list()


class GettingPageInfo(Task):
    """ parse item """
    total_area_label = "Общая площадь, м²"
    house_type_label = "Тип дома"
    address_label = "Адрес"
    floor_label = "Этаж"
    file_path = "data.json"

    def __init__(self, *args, **kwargs):
        capa = DesiredCapabilities.CHROME
        capa['pageLoadStrategy'] = "none"
        driver_kwargs = {
            "desired_capabilities": capa
        }

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        super().__init__(*args, driver_options=options,
                         driver_kwargs=driver_kwargs, **kwargs)

    def prepare(self, driver):
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[@data-marker='item-properties/list']")))
        driver.execute_script("window.stop();")

    def parse(self, driver):
        container = driver.find_element_by_xpath(".//*[@data-marker='item-container']")
        price = container.find_element_by_xpath("//*[@data-marker='item-description/price']").text
        prop_list = container.find_element_by_xpath("//*[@data-marker='item-properties/list']")

        total_area = self.get_props_item_text(prop_list, self.total_area_label)
        house_type = self.get_props_item_text(prop_list, self.house_type_label)
        address = self.get_props_item_text(prop_list, self.address_label)
        floor = self.get_props_item_text(prop_list, self.floor_label)

        data = {
            'price': price,
            'address': address,
            'total_area': total_area,
            'house_type': house_type,
            'floor': floor
        }
        return data

    def get_props_item_text(self, prop_list, label):
        item = prop_list.find_element_by_xpath(
            "//*[.='%s']/../*[2]" % label
        )
        return item.text

    def save_data(self, data):
        with open(self.file_path, 'a', encoding='utf-8', newline="") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.write(',\n')


def main():
    start_time = time()
    manager = TaskManager()
    getting_links_task = GettingPageUrlList("get_links", [URL])
    manager.add_task(getting_links_task)

    manager.run_by_name("get_links")

    items_links = getting_links_task.get_links()
    parse_item_task = GettingPageInfo("parse_url", items_links)
    manager.add_task(parse_item_task)

    manager.run_by_name("parse_url")
    print(f"Time: {round(time() - start_time, 2)} sec.")


if __name__ == '__main__':
    main()
