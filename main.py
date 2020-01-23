import os
import sys
from time import time
from concurrent.futures import ProcessPoolExecutor
from flat_parser.web_parser.parser import TaskManager
from flat_parser.sites.avito import GettingAvitoFlatInfo
from flat_parser.sites.domaekb import GettingHouseInfo
from flat_parser.sites.jula import GettingJulaFlatInfo


AVITO_URL = "https://m.avito.ru/ekaterinburg/kvartiry/prodam/vtorichka"
JULA_URL = "https://youla.ru/ekaterinburg/nedvijimost/prodaja-kvartiri"


def run_task(task):
    task.run()


def main():
    start_time = time()

    if len(sys.argv) >= 2:
        manager = TaskManager()
        if sys.argv[1] == 'avito':
            task = manager.create_task(GettingAvitoFlatInfo, "avito", AVITO_URL)
        elif sys.argv[1] == 'jula':
            task = manager.create_task(GettingJulaFlatInfo, "jula", JULA_URL)
        else:
            print(f'`{sys.argv[1]}` is not valid parser name')
            sys.exit(1)
        data = task.run()

        addresses = [flat.get("address") for flat in data]
        tasks = GettingHouseInfo.create_tasks_from_addresses(addresses, data)
        with ProcessPoolExecutor(os.cpu_count()) as executor:
            executor.map(run_task, tasks)
    else:
        print('Please pass parser name')

    print(f"Time: {round(time() - start_time, 2)} sec.")


if __name__ == '__main__':
    main()
