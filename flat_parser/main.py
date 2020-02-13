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
from flat_parser import data_modify


CONFIG_FILE = "config.ini"


def run_task(task):
    task.run()


def read_config(config_file):
    config = ConfigParser()
    config.read(config_file)
    return config


def get_prev_data(path):
    if path is None:
        sys.exit(f'No input file passed to console or in config file: {CONFIG_FILE}')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as file:
            dict_reader = csv.DictReader(file)
            data = list(dict_reader)
        return data
    else:
        print(f'Input file: {path} does not exist. '
              'Try specify it in config file or passed it as a console argument.')


class NoUrlException(Exception):
    def __init__(self, name):
        self.name = name


def main():
    start_time = time()
    config = read_config(CONFIG_FILE)
    flat_parser_output = config['main'].get('default_output_flat_parsers')

    if len(sys.argv) >= 2:
        name = sys.argv[1]
        manager = TaskManager()
        output_file = sys.argv[2] if len(sys.argv) >= 3 else flat_parser_output

        try:
            if name == 'avito':
                url = config['avito'].get('url')
                scroll_count = int(config['avito'].get('scroll_count'))
                if url is None:
                    raise NoUrlException(name)
                task = manager.create_task(GettingAvitoFlatInfo, "avito", url,
                                           output_file=output_file,
                                           scroll_count=scroll_count)
                task.run()
            elif name == 'jula':
                url = config['jula'].get('url')
                scroll_count = int(config['jula'].get('scroll_count'))
                if url is None:
                    raise NoUrlException(name)
                task = manager.create_task(GettingJulaFlatInfo, "jula", url,
                                           output_file=output_file,
                                           scroll_count=scroll_count)
                task.run()
            elif name == 'upn':
                url = config['upn'].get('url')
                page_count = int(config['upn'].get('page_count'))
                if url is None:
                    raise NoUrlException(name)
                task = manager.create_task(GettingUPNFlatInfo, "upn", url,
                                           output_file=output_file,
                                           page_count=page_count)
                task.run()
            elif name == 'domaekb':
                # get data
                output_file = sys.argv[3] if len(sys.argv) >= 4 else None
                input_file = sys.argv[2] if len(
                    sys.argv) >= 3 else flat_parser_output

                prev_data = get_prev_data(input_file)
                if prev_data:
                    tasks = GettingHouseInfo.create_tasks_from_addresses(prev_data,
                                                                         output_file=output_file)
                    with ProcessPoolExecutor(os.cpu_count()) as executor:
                        executor.map(run_task, tasks)
                # modify data. TODO: move to func and test it
                need_binary = config['main'].get('need_binary')
                cleaned = data_modify.clean_data.clean(input_file=output_file,
                                                       varialbes=need_binary)
                result = data_modify.binarized.binarized(input_file=cleaned)
                print(f'Domaekb parser finished successful. Result file: {result}')
            # No match parser name
            else:
                sys.exit(f'`{name}` is not valid parser name')
        except NoUrlException as exc:
            sys.exit(f'{exc} url is not found in cofing file: {CONFIG_FILE}')
    else:
        print('Please pass parser name')
    print(f"Time: {round(time() - start_time, 2)} sec.")


if __name__ == '__main__':
    main()
