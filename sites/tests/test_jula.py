from flat_parser.sites.jula import ParseJulaItem


def test_jula_item_parse():
    url = 'https://youla.ru/ekaterinburg/nedvijimost/prodaja-kvartiri/kvartira-2-komnaty-48-m2-5dc84b22b5fc2d861b51f80f'
    task = ParseJulaItem("test", url)
    data = task.run()
    assert data
    assert data.get('price') == '3 700 000'
    assert data.get('address') == 'Екатеринбург, 62/2 улица Уральская'
    assert data.get('floor') == '4'
    assert data.get('floor_num') == '5'
    assert data.get('total_area') == '48 м²'
    assert data.get('kitchen_area') == '7 м²'
