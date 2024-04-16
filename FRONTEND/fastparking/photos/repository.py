import base64
import random
from datetime import datetime
from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.core import signing
import qrcode

from ds.predict_num import get_num_auto_png_io

from .models import Photo

from parking.models import ParkingSpace, Registration
from cars.models import Car
from datetime import datetime

# from .repository import sign_text, build_qrcode


TYPES = {"0": "IN", "1": "OUT"}


def db_save_photo_information(predict: dict, type: str) -> Photo | None:
    num_auto = predict.get("num_avto_str")
    accuracy = predict.get("accuracy")
    num_img = predict.get("num_img")
    if num_auto:
        record = Photo()
        record.recognized_car_number = num_auto
        record.accuracy = accuracy
        record.photo = num_img
        record.type = int(type)
        record.save()
        return record


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


def registration_car(utc_datetime, registration_data) -> dict:
    print(f"registration_car: {utc_datetime=}, {registration_data=}")
    # DEMO MODE
    if registration_data.get("type") == "0":
        registration_data["registration_id"] = random.randint(1, 999999)
    return registration_data


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
    img = qr.make_image(fill_color=(56, 64, 88), back_color="white")

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
        # uniform for manual enter registration_id
        if registration_id and isinstance(registration_id, Registration):
            registration_id = registration_id.pk
        registration_data = {
            "photo_id": photo_id,
            "num_auto": num_auto,
            "type": type,
            "registration_id": registration_id,
        }
        res = check_and_register_car(registration_data)
        print(res)

        # -------------------------------------------------------
        registration_result = None
        if num_auto and photo_id:
            registration_result = register_parking_event(
                utc_datetime, num_auto, type, photo_id, registration_id
            )
        # -------------------------------------------------------

        binary_image_data = predict.get("num_img")
        if binary_image_data:
            base64_image = build_base64_image(binary_image_data)
            predict["num_img"] = base64_image
        if registration_result:
            registration_id = registration_result.get("registration_id")
        registration = None
        if registration_id:
            date_formatted = utc_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
            registration_id_formatted = f"{registration_id:06}"
            parking_place = registration_result.get("parking_place")
            reg_info = f"id:{registration_id},place:{parking_place},date:{int(utc_datetime.timestamp())}|"
            encoded_text = sign_text(reg_info)
            hash_code = encoded_text.split("|:")[-1]
            qrcode_img = build_qrcode(encoded_text)
            registration = {
                "id": registration_id_formatted,
                "parking_place": parking_place,
                "qr_code": qrcode_img,
                "date": date_formatted,
                "hash": hash_code,
            }
        return {"info": info, "predict": predict, "registration": registration}


def check_and_register_car(registration_data):
    num_auto = registration_data.get("num_auto")
    photo_id = registration_data.get("photo_id")
    photo_id = photo_id.pk

    try:
        car = Car.objects.get(car_number=num_auto)
        if car.blocked:
            return {"success": False, "info": "Автомобіль заблокований"}
        else:
            return {"success": True, "info": "Автомобіль існує і не заблокований"}
    except Car.DoesNotExist:
        # Створюємо новий запис в таблиці Car
        car = Car.objects.create(car_number=num_auto, photo_car_id=photo_id)
        return {"success": True, "info": "Автомобіль не існує, створено новий запис"}


def find_free_parking_space() -> ParkingSpace:
    try:
        # Шукаємо перше вільне місце на парковці
        parking_space = ParkingSpace.objects.filter(status=False).first()
        if parking_space:
            # Змінюємо статус місця на зайнято
            parking_space.status = True
            parking_space.save()
            return parking_space
        else:
            return None  # Немає вільних місць на парковці
    except Exception as e:
        print(f"Error: {e}")
        return None


def parking_space_status_change(id: int, status: bool) -> ParkingSpace | None:
    try:
        parking_space = ParkingSpace.objects.get(pk=id)
        parking_space.status = status
        parking_space.save()
        return parking_space
    except ParkingSpace.DoesNotExist as e:
        print(f"Error: {e}")


def register_parking_event(
    utc_datetime: datetime,
    num_auto: str,
    registration_type,
    photo_id: Photo,
    registration_id: int | str | None = None,
) -> dict | None:
    if registration_type == "0":
        return register_parking_in_event(utc_datetime, num_auto, photo_id)
    elif registration_type == "1":
        return register_parking_out_event(
            utc_datetime, num_auto, photo_id, registration_id
        )


def register_parking_in_event(
    utc_datetime: datetime,
    num_auto: str,
    photo_id: Photo,
) -> dict:
    result = {"registration_id": None, "parking_space": None, "info": None}
    parking_space = find_free_parking_space()
    if parking_space:
        # Реєструємо нову подію на парковці
        try:
            print(f"register_parking_in_event : {photo_id=}")
            registration = Registration.objects.create(
                entry_datetime=utc_datetime,
                car_number_in=num_auto,
                photo_in=photo_id,
                parking=parking_space,
            )
            result = {
                "registration_id": registration.pk,
                "parking_place": parking_space.number,
                "info": None,
            }
        except Exception as e:
            print(f"Error: {e} , restore free place {parking_space}")
            # restore free place
            parking_space_status_change(parking_space.pk, False)
    return result


def register_parking_out_event(
    utc_datetime: datetime,
    num_auto: str,
    photo_id: Photo,
    registration_id: int | str | None = None,
) -> dict | None:
    result = {"registration_id": None, "parking_space": None, "info": None}
    if registration_id:
        registration_id = int(registration_id)
        try:
            registration = Registration.objects.get(pk=registration_id)
            registration.exit_datetime = utc_datetime
            registration.car_number_out = num_auto
            registration.photo_out = photo_id
            registration.save()
            result = {
                "registration_id": registration.pk,
                "parking_place": registration.parking.number,
                "info": None,
            }
        except Registration.DoesNotExist as e:
            print(f"Error: {e}")
    return result
