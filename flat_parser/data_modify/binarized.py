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
            file.read()

    def set_vars(self, _vars: list):
        self.vars = _vars

    def write_result(self, path: str = None):
        if path is None:
            path_without_ext = self.path.split('.')[:-1]
            path = f'{path_without_ext}_binarized.{self.file_type}'
        with open(self.path, encoding='utf-8') as file:
            data = csv.DictReader(file)
            # logic
            with open(path, 'w', encoding='utf-8') as file:
                writter = csv.writer(file)
                writter.writerows(data)
