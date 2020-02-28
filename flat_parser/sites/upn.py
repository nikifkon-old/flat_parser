from collections import namedtuple

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from flat_parser.web_parser.parser import Task
from flat_parser.utils.data import get_meter_price


class UPNParser(Task):
    def __init__(self, *args, page_count=None, **kwargs):
        self.tr_namedturple = namedtuple('Flat', ['membership', 'rooms',
                                                  'address', 'areas',
                                                  'floors', 'price',
                                                  'house', 'year',
                                                  'walls', 'sell_conditions',
                                                  'video'])
        self.page_count = page_count or 1

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options, **kwargs)

    def prepare(self, driver):
        room_checkbox = driver.find_element_by_xpath(
            "//span[@data-search='room']/input")
        room_checkbox.click()
        part_checkbox = driver.find_element_by_xpath(
            "//span[@data-search='part']/input")
        part_checkbox.click()
        submit = driver.find_element_by_xpath("//a[@data-gpush]")
        submit.click()

    def parse(self, driver):
        result = []
        for _ in range(self.page_count):
            result.extend(self.parse_page(driver))
            self.go_to_next_page(driver)
        return result

    def go_to_next_page(self, driver):
        btn_xpath = ("//div[@id='panel_search']//div[@class='pager_panel right']"
                     "/div[@class='middle']/a[position()=last()-1]")
        next_page_btn = driver.find_element_by_xpath(btn_xpath)
        next_page_btn.click()

    def parse_page(self, driver):
        table_xpath = "//div[@id='panel_search']//table/tbody/tr"
        loader_xpath = "//div[@id='loader']"
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, table_xpath)))
            wait.until(EC.invisibility_of_element((By.XPATH, loader_xpath)))
        except (NoSuchElementException, TimeoutException):
            self.logger.error('Unable to find table at %s', driver.current_url)
            # TODO: get screanshot
            return None
        trs = driver.find_elements_by_xpath(
            "//div[@id='panel_search']//table/tbody/tr")
        result = [self.parse_tr(tr) for tr in trs]
        return result

    def clean_data(self, data):
        if 'address' in data and data.get('address') != '':
            data['address'] = data['address'].split(', ')[-1]
        else:
            self.logger.warning('Cant get address: %s at %s',
                                data['address'], data.get('link'))
            return None

        # get areas
        try:
            data['kitchen_area'] = float(data['areas'].split(' / ')[-1])
        except ValueError as exc:
            self.logger.warning('Cant get kitchen_area: %s at %s',
                                data['areas'], data.get('link'), exc_info=exc)
            data['kitchen_area'] = 0
        try:
            data['total_area'] = float(data['areas'].split(' / ')[0])
        except ValueError as exc:
            self.logger.warning('Cant get total_area: %s at %s',
                                data['areas'], data.get('link'), exc_info=exc)
            data['total_area'] = 0

        data.pop('areas', None)

        # clear price
        if data.get('price') is not None:
            try:
                data['price'] = int(data['price'].replace('.', ''))
            except ValueError as exc:
                self.logger.debug('Cant format price: %s at %s',
                                  data['price'], data.get('link'), exc_info=exc)
                return None

        # get floor
        if data.get('floors') is not None:
            try:
                data['floor'] = int(data['floors'].split('/')[0].strip())
            except (ValueError, IndexError) as exc:
                self.logger.warning('Cant format floor: %s at %s',
                                    data['floors'], data.get('link'), exc_info=exc)
                data['floor'] = None
            try:
                data['floor_count'] = int(data['floors'].split('/')[1].strip())
            except (ValueError, IndexError) as exc:
                self.logger.warning('Cant format floor: %s at %s',
                                    data['floors'], data.get('link'), exc_info=exc)
                data['floor_count'] = None

        data.pop('floors')

        # delete unused
        data.pop('membership', None)
        data.pop('rooms', None)
        data.pop('house', None)
        data.pop('year', None)
        data.pop('walls', None)
        data.pop('sell_conditions', None)
        data.pop('video', None)

        return data

    def parse_tr(self, tr_element):
        tds = [td.text for td in tr_element.find_elements_by_xpath("./td")]
        data = self.tr_namedturple(*tds)._asdict()
        data['link'] = tr_element.find_element_by_xpath(
            ".//a").get_attribute('href')
        data = self.clean_data(data)

        # calc meter price
        data['meter_price'] = get_meter_price(data)
        return data

    def save_data(self, data):
        self.save_list_to_csv(data)
