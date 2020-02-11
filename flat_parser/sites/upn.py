from collections import namedtuple
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from flat_parser.web_parser.parser import Task
from flat_parser.data_modify.utils import get_meter_price


class GettingUPNFlatInfo(Task):
    debug_file = 'upn_debug.log'

    def __init__(self, *args, page_count=None, **kwargs):
        self.flat_namedtuple = namedtuple('Flat', ['membership', 'rooms',
                                                   'address', 'areas',
                                                   'floors', 'price',
                                                   'house', 'year',
                                                   'walls', 'sell_conditions',
                                                   'video'])
        self.page_count = page_count or 1
        super().__init__(*args, **kwargs)

    def prepare(self, driver):
        room_checkbox = driver.find_element_by_xpath("//span[@data-search='room']/input")
        room_checkbox.click()
        part_checkbox = driver.find_element_by_xpath("//span[@data-search='part']/input")
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
        btn_xpath = "//div[@id='panel_search']//div[@class='pager_panel right']/div[@class='middle']/a[position()=last()-1]"
        next_page_btn = driver.find_element_by_xpath(btn_xpath)
        next_page_btn.click()

    def parse_page(self, driver):
        table_xpath = "//div[@id='panel_search']//table/tbody/tr"
        loader_xpath = "//div[@id='loader']"
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_all_elements_located((By.XPATH, table_xpath)))
            wait.until(EC.invisibility_of_element((By.XPATH, loader_xpath)))
        except NoSuchElementException:
            return None
        trs = driver.find_elements_by_xpath("//div[@id='panel_search']//table/tbody/tr")
        result = [self.parse_tr(tr) for tr in trs]
        return result

    def clean_data(self, data):
        if 'address' in data:
            data['address'] = data['address'].split(', ')[-1]
        else:
            with open(self.debug_file, 'a', encoding='utf-8') as file:
                file.write(f'Address is None at {data.get("link")}')

        data['kitchen_area'] = data['areas'].split(' / ')[-1]
        data['total_area'] = data['areas'].split(' / ')[0]
        if data.get('price') is not None:
            data['price'] = data['price'].replace('.', '')
        if data.get('floors') is not None:
            try:
                data['floor'] = data['floors'].split('/')[0].strip()
                data['floor_count'] = data['floors'].split('/')[1].strip()
            except IndexError:
                data.pop('floor', None)
                data.pop('floor_num', None)
            finally:
                data.pop('floors')
        data.pop('areas', None)
        data.pop('membership', None)
        data.pop('rooms', None)
        data.pop('house', None)
        data.pop('year', None)
        data.pop('walls', None)
        data.pop('sell_conditions', None)
        data.pop('video', None)

        return data

    def parse_tr(self, tr):
        tds = [td.text for td in tr.find_elements_by_xpath("./td")]
        data = self.flat_namedtuple(*tds)._asdict()
        data['link'] = tr.find_element_by_xpath(".//a").get_attribute('href')
        data = self.clean_data(data)
        data['meter_price'] = get_meter_price(data)
        return data

    def save_data(self, data):
        self.save_list_to_csv(data)
