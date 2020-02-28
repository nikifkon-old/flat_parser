import pytest


RUS_ALPHAABET = 'АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя'
SPECIAL_CHARS = 'ϠϜΗͻ˜ˢˈǌǊ§₽²'


@pytest.mark.parametrize('string', [
    'test_unicode_string',
    f'test_ascii_{RUS_ALPHAABET}',
    f'test_special_characters{SPECIAL_CHARS}'
])
def test_log_encoding(logger, string):
    logger.warning(string)
    with open('flat_parser/tests/flat_parser.log', encoding='utf-8') as file:
        content = file.readlines()
        last = content[-1]
        assert last == string + '\n'
