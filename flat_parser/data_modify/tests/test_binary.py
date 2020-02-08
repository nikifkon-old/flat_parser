import pytest
from flat_parser.data_modify.binarized import Binarized


def test_blank_init():
    with pytest.raises(FileNotFoundError):
        Binarized()


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        Binarized('flat_parser/data_modify/tests/this_file_does_not_exist.csv', file_type='csv')


def test_init():
    binary = Binarized('flat_parser/data_modify/tests/normal.csv', file_type='csv')
    assert binary.path == 'flat_parser/data_modify/tests/normal.csv'
    assert binary.file_type == 'csv'


def test_set_vars():
    binary = Binarized('flat_parser/data_modify/tests/normal.csv', file_type='csv')
    var_list = ['test', 'test2']
    binary.set_vars(var_list)
    assert binary.vars == var_list


def test_file_is_empty():
    binary = Binarized('flat_parser/data_modify/tests/empty.csv', file_type='csv')
    var_list = ['test', 'test2']
    binary.set_vars(var_list)
    output_file = 'flat_parser/data_modify/tests/test_empty_output_file.csv'
    binary.write_result(output_file)
    with open(output_file) as file:
        assert file.read() == ''
