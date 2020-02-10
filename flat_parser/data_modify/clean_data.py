import csv


class DataCleaner:
    """
    Transform values in csv file to specific type.

    Usage:
    cleaner = DataCleaner(path='test.csv', file_type='csv')
    cleaner.clean_price()
    cleaner.write_result()
    """
    def __init__(self, path: str = None, file_type: str = 'csv'):
        if path is None:
            raise FileNotFoundError('You must provide path to file')
        self.path = path
        self.file_type = file_type
        with open(path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.keys = reader.fieldnames
            if self.keys is None:
                print(f'{path} is not valid or empty csv file')
                self.keys = []
            self.data = list(reader)

    def write_result(self, path: str = None) -> str:
        if path is None:
            path_without_ext = ''.join(self.path.split('.')[:-1])
            path = f'{path_without_ext}_cleaned.{self.file_type}'
        with open(path, 'w', encoding='utf-8') as file:
            writter = csv.DictWriter(file, fieldnames=self.keys, restval=0)
            writter.writeheader()
            writter.writerows(self.data)
        return path

    def clean_price(self):
        for row in self.data:
            if 'price' in row:
                row['price'] = row['price'].replace('.', '')
