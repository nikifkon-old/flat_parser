import csv
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from configparser import ConfigParser
from time import time

from flat_parser.data_modify import binarized
from flat_parser.sites.avito import GettingAvitoFlatInfo
from flat_parser.sites.domaekb import GettingHouseInfo
from flat_parser.sites.google_maps import GoogleMapsParser
from flat_parser.sites.jula import GettingJulaFlatInfo
from flat_parser.sites.upn import GettingUPNFlatInfo
from flat_parser.web_parser.parser import TaskManager


CONFIG_FILE = "config.ini"


def run_task(task):
    task.run()


def read_config(config_file):
    config = ConfigParser()
    config.read(config_file)
    return config


def get_prev_data(path):
    if path is None:
        sys.exit(
            f'No input file passed to console or in config file: {CONFIG_FILE}')
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
        super().__init__()


def run_flat_parser_from_command_line(name, config):
    manager = TaskManager()

    flat_parser_output = config['main'].get('default_output_flat_parsers')
    output_file = sys.argv[2] if len(sys.argv) >= 3 else flat_parser_output

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
    print(f'Output file: {output_file}')


def run_house_parser_from_command_line(name, config):
    input_file = sys.argv[2] if len(sys.argv) >= 3 else exit(
        'You must provide input file')

    house_parser_output = config['main'].get('default_output_house_parsers')
    output_file = sys.argv[3] if len(
        sys.argv) >= 4 else house_parser_output

    prev_data = get_prev_data(input_file)
    if name == 'domaekb':
        if prev_data:
            tasks = GettingHouseInfo.create_tasks_from_addresses(prev_data,
                                                                 output_file=output_file)

            with ProcessPoolExecutor(os.cpu_count()) as executor:
                executor.map(run_task, tasks)
    print(f'Output file: {output_file}')


def run_location_parser_from_command_line(name, config):
    input_file = sys.argv[2] if len(sys.argv) >= 3 else exit(
        'You must provide input file')

    location_parser_ouput = config['main'].get(
        'default_output_location_parsers')
    output_file = sys.argv[3] if len(
        sys.argv) >= 4 else location_parser_ouput

    prev_data = get_prev_data(input_file)

    if name == 'google_maps':
        tasks = GoogleMapsParser.create_tasks_from_prev_data(prev_data,
                                                             output_file=output_file)
        with ProcessPoolExecutor(int(os.cpu_count() / 2)) as executor:
            executor.map(run_task, tasks)
    print(f'Output file: {output_file}')


def run_data_mod_from_command_line(name, config):
    input_file = sys.argv[2] if len(sys.argv) >= 3 else exit(
        'You must provide input file')

    data_mod_output = config['main'].get('default_output_data_mod')
    output_file = sys.argv[3] if len(
        sys.argv) >= 4 else data_mod_output

    if name == 'binarized':
        vars_need_be_binary = config['main'].get('vars_need_be_binary')
        var_list = None
        if vars_need_be_binary:
            var_list = vars_need_be_binary.split(',')

        binarized.binarized(input_file=input_file,
                            output_file=output_file,
                            variables=var_list)
    print(f'Output file: {output_file}')


def main():
    start_time = time()
    logging.basicConfig(filename='data/main.log', level=logging.DEBUG)
    config = read_config(CONFIG_FILE)

    if len(sys.argv) >= 2:
        name = sys.argv[1]

        try:
            if name in ['avito', 'jula', 'upn']:
                run_flat_parser_from_command_line(name, config)

            elif name in ['domaekb']:
                run_house_parser_from_command_line(name, config)

            elif name in ['google_maps']:
                run_location_parser_from_command_line(name, config)

            elif name in ['binarized']:
                run_data_mod_from_command_line(name, config)

            else:
                # Doesnt match parser name
                logging.error('%s is not a valid parser name', name)
        except NoUrlException as exc:
            logging.error(
                '%s url is not found in config file: %s', exc, CONFIG_FILE)
    else:
        print('Please pass parser name')
    print("Time: %s sec." % round(time() - start_time, 2))
