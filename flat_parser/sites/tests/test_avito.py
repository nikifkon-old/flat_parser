import pytest
from flat_parser.sites.avito import AvitoParser


@pytest.mark.parametrize('item_text, expected', [
    ['2-к квартира, 53.6 м², 4/4 эт.\n3 700 000 руб.\nДинамо, 2,7 км, Первомайская ул., 79\nАгентство\n32 минуты назад',
        {
            'price': '3700000',
            'address': 'Первомайская ул., 79',
            'total_area': '53.6',
            'floor': '4',
            'floor_num': '4'}],
    ['2-к квартира, 53.6 м², 4/4 эт.\n3 700 000 руб.\nДинамо, 2,7 км, Первомайская улица., 79\nАгентство\n32 минуты назад',
        {
            'price': '3700000',
            'address': 'Первомайская улица., 79',
            'total_area': '53.6',
            'floor': '4',
            'floor_num': '4'}],
    ['1-к квартира, 43 м², 3/22 эт.\n3 999 000 руб.\nТатищева, 54\n1 час назад',
        {
            'price': '3999000',
            'address': 'Татищева, 54',
            'total_area': '43',
            'floor': '3',
            'floor_num': '22'}],
    ['2-к квартира, 42.9 м², 1/9 эт.\n2 650 000 руб.\nЧкаловская, 3,5 км, ул. Начдива Онуфриева, 24к2\n"Малахит Риэл" Агентство недвижимости\n2 часа назад',
        {
            'price': '2650000',
            'address': 'ул. Начдива Онуфриева, 24к2',
            'total_area': '42.9',
            'floor': '1',
            'floor_num': '9'}],
    ['2-к квартира, 44.3 м², 1/5 эт.\n2 400 000 руб.\nБотаническая, 12,4 км, Октябрьский район, микрорайон Кольцово, ул. Бахчиванджи, 13А\n"Малахит Риэл" Агентство недвижимости\n3 часа назад',
        {
            'price': '2400000',
            'address': 'ул. Бахчиванджи, 13А',
            'total_area': '44.3',
            'floor': '1',
            'floor_num': '5'}],
    ['1-к квартира, 43 м², 11/21 эт.\n3 085 000 руб.\n«Этажи»\nпроспект Академика Сахарова , 29\nСегодня, 12:27',
        {
            'price': '3085000',
            'address': 'проспект Академика Сахарова , 29',
            'total_area': '43',
            'floor': '11',
            'floor_num': '21'}]
])
def test_get_address(item_text, expected):
    task = AvitoParser('test', 'url')
    assert task.parse_string(item_text) == expected


def test_run_multi_process():
    test_string = '2-к квартира, 42.9 м², 1/9 эт.\n2 650 000 руб.\nЧкаловская, 3,5 км, ул. Начдива Онуфриева, 24к2\n"Малахит Риэл" Агентство недвижимости\n2 часа назад'
    expected = {
        'price': '2650000',
        'address': 'ул. Начдива Онуфриева, 24к2',
        'total_area': '42.9',
        'floor': '1',
        'floor_num': '9',
        'link': 'url',
        'meter_price': '61771.561772'}
    task = AvitoParser('test', 'url')
    result = task.run_multi_proccess(task.parse_item, [(test_string, 'url')])
    assert list(result) == [expected]


@pytest.mark.parametrize('passed, expected', [
    (2, 2),
    (None, 1)
])
def test_avito_init(passed, expected):
    task = AvitoParser("test", "test", scroll_count=passed)
    assert task.scroll_count == expected
