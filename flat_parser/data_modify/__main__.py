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
        output_file = None
        if len(sys.argv) >= 4:
            output_file = sys.argv[3]

        if name == 'binarized':
            if input_file is None:
                exit('Provide file you want to binarized')
            binary = Binarized(input_file, file_type='csv')
            binary.set_vars(VARS)
            result_path = binary.write_result(output_file)

        elif name == 'clean':
            clean = DataCleaner(input_file)
            result_path = clean.write_result(output_file)
        else:
            print(f'Script {name} not found')
        print(f'Output file: {result_path}')
    else:
        print('Provide script name, please')
    print(f"Time: {round(time() - start_time, 2)} sec.")


if __name__ == '__main__':
    main()
