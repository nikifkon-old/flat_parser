import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from flat_parser.web_parser.parser import Task
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

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        super().__init__(*args, driver_options=options, **kwargs)

    @classmethod
    def create_task_from_prev_data(cls, prev_data, *args, **kwargs):
        name = "google_maps"
        url = "https://google.com/maps"
        return cls(name, url, *args, prev_data=prev_data, **kwargs)

    @classmethod
    def create_tasks_from_prev_data(cls, prev_data, *args, **kwargs):
        for data in prev_data:
            yield cls.create_task_from_prev_data(*args, prev_data=data, **kwargs)

    @staticmethod
    def _get_valid_google_address(prev_data):
        if prev_data is not None and 'address' in prev_data:
            address = prev_data['address']
            return address

    def prepare(self, driver):
        wait = WebDriverWait(driver, 10)

        search_box_xpath = "//input[@id='searchboxinput']"
        search_btn_xpath = "//button[@id='searchbox-directions']"
        reverse_btn_xpath = "//button[@class='widget-directions-reverse']"
        search_box = driver.find_element_by_xpath(search_box_xpath)
        search_box.send_keys(self.address)

        wait.until(EC.element_to_be_clickable((By.XPATH, search_btn_xpath)))
        btn = driver.find_element_by_xpath(search_btn_xpath)
        btn.click()

        wait.until(EC.element_to_be_clickable((By.XPATH, reverse_btn_xpath)))
        reverse_btn = driver.find_element_by_xpath(reverse_btn_xpath)
        reverse_btn.click()

    def parse(self, driver):
        post_office_time = self.get_post_office_time(driver)
        metro_time = self.get_metro_time(driver)
        data = {**self.prev_data,
                'post_office_time': post_office_time,
                'metro_time': metro_time}
        return data

    def get_post_office_time(self, driver):
        wait = WebDriverWait(driver, 10)

        input_xpath = "//input[@id='searchboxinput']"
        wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
        input_ = driver.find_element_by_xpath(input_xpath)
        input_.send_keys(self.main_post_office_address)
        input_.send_keys(Keys.RETURN)

        switch_to_auto_btn_xpath = "//div[@aria-label='На автомобиле']/.."
        switch_to_auto_btn = driver.find_element_by_xpath(switch_to_auto_btn_xpath)
        switch_to_auto_btn.click()

        # get_few_time
        direction_container = "//div[@id='section-directions-trip-1']"
        few_time_xpath = f"{direction_container}//span"
        wait.until(EC.presence_of_all_elements_located((By.XPATH, direction_container)))
        few_time_text = driver.find_element_by_xpath(few_time_xpath).text
        return str(get_time_in_minutes_by_text(few_time_text))

    def get_metro_time(self, driver):
        wait = WebDriverWait(driver, 10)

        input_xpath = "//input[@id='searchboxinput']"
        wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
        input_ = driver.find_element_by_xpath(input_xpath)

        switch_to_feet_btn_xpath = "//div[@aria-label='Пешком']/.."
        switch_to_auto_btn = driver.find_element_by_xpath(switch_to_feet_btn_xpath)
        switch_to_auto_btn.click()

        few_time = None
        # few_time_station = None
        for metro_station_address in self.metro_station_addresses:
            input_.clear()
            input_.send_keys(metro_station_address)
            input_.send_keys(Keys.RETURN)

            # get_few_time
            direction_container = "//div[@data-trip-index='0']"
            few_time_xpath = f"{direction_container}//div[@class='section-directions-trip-duration']"
            wait.until(EC.presence_of_all_elements_located((By.XPATH, direction_container)))
            metro_time_text = driver.find_element_by_xpath(few_time_xpath).text
            metro_time = get_time_in_minutes_by_text(metro_time_text)
            if few_time is None or metro_time < few_time:
                few_time = metro_time
                # few_time_station = metro_station_address
        return str(few_time)

    def save_data(self, data):
        self.save_data_to_csv(data)
        return data
