import logging
import datetime
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


def get_meter_price(data: dict) -> str:
    if 'price' in data and 'total_area' in data:
        try:
            meter_price = float(data['price']) / float(data['total_area'])
            return str(round(meter_price, 6))
        except (TypeError, ValueError) as exc:
            logger.error('Can not count meter_price', exc_info=exc)


def get_time_in_minutes_by_text(text: str) -> int: 
    try:
        strp = []
        need_date = False
        if 'д.' in text:
            strp.append('%d д.')
            need_date = True
        if 'ч.' in text:
            strp.append('%H ч.')
        if 'мин.' in text:
            strp.append('%M мин.')
        time = datetime.datetime.strptime(text, ' '.join(strp))
        result = time.minute + time.hour * 60
        if need_date:
            result += time.day * 1440
        return result
    except (ValueError, TypeError) as exc:
        logger.error('[Error] Unable to get time in minutest - %s', text, exc_info=exc)
        return None
