registration_car: utc_datetime=datetime.datetime(2024, 4, 13, 23, 32, 24, 651185), registration_data={'photo_id': 5, 'num_auto': 'AI1182HK', 'type': '0'}
registration_car: utc_datetime=datetime.datetime(2024, 4, 13, 23, 32, 58, 682056), registration_data={'photo_id': 6, 'num_auto': 'AM8417HK', 'type': '1'}
Я приготцував для Ваc такі запити:
registration_data = {"photo_id": photo_id, "num_auto": num_auto, "type": type}
registration_car(utc_datetime, registration_data)
TYPES = {"0": "IN", "1": "OUT"}
photos.repository.TYPES (edited) 