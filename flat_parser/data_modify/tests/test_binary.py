import csv
import pytest
from flat_parser.data_modify.binarized import Binarized


test_dir = 'flat_parser/data_modify/tests/'


def test_blank_init():
    with pytest.raises(FileNotFoundError):
        Binarized()


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        Binarized('flat_parser/data_modify/tests/csv_cases/this_file_does_not_exist.csv', file_type='csv')


def test_init():
    binary = Binarized(f'{test_dir}csv_cases/case1/data.csv', file_type='csv')
    assert binary.path == f'{test_dir}csv_cases/case1/data.csv'
    assert binary.file_type == 'csv'
    assert len(binary.keys) == 6
    with open(binary.path, encoding='utf-8') as file:
        data = csv.DictReader(file)
        assert list(binary.data) == list(data)


def test_set_vars():
    binary = Binarized('flat_parser/data_modify/tests/csv_cases/normal.csv', file_type='csv')
    var_list = ['test', 'test2']
    binary.set_vars(var_list)
    assert binary.vars == var_list


def test_file_is_empty():
    binary = Binarized('flat_parser/data_modify/tests/csv_cases/empty.csv', file_type='csv')
    var_list = ['test', 'test2']
    binary.set_vars(var_list)
    output_file = 'flat_parser/data_modify/tests/csv_cases/test_empty_output_file.csv'
    binary.write_result(output_file)
    with open(output_file) as file:
        assert list(csv.DictReader(file)) == list()


@pytest.mark.parametrize('file, expected_file', [
    (f'{test_dir}csv_cases/case1/data.csv', f'{test_dir}csv_cases/case1/expected.csv'),
    (f'{test_dir}csv_cases/case2/data.csv', f'{test_dir}csv_cases/case2/expected.csv'),
    (f'{test_dir}csv_cases/case3/data.csv', f'{test_dir}csv_cases/case3/expected.csv'),
])
def test_by_cases(file, expected_file):
    test_output = f'{test_dir}csv_cases/cases_output.csv'
    binary = Binarized(file, file_type='csv')
    var_list = ['test', 'test2']
    binary.set_vars(var_list)

    binary.write_result(test_output)
    with open(expected_file, encoding='utf-8') as file:
        expected_data = list(csv.DictReader(file))
        with open(test_output, encoding='utf-8') as file:
            test_data = list(csv.DictReader(file))
            assert test_data == expected_data
