import json
from time import sleep
from web_parser.parser import Task, TaskManager

URL = "https://www.avito.ru/ekaterinburg/kvartiry/prodam/vtorichka?f=549_5696-5697-5698-5699-5700-5701-11018-11019-11020-11021"


class GettingPageUrlList(Task):
    """ Get list of items urls for parse """
    scroll_sleep_time = 0.5
    file_path = 'links.txt'

    def prepare(self, driver):
        # TODO: also click load more button
        last = driver.execute_script("return document.body.scrollHeight")
        new = None
        while last != new:
            last = new
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(self.scroll_sleep_time)
            new = driver.execute_script("return document.body.scrollHeight")
            assert new is not None

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
        # TODO: catch io errors
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return file.read().split('\n')


class GettingPageInfo(Task):
    """ parse item """
    total_area_label = "Общая площадь, м²"
    house_type_label = "Тип дома"
    address_label = "Адрес"
    floor_label = "Этаж"
    file_path = "data.json"

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
            file.write('\n')


def main():
    manager = TaskManager()
    getting_links_task = GettingPageUrlList("get_links", [URL])
    manager.add_task(getting_links_task)

    manager.run_by_name("get_links")

    items_links = getting_links_task.get_links()
    parse_item_task = GettingPageInfo("parse_url", items_links)
    manager.add_task(parse_item_task)

    manager.run_by_name("parse_url")


if __name__ == '__main__':
    main()
