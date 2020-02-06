import os
import csv
import sys
from time import time
from concurrent.futures import ProcessPoolExecutor
from flat_parser.web_parser.parser import TaskManager
from flat_parser.sites.avito import GettingAvitoFlatInfo
from flat_parser.sites.domaekb import GettingHouseInfo
from flat_parser.sites.jula import GettingJulaFlatInfo
from flat_parser.sites.upn import GettingUPNFlatInfo


AVITO_URL = "https://m.avito.ru/ekaterinburg/kvartiry/prodam/vtorichka"
JULA_URL = "https://youla.ru/ekaterinburg/nedvijimost/prodaja-kvartiri?attributes[realty_building_type][0]=166228"
UPN_URL = "https://upn.ru/realty_eburg_flat_sale.htm#panel_search"


def run_task(task):
    task.run()


def get_prev_data(path):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as file:
            dict_reader = csv.DictReader(file)
            data = list(dict_reader)
        return data


def main():
    start_time = time()

    if len(sys.argv) >= 2:
        manager = TaskManager()
        if len(sys.argv) >= 3:
            output_file = sys.argv[2]
        else:
            output_file = None
        if sys.argv[1] == 'avito':
            task = manager.create_task(GettingAvitoFlatInfo, "avito",
                                       AVITO_URL, output_file=output_file)
            task.run()
        elif sys.argv[1] == 'jula':
            task = manager.create_task(GettingJulaFlatInfo, "jula", JULA_URL,
                                       output_file=output_file)
            task.run()
        elif sys.argv[1] == 'upn':
            task = manager.create_task(GettingUPNFlatInfo, "upn", UPN_URL,
                                       output_file=output_file)
            task.run()
        elif sys.argv[1] == 'domaekb':
            if len(sys.argv) >= 4:
                output_file = sys.argv[3]
            else:
                output_file = None
            if len(sys.argv) >= 3:
                input_file = sys.argv[2]
            else:
                input_file = 'flat_info.csv'

            prev_data = get_prev_data(input_file)
            if prev_data:
                tasks = GettingHouseInfo.create_tasks_from_addresses(prev_data,
                                                                     output_file=output_file)
                with ProcessPoolExecutor(os.cpu_count()) as executor:
                    executor.map(run_task, tasks)
        else:
            print(f'`{sys.argv[1]}` is not valid parser name')
            sys.exit(1)
    else:
        print('Please pass parser name')
    print(f"Time: {round(time() - start_time, 2)} sec.")


if __name__ == '__main__':
    main()
