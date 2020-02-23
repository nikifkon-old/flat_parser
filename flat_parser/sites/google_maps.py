import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, ElementClickInterceptedException
)

from flat_parser.web_parser.parser import Task, StopTaskException
from flat_parser.data_modify.utils import get_time_in_minutes_by_text


class GoogleMapsParser(Task):
    """
    A parser that gets time need to reach (by feet or by auto)
    to certain places (to a main post office or neer metro station)
    from https://google.com/maps. And finally, writes the data to csv file
    """
    metro_station_addresses = [
        'Ботаническая, ул. Белинского, 246А, Екатеринбург, Свердловская обл., 620089',
        'Чкаловская, Екатеринбург, Свердловская обл., 620144',
        'Геологическая, Екатеринбург, Свердловская обл., 620014',
        'Площадь 1905 Года, Екатеринбург, Свердловская обл., 620014',
        'Динамо, Екатеринбург, Свердловская обл., 620027',
        'Уральская, Екатеринбург, Свердловская обл., 620107',
        'Машиностроителей, Екатеринбург, Свердловская обл., 620017',
        'Уралмаш, Екатеринбург, Свердловская обл., 620012',
        'Проспект Космонавтов, Екатеринбург, Свердловская обл., 620135'
    ]
    main_post_office_address = 'Главпочтамт, проспект Ленина, Екатеринбург'

    def __init__(self, *args, prev_data=None, **kwargs):
        self.address = self._get_valid_google_address(prev_data)
        self._refreshed = False

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options, prev_data=prev_data, **kwargs)

    @staticmethod
    def _get_valid_google_address(prev_data):
        if prev_data is not None and 'address' in prev_data:
            address = prev_data['address']
            num_re = re.compile(r'\d+к\d+')
            match = re.search(num_re, address)
            if match:
                num = match.group()
                slash_num = num.replace('к', '/')
                address = address.replace(num, slash_num)
            return address

    def prepare(self, driver):
        if self.address is None or self.address == '':
            raise StopTaskException
        wait = WebDriverWait(driver, 10)

        search_box_xpath = "//input[@id='searchboxinput']"
        search_btn_xpath = "//button[@id='searchbox-directions']"
        reverse_btn_xpath = "//button[@class='widget-directions-reverse']"
        search_box = driver.find_element_by_xpath(search_box_xpath)
        search_box.send_keys(self.address.lower())

        try:
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, search_btn_xpath)))
            btn = driver.find_element_by_xpath(search_btn_xpath)
            btn.click()

            wait.until(EC.element_to_be_clickable(
                (By.XPATH, reverse_btn_xpath)))
            reverse_btn = driver.find_element_by_xpath(reverse_btn_xpath)
            reverse_btn.click()
        except (ElementClickInterceptedException, TimeoutException):
            if not self._refreshed:
                self._refreshed = True
                driver.refresh()
                self.prepare(driver)
            else:
                raise StopTaskException

    def parse(self, driver):
        post_office_time = self.get_post_office_time(driver)
        metro_time = self.get_metro_time(driver)
        data = {**self.prev_data,
                'post_office_time': post_office_time,
                'metro_time': metro_time}
        return data

    def get_post_office_time(self, driver):
        wait = WebDriverWait(driver, 5)

        input_xpath = "//div[@id='directions-searchbox-1']//input"
        wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
        input_ = driver.find_element_by_xpath(input_xpath)
        input_.send_keys(self.main_post_office_address.lower())
        input_.send_keys(Keys.RETURN)

        public_transport_btn_xpath = "//div[@aria-label='На общественном транспорте']/.."
        public_transport_btn = driver.find_element_by_xpath(
            public_transport_btn_xpath)
        public_transport_btn.click()

        # get_few_time
        few_time_xpath = (f"//div[@id='section-directions-trip-0']"
                          f"//div[@class='section-directions-trip-duration']")
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, few_time_xpath)))
            few_time_text = driver.find_element_by_xpath(few_time_xpath).text
            return str(get_time_in_minutes_by_text(few_time_text))
        except TimeoutException:
            print(f'[Error] TimeoutException: address is {self.address}')
            return None

    def get_metro_time(self, driver):
        wait = WebDriverWait(driver, 5)

        input_xpath = "//div[@id='directions-searchbox-1']//input"
        wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
        input_ = driver.find_element_by_xpath(input_xpath)

        switch_to_feet_btn_xpath = "//div[@aria-label='Пешком']/.."
        switch_to_auto_btn = driver.find_element_by_xpath(
            switch_to_feet_btn_xpath)
        switch_to_auto_btn.click()

        few_time = None
        prev_time = None
        # few_time_station = None
        for metro_station_address in self.metro_station_addresses:
            input_.clear()
            input_.send_keys(metro_station_address.lower())
            input_.send_keys(Keys.RETURN)

            # get_few_time
            container = "//div[@data-trip-index='0']"
            few_time_xpath = f"{container}//div[@class='section-directions-trip-duration']"
            try:
                wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, container)))
            except TimeoutException:
                continue
            metro_time_text = driver.find_element_by_xpath(few_time_xpath).text
            metro_time = get_time_in_minutes_by_text(metro_time_text)
            if metro_time:
                if few_time is None or metro_time < few_time:
                    few_time = metro_time
                elif metro_time > prev_time:
                    break
                prev_time = metro_time
                # few_time_station = metro_station_address
        return str(few_time)

    def save_data(self, data):
        self.save_data_to_csv(data)
        return data
