import datetime


def get_meter_price(data: dict) -> str:
    if 'price' in data and 'total_area' in data:
        try:
            meter_price = float(data['price']) / float(data['total_area'])
            return str(round(meter_price, 6))
        except (TypeError, ValueError):
            pass


def get_time_in_minutes_by_text(text):
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
    except TypeError:
        print(f'[Error] Unable to get time in minutest - {text}')
        return None
