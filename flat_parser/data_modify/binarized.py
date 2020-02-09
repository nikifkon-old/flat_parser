import csv


class Binarized:
    """
    For each nominal variables(in csv file) that taking more then
    two value, create new binary variable.

    Usage:
    binary = Binarized(path='test.csv', file_type='csv')
    list = ['var1', 'var2']
    binary.set_vars(list)
    binary.write_result(path='output.csv')
    """
    def __init__(self, path: str = None, file_type: str = 'csv'):
        if path is None:
            raise FileNotFoundError('You must pass input_file to Binarized')
        self.path = path
        self.file_type = file_type
        with open(path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.keys = reader.fieldnames
            if self.keys is None:
                print(f'{path} is not valid or empty csv file')
                self.keys = []
            self.data = list(reader)

    def set_vars(self, _vars: list):
        self.vars = _vars

    def write_result(self, path: str = None):
        if path is None:
            path_without_ext = self.path.split('.')[:-1]
            path = f'{path_without_ext}_binarized.{self.file_type}'
        new_keys = self.binary_data()
        with open(path, 'w', encoding='utf-8') as file:
            fieldnames = [*self.keys, *new_keys]
            writter = csv.DictWriter(file, fieldnames=fieldnames, restval=0)
            writter.writeheader()
            writter.writerows(self.data)

    def binary_data(self) -> list:
        new_keys = set()
        for flat in self.data:
            for var in self.vars:
                if var in flat:
                    value = flat[var]
                    if value == '':
                        continue
                    new_keys.add(value)
                    flat[value] = 1
        return new_keys
