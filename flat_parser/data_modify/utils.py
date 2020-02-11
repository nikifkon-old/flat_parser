def get_meter_price(data: dict) -> str:
    if 'price' in data and 'total_area' in data:
        try:
            meter_price = float(data['price']) / float(data['total_area'])
            return str(round(meter_price, 6))
        except (TypeError, ValueError):
            pass
