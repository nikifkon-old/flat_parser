from collections import namedtuple
from time import sleep
from flat_parser.web_parser.parser import Task


class GettingUPNFlatInfo(Task):
    def __init__(self, *args, **kwargs):
        self.flat_namedtuple = namedtuple('Flat', ['membership', 'rooms',
                                                   'address', 'areas',
                                                   'floors', 'price',
                                                   'house', 'year',
                                                   'walls', 'sell_conditions',
                                                   'video'])
        super().__init__(*args, **kwargs)

    def prepare(self, driver):
        room_checkbox = driver.find_element_by_xpath("//span[@data-search='room']/input")
        room_checkbox.click()
        part_checkbox = driver.find_element_by_xpath("//span[@data-search='part']/input")
        part_checkbox.click()
        submit = driver.find_element_by_xpath("//a[@data-gpush]")
        submit.click()
        sleep(1)

    def parse(self, driver):
        trs = driver.find_elements_by_xpath("//div[@id='panel_search']//table/tbody/tr")

        result = [self.parse_tr(tr) for tr in trs]
        return result

    def clean_data(self, data):
        data['address'] = data['address'].split(', ')[-1]
        data['kitchen_area'] = data['areas'].split(' / ')[-1]
        data['total_area'] = data['areas'].split(' / ')[0]
        data.pop('areas')
        data.pop('membership')
        data.pop('rooms')
        data.pop('house')
        data.pop('year')
        data.pop('walls')
        data.pop('sell_conditions')
        data.pop('video')
        return data

    def parse_tr(self, tr):
        tds = [td.text for td in tr.find_elements_by_xpath("./td")]
        data = self.flat_namedtuple(*tds)._asdict()
        data['link'] = tr.find_element_by_xpath(".//a").get_attribute('href')
        return self.clean_data(data)

    def save_data(self, data):
        return data
