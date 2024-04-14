import base64
from datetime import datetime
from pathlib import Path
from django.conf import settings

from ds.predict_num import get_num_auto_png_io

from .models import Photo

TYPES = {"0": "IN", "1": "OUT"}


<<<<<<< HEAD
def save_prediction(predict: dict, type: str) -> None:
=======
def db_save_photo_information(predict: dict, type: str) -> int | None:
>>>>>>> 24a318c026ab56ee1be90672976362ed52bc0463
    num_auto = predict.get("num_avto_str")
    accuracy = predict.get("accuracy")
    num_img = predict.get("num_img")
    if num_auto:
        record = Photo()
        record.recognized_car_number = num_auto
        record.accuracy = accuracy
        record.photo = num_img
        record.type = type
        record.save()
<<<<<<< HEAD
=======
        return record.id
>>>>>>> 24a318c026ab56ee1be90672976362ed52bc0463


def save_image(f, type: str = "", filepath: Path | None = None):
    if filepath is None:
        if settings.MEDIA_ROOT:
            utc_datetime = datetime.utcnow()
            file_date = utc_datetime.strftime("%Y%m%d%H%M%S")
            media: Path = settings.MEDIA_ROOT.joinpath("photos").joinpath(
                TYPES.get(type)
            )
            media.mkdir(parents=True, exist_ok=True)
            image_type = "jpg"
            filepath = media.joinpath(f"{file_date}.{image_type}")
    if f and filepath:
        with filepath.open("wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)


<<<<<<< HEAD
def handle_uploaded_file(f, type: str | None) -> dict[str, dict]:
    if f and type:
=======
def registration_car(utc_datetime, registration_data):
    print(f"registration_car: {utc_datetime=}, {registration_data=}")


def handle_uploaded_file(f, type: str | None) -> dict[str, dict]:
    if f and type:
        utc_datetime = datetime.utcnow()
>>>>>>> 24a318c026ab56ee1be90672976362ed52bc0463
        info = f"File accepted, sizes: {len(f) // 1024} KB, {type=}"
        #  try to save
        # try:
        #  save_image(f, type=type)
        # except Exception:
        #     ...

        # analyze and calculate prediction of image
        predict = get_num_auto_png_io(f.read())
        # store information to database
<<<<<<< HEAD
        save_prediction(predict, type)
=======
        photo_id = db_save_photo_information(predict, type)
        # registration
        num_auto = predict.get("num_avto_str")
        registration_data = {"photo_id": photo_id, "num_auto": num_auto, "type": type}
        registration_car(utc_datetime, registration_data)
>>>>>>> 24a318c026ab56ee1be90672976362ed52bc0463
        # prepare for show on web page
        binary_image_data = predict.get("num_img")
        if binary_image_data:
            base64_image = base64.b64encode(binary_image_data).decode("utf-8")
            predict["num_img"] = base64_image
        return {"info": info, "predict": predict}
