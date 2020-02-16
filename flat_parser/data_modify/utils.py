import datetime


def get_meter_price(data: dict) -> str:
    if 'price' in data and 'total_area' in data:
        try:
            meter_price = float(data['price']) / float(data['total_area'])
            return str(round(meter_price, 6))
        except (TypeError, ValueError):
            pass


def get_time_in_minutes_by_text(text):
    if 'ч.' in text:
        time = datetime.datetime.strptime(text, '%H ч. %M мин.')
        return time.minute + time.hour * 60
    time = datetime.datetime.strptime(text, '%M мин.')
    return time.minute
