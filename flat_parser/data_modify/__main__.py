import sys
from time import time
from flat_parser.data_modify.binarized import Binarized
from flat_parser.data_modify.clean_data import DataCleaner


VARS = ['foundation_type', 'house_type', 'coating_type']


def main():
    start_time = time()
    if len(sys.argv) >= 2:
        name = sys.argv[1]

        input_file = None
        if len(sys.argv) >= 3:
            input_file = sys.argv[2]

        if name == 'binarized':

            if input_file is None:
                exit('Provide file you want to binarized')

            output_file = None
            if len(sys.argv) >= 4:
                output_file = sys.argv[3]
            binary = Binarized(input_file, file_type='csv')
            binary.set_vars(VARS)
            result_path = binary.write_result(output_file)
            print(f'Output file: {result_path}')

        if name == 'clean_price':
            clean = DataCleaner(input_file)
            clean.clean_price()
            clean.write_result()
        else:
            print(f'Script {name} not found')
    else:
        print('Provide script name, please')
    print(f"Time: {round(time() - start_time, 2)} sec.")


if __name__ == '__main__':
    main()
