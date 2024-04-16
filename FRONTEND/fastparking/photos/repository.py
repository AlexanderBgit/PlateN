import base64
from datetime import datetime
from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.core import signing
import qrcode

from ds.predict_num import get_num_auto_png_io

from .models import Photo

TYPES = {"0": "IN", "1": "OUT"}


def db_save_photo_information(predict: dict, type: str) -> int | None:
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
        return record.pk


def save_image(
    f, type: str = "", filepath: Path | None = None, filename: str | None = None
):
    if filepath is None:
        if settings.MEDIA_ROOT:
            utc_datetime = datetime.utcnow()
            file_date = utc_datetime.strftime("%Y%m%d%H%M%S")
            media: Path = settings.MEDIA_ROOT.joinpath("photos").joinpath(
                TYPES.get(type)
            )
            media.mkdir(parents=True, exist_ok=True)
            if filename:
                image_type = Path(filename).suffix
            else:
                image_type = ".jpg"
            filepath = media.joinpath(f"{file_date}{image_type}")
    if f and filepath:
        with filepath.open("wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)


def registration_car(utc_datetime, registration_data):
    print(f"registration_car: {utc_datetime=}, {registration_data=}")


def build_base64_image(binary_image_data):
    return base64.b64encode(binary_image_data).decode("utf-8")


def build_html_image(binary_image_data):
    base64_image_data = build_base64_image(binary_image_data)
    return f'<img src="data:image/jpeg;base64,{base64_image_data}">'


def build_qrcode(qr_data) -> str:
    qr = qrcode.QRCode(  # type: ignore
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # type: ignore
        box_size=6,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="brown", back_color="white")

    # img = qrcode.make(qr_data, border=2)
    mem_file = BytesIO()
    img.save(mem_file)
    mem_file.seek(0)
    return build_base64_image(mem_file.getvalue())


def sign_text(text):
    signer = signing.Signer()
    encoded_text = signer.sign(text)
    return encoded_text


def unsign_text(text):
    signer = signing.Signer()
    try:
        original = signer.unsign(text)
        return original
    except signing.BadSignature:
        print("Tampering detected!")
        return None


def handle_uploaded_file(
    f, type: str | None, filename: str | None = None, registration_id: str | None = None
) -> dict[str, dict]:
    if f and type:
        utc_datetime = datetime.utcnow()
        info = f"File accepted, sizes: {len(f) // 1024} KB, {TYPES.get(type)}, {filename=}."
        #  try to save
        # try:
        #  save_image(f, type=type, filename)
        # except Exception:
        #     ...

        # analyze and calculate prediction of image
        predict = get_num_auto_png_io(f.read())
        # store information to database
        photo_id = db_save_photo_information(predict, type)
        # registration
        num_auto = predict.get("num_avto_str")
        registration_data = {
            "photo_id": photo_id,
            "num_auto": num_auto,
            "type": type,
            "registration_id": registration_id,
        }
        registration_result = registration_car(utc_datetime, registration_data)
        # prepare for show on web page
        binary_image_data = predict.get("num_img")
        if binary_image_data:
            base64_image = build_base64_image(binary_image_data)
            predict["num_img"] = base64_image
        date_formated = utc_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
        registration_id = 1
        registration_id_formatted = f"{registration_id:06}"
        parking_place = "L01-01"
        reg_info = f"id:{registration_id},place:{parking_place},date:{int(utc_datetime.timestamp())}|"
        encoded_text = sign_text(reg_info)
        hash_code = encoded_text.split("|:")[-1]
        qrcode_img = build_qrcode(encoded_text)
        registration = {
            "id": registration_id_formatted,
            "parking_place": parking_place,
            "qr_code": qrcode_img,
            "date": date_formated,
            "hash": hash_code,
        }
        return {"info": info, "predict": predict, "registration": registration}
