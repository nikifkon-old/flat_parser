import pytest
from flat_parser.sites.jula import ParseJulaItem, GettingJulaFlatInfo


@pytest.mark.parametrize('passed, expected', [
    (2, 2),
    (None, 1)
])
def test_jula_init(passed, expected):
    task = GettingJulaFlatInfo("test", "test", scroll_count=passed)
    assert task.scroll_count == expected


def test_jula_item_parse():
    url = 'https://youla.ru/ekaterinburg/nedvijimost/prodaja-kvartiri/kvartira-2-komnaty-48-m2-5dc84b22b5fc2d861b51f80f'
    task = ParseJulaItem("test", url)
    task.run()
    data = task.data
    assert task.status == 'successed'
    assert data
    assert data.get('price') == '3700000'
    assert data.get('address') == 'Екатеринбург, 62/2 улица Уральская'
    assert data.get('floor') == '4'
    assert data.get('floor_num') == '5'
    assert data.get('total_area') == '48'
    assert data.get('kitchen_area') == '7'
    assert data.get('link') == url


@pytest.mark.parametrize('data, expected', [
    (None, None),
    ({'kitchen_area': '14', 'total_area': '43'}, {'kitchen_area': '14', 'total_area': '43'}),
    ({'kitchen_area': '14 м²', 'total_area': '43 м²'}, {'kitchen_area': '14', 'total_area': '43'}),
])
def test_clean_data(data, expected):
    task = ParseJulaItem("test", "test")
    assert expected == task.clean_data(data)
