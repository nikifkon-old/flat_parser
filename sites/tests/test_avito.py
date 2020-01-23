import pytest
from flat_parser.sites.avito import GettingAvitoFlatInfo


@pytest.mark.parametrize('item_text, expected', [
    ['2-к квартира, 53.6 м², 4/4 эт.\n3 700 000 руб.\nДинамо, 2,7 км, Первомайская ул., 79\nАгентство\n32 минуты назад',
        {
            'price': '3 700 000',
            'address': 'Первомайская ул., 79',
            'total_area': '53.6',
            'floor': '4',
            'floor_num': '4',
            'metro_distance': '2,7'}],
    ['2-к квартира, 53.6 м², 4/4 эт.\n3 700 000 руб.\nДинамо, 2,7 км, Первомайская улица., 79\nАгентство\n32 минуты назад',
        {
            'price': '3 700 000',
            'address': 'Первомайская улица., 79',
            'total_area': '53.6',
            'floor': '4',
            'floor_num': '4',
            'metro_distance': '2,7'}],
    ['1-к квартира, 43 м², 3/22 эт.\n3 999 000 руб.\nТатищева, 54\n1 час назад',
        {
            'price': '3 999 000',
            'address': 'Татищева, 54',
            'total_area': '43',
            'floor': '3',
            'floor_num': '22',
            'metro_distance': None}],
    ['2-к квартира, 42.9 м², 1/9 эт.\n2 650 000 руб.\nЧкаловская, 3,5 км, ул. Начдива Онуфриева, 24к2\n"Малахит Риэл" Агентство недвижимости\n2 часа назад',
        {
            'price': '2 650 000',
            'address': 'ул. Начдива Онуфриева, 24к2',
            'total_area': '42.9',
            'floor': '1',
            'floor_num': '9',
            'metro_distance': '3,5'}],
    ['2-к квартира, 44.3 м², 1/5 эт.\n2 400 000 руб.\nБотаническая, 12,4 км, Октябрьский район, микрорайон Кольцово, ул. Бахчиванджи, 13А\n"Малахит Риэл" Агентство недвижимости\n3 часа назад',
        {
            'price': '2 400 000',
            'address': 'ул. Бахчиванджи, 13А',
            'total_area': '44.3',
            'floor': '1',
            'floor_num': '5',
            'metro_distance': '12,4'}],
    ['1-к квартира, 43 м², 11/21 эт.\n3 085 000 руб.\n«Этажи»\nпроспект Академика Сахарова , 29\nСегодня, 12:27',
        {
            'price': '3 085 000',
            'address': 'проспект Академика Сахарова , 29',
            'total_area': '43',
            'floor': '11',
            'floor_num': '21',
            'metro_distance': None}]
])
def test_get_address(item_text, expected):
    task = GettingAvitoFlatInfo('test', 'url')
    assert task.parse_item(item_text) == expected
