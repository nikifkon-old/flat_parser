import os
import csv
import sys
from time import time
from configparser import ConfigParser
from concurrent.futures import ProcessPoolExecutor
from flat_parser.web_parser.parser import TaskManager
from flat_parser.sites.avito import GettingAvitoFlatInfo
from flat_parser.sites.domaekb import GettingHouseInfo
from flat_parser.sites.jula import GettingJulaFlatInfo
from flat_parser.sites.upn import GettingUPNFlatInfo


CONFIG_FILE = "config.ini"


def run_task(task):
    task.run()


def read_config(config_file):
    config = ConfigParser()
    config.read(config_file)
    return config


def get_prev_data(path):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as file:
            dict_reader = csv.DictReader(file)
            data = list(dict_reader)
        return data


def main():
    start_time = time()
    config = read_config(CONFIG_FILE)

    if len(sys.argv) >= 2:
        manager = TaskManager()
        if len(sys.argv) >= 3:
            output_file = sys.argv[2]
        else:
            output_file = None
        if sys.argv[1] == 'avito':
            url = config['avito'].get('url')
            if url is None:
                sys.exit('Config has not avito url')
            task = manager.create_task(GettingAvitoFlatInfo, "avito", url,
                                       output_file=output_file)
            task.run()
        elif sys.argv[1] == 'jula':
            url = config['jula'].get('url')
            if url is None:
                sys.exit('Config has not jula url')
            task = manager.create_task(GettingJulaFlatInfo, "jula", url,
                                       output_file=output_file)
            task.run()
        elif sys.argv[1] == 'upn':
            url = config['upn'].get('url')
            if url is None:
                sys.exit('Config has not upn url')
            task = manager.create_task(GettingUPNFlatInfo, "upn", url,
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
