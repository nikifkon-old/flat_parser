import logging
import re


logger = logging.getLogger(__name__)


def normolize_address_for_domaekb(address):
    if address is not None and address != '':
        address = re.sub('проспект', 'пр-кт', address)
        address = re.sub('пр-т', 'пр-кт', address)
        address = re.sub('пр ', 'пр-кт ', address)
        address = re.sub('улица', 'ул', address)
        address = re.sub('проспект', 'пр-кт', address)
        address = re.sub('переулок', 'пер.', address)
        address = re.sub('(, )?Россия,? ?', '', address)
        address = re.sub('(, )?Свердловская область,? ?', '', address)
        address = re.sub('(, )?Свердловская обл.,? ?', '', address)
        address = re.sub(
            '(, )?городской округ Екатеринбург,? ?', '', address)
        address = re.sub('(, )?Екатеринбург,? ?', '', address)
        address = re.sub('станция ?', '', address)
        address = re.sub(', д', ', ', address)
        try:
            house_number = r'\d+\/?(\s?(корпус|ст|\w)?\.?\s?\d?)'
            number = re.search(house_number, address).group()
            slash_number = number
            if 'к' in number:
                slash_number = re.sub(' ?к(орпус)? ?', '/', number)
            elif 'ст' in number:
                slash_number = re.sub(' ?ст(анция)? ?', '/', number)
            address = address.replace(number, slash_number)
        except AttributeError:
            logger.warning('Can not get number from address: %s', address)

    return address
