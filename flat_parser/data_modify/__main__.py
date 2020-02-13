import sys
from time import time
from flat_parser.data_modify.binarized import binarized
from flat_parser.data_modify.clean_data import clean


# TODO: read from config
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
            result_path = binarized(input_file, output_file, variables=VARS)

        elif name == 'clean':
            result_path = clean(input_file, output_file)

        else:
            print(f'Script {name} not found')
        print(f'Output file: {result_path}')
    else:
        print('Provide script name, please')
    print(f"Time: {round(time() - start_time, 2)} sec.")


if __name__ == '__main__':
    main()
