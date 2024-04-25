import base64
import random
from datetime import datetime
from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.core import signing
import qrcode
import pytz

from ds.predict_num import get_num_auto_png_io
from finance.repository import calculate_total_payments
from parking.repository import number_present_on_parking
from parking.services import compare_plates, format_hours

from .models import Photo
from finance.models import Tariff
from parking.models import ParkingSpace, Registration
from cars.models import Car
from datetime import datetime

# from .repository import sign_text, build_qrcode


TYPES = {"0": "IN", "1": "OUT"}


def db_save_photo_information(predict: dict, type: str) -> Photo | None:
    num_auto = predict.get("num_avto_str")
    accuracy = predict.get("accuracy")
    num_img = predict.get("num_img")
    if num_auto and num_img:
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


# def registration_car(utc_datetime, registration_data) -> dict:
#     print(f"registration_car: {utc_datetime=}, {registration_data=}")
#     # DEMO MODE
#     if registration_data.get("type") == "0":
#         registration_data["registration_id"] = random.randint(1, 999999)
#     return registration_data


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


def check_and_register_car(registration_data) -> dict:
    """
    return {
        "success": True,
        "info": "The car does not exist, a new record has been created",
        "car": car,
    }
    """
    num_auto = registration_data.get("num_auto")
    photo_id = registration_data.get("photo_id")
    if not photo_id or not num_auto:
        return {
            "success": False,
            "info": "No license plate information found",
            "car": None,
        }
    photo_id = photo_id.pk
    try:
        car = Car.objects.get(car_number=num_auto)
        if car.blocked:
            return {"success": False, "info": "The car is blocked", "car": car}
        else:
            pay_pass_text = ""
            if car.PayPass:
                pay_pass_text = f", PayPass: {car.PayPass}"
            return {
                "success": True,
                "info": f"The car exists and is not blocked{pay_pass_text}",
                "car": car,
            }
    except Car.DoesNotExist:
        # Створюємо новий запис в таблиці Car
        car = Car.objects.create(car_number=num_auto, photo_car_id=photo_id)
        return {
            "success": True,
            "info": "The car does not exist, a new record has been created",
            "car": car,
        }


def handle_uploaded_file(
    f, type: str | None, filename: str | None = None, registration_id: str | None = None
) -> dict | None:
    """
    RETURNED STRUCTURE of handle_uploaded_file:
    img_predict: {"info": info, "predict": predict, "registration": registration}

    info = str

    predict = {
    "num_avto_str": num_avto_str,
    "accuracy": total_accuracy,
    num_img": num_img,
    }

    registration = {
        "id": registration_id_formatted,
        "parking_place": parking_place,
        "tariff_in": tariff_in,
        "invoice": invoice,
        "compare_plates": compare_plates_result,
        "qr_code": qrcode_img,
        "date": date_formatted,
        "hash": hash_code,
        "total_paid": total_paid
        "duration": duration
    }
    """
    if f and type:
        utc_datetime = datetime.utcnow()
        utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)

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
        register_car_result = {}
        if photo_id and num_auto:
            register_car_result = check_and_register_car(registration_data)
            # print(register_car_result)
            info = register_car_result.get("info")
        else:
            info = "No license plate information found"

        registration_result = None
        registration = None

        binary_image_data = predict.get("num_img")
        if binary_image_data:
            base64_image = build_base64_image(binary_image_data)
            predict["num_img"] = base64_image

        if register_car_result.get("success"):
            # -------------------------------------------------------
            if num_auto and photo_id:
                car = register_car_result.get("car")
                registration_result = register_parking_event(
                    utc_datetime, num_auto, type, photo_id, registration_id, car
                )
            # -------------------------------------------------------
            if registration_result:
                registration_id = registration_result.get("registration_id")
                info = f"Car: {register_car_result.get('info')}, Register: {registration_result.get('info')}"

            if registration_id:
                date_formatted = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
                registration_id_formatted = f"{registration_id:06}"
                parking_place = registration_result.get("parking_place")
                already_on_parking = registration_result.get("already_on_parking")
                tariff_in = registration_result.get("tariff_in")
                invoice = registration_result.get("invoice")
                compare_plates_result = registration_result.get("compare_plates")
                duration = registration_result.get("duration")
                duration_formatted = (
                    f"{duration:.2f}h = {format_hours(duration)}" if duration else None
                )
                invoice_str = f"invoice: {invoice}," if invoice is not None else ""
                reg_info = f"id:{registration_id},place:{parking_place},{invoice_str}date:{int(utc_datetime.timestamp())}|"
                encoded_text = sign_text(reg_info)
                hash_code = encoded_text.split("|:")[-1]
                qrcode_img = build_qrcode(encoded_text)
                total_paid = calculate_total_payments(int(registration_id))
                registration = {
                    "id": registration_id_formatted,
                    "parking_place": parking_place,
                    "already_on_parking": already_on_parking,
                    "tariff_in": tariff_in,
                    "invoice": invoice,
                    "compare_plates": compare_plates_result,
                    "qr_code": qrcode_img,
                    "date": date_formatted,
                    "hash": hash_code,
                    "total_paid": total_paid,
                    "duration": duration_formatted,
                }
        return {"info": info, "predict": predict, "registration": registration}


# def find_free_parking_space(num_auto) -> ParkingSpace:
#     try:
#         car_auto=num_auto
#         # Шукаємо перше вільне місце на парковці
#         parking_space = ParkingSpace.objects.filter(status=False).first()
#         if parking_space:

#             # Змінюємо статус місця на зайнято
#             parking_space.status = True
#             parking_space.save()
#             return parking_space
#         else:
#             return None  # Немає вільних місць на парковці
#     except Exception as e:
#         print(f"Error: {e}")
#         return None


def find_free_parking_space(num_auto=None) -> ParkingSpace | None:
    try:
        # Шукаємо перше вільне місце на парковці
        parking_space = ParkingSpace.objects.filter(status=False).first()
        if parking_space:
            # Змінюємо статус місця на зайнято
            parking_space.status = True
            # Передаємо номер автомобіля, якщо він переданий
            if num_auto:
                parking_space.car_num = num_auto
            parking_space.save()
            return parking_space
        else:
            # Якщо не знайдено вільного місця, повертаємо None
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def parking_space_status_change(id: int, status: bool) -> ParkingSpace | None:
    try:
        parking_space = ParkingSpace.objects.get(pk=id)
        parking_space.status = status
        if not status:
            parking_space.car_num = ""
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
    car: Car | None = None,
) -> dict | None:
    if registration_type == "0":
        return register_parking_in_event(utc_datetime, num_auto, photo_id, car)
    elif registration_type == "1":
        return register_parking_out_event(
            utc_datetime, num_auto, photo_id, registration_id
        )


def register_parking_in_event(
    utc_datetime: datetime, num_auto: str, photo_id: Photo, car: Car | None = None
) -> dict:
    result = {"registration_id": None, "parking_space": None, "info": None}

    already_on_parking = number_present_on_parking(num_auto)
    print(f"register_parking_in_event. {num_auto=}, {already_on_parking=}")
    parking_space = find_free_parking_space(num_auto)

    if parking_space:
        # Реєструємо нову подію на парковці
        try:
            tariff_in = get_price_per_hour(utc_datetime)
            # print(f"register_parking_in_event : {photo_id=}")
            registration = Registration.objects.create(
                entry_datetime=utc_datetime,
                car_number_in=num_auto,
                photo_in=photo_id,
                parking=parking_space,
                tariff_in=tariff_in,
                car=car,
            )
            result = {
                "registration_id": registration.pk,
                "parking_place": parking_space.number,
                "already_on_parking": already_on_parking,
                "tariff_in": tariff_in,
                "info": "Success",
            }
        except Exception as e:
            print(f"Error: {e} , restore free place {parking_space}")
            # restore free place
            parking_space_status_change(parking_space.pk, False)
    else:
        result["info"] = "No free space"
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
            calc_invoice = registration.calculate_parking_fee()
            total_payed = registration.calculate_total_payed()
            duration = registration.get_duration()
            if calc_invoice is None:
                result[
                    "info"
                ] = f"Failed. Missing finance information for id: {registration_id:06}."
                return result
            if total_payed is None:
                total_payed = 0.0
            if total_payed < calc_invoice:
                currency = settings.PAYMENT_CURRENCY[0]
                result["info"] = (
                    f"Failed. Total paid: {total_payed} {currency} for what is less than the invoice "
                    f"of {calc_invoice:.2f} {currency}. Please pay the rest."
                )
                return result

            # invoice = calculate_invoice(
            #     registration.entry_datetime, utc_datetime, registration.tariff_in
            # )
            if calc_invoice is not None:
                registration.invoice = "{:.2f}".format(float(calc_invoice))

            registration.exit_datetime = utc_datetime
            registration.car_number_out = num_auto
            registration.photo_out = photo_id
            registration.save()
            # compare_plates_result = compare_plates(
            #     registration.car_number_in, registration.car_number_out
            # )
            compare_plates_result = registration.compare_in_out()
            # Free parking space
            parking_space_status_change(registration.parking.pk, False)
            result = {
                "registration_id": registration.pk,
                "parking_place": registration.parking.number,
                "tariff_in": registration.tariff_in,
                "invoice": calc_invoice,
                "compare_plates": compare_plates_result,
                "duration": duration,
                "info": "Success",
            }
        except Registration.DoesNotExist as e:
            print(f"Error: {e}")
    else:
        result["info"] = "registration_id not found"
    return result


def get_price_per_hour(entry_time) -> float | None:
    """
    Returns the price per hour from the Tariff object applicable at the given time.
    """
    applicable_tariffs = Tariff.objects.filter(
        start_date__lte=entry_time.replace(tzinfo=pytz.utc),
        end_date__gte=entry_time.replace(tzinfo=pytz.utc),
    ).order_by(
        "-start_date"
    )  # Get the latest applicable tariff

    if applicable_tariffs.exists():
        applicable_tariff = applicable_tariffs.first()
        return float(applicable_tariff.price_per_hour)
    else:
        return None


# NO USED, USED - Registration.calculate_parking_fee()
def calculate_invoice(
    entry_datetime: datetime | None,
    exit_datetime: datetime | None,
    tariff_in,
) -> float:
    parking_fee = 0.0
    if (
        entry_datetime is not None
        and exit_datetime is not None
        and tariff_in is not None
    ):
        duration = exit_datetime.replace(tzinfo=pytz.utc) - entry_datetime.replace(
            tzinfo=pytz.utc
        )
        hours = duration.total_seconds() / 3600  # переводимо час в години
        if tariff_in:
            price_per_hour = float(tariff_in)  # Зміна типу на float
            parking_fee = round(hours * price_per_hour, 2)
    return parking_fee


def calculate_invoice_for_reg_id(
    registration_id: int, update_record: bool = False
) -> float | None:
    result = None

    try:
        registration = Registration.objects.get(pk=registration_id)
        tariff_in = registration.tariff_in
        if tariff_in:
            tariff_in = float(registration.tariff_in)
            result = calculate_invoice(
                entry_datetime=registration.entry_datetime,
                exit_datetime=registration.exit_datetime,
                tariff_in=tariff_in,
            )
            if update_record and result:
                registration.invoice = str(result)
                registration.save()

    except Registration.DoesNotExist as e:
        print(f"Error: {e}")
    print("calculate_invoice_for_reg_id", registration_id, result)
    return result


def get_registration_allowed_for_out():
    # Filter registrations where invoice is null and payment is not null
    # queryset = Registration.objects.filter(
    #     invoice__isnull=True, payment__isnull=False
    # )

    # Retrieve all registrations where invoice is null
    queryset_inv = Registration.objects.filter(invoice__isnull=True)

    # Filter registrations where invoice is null and payment is not null
    queryset_pks = queryset_inv.filter(payment__isnull=False).values_list(
        "pk", flat=True
    )

    # Filter registrations where calculate_parking_fee method returns 0
    filtered_queryset_pks = [
        registration.pk
        for registration in queryset_inv
        if registration.calculate_parking_fee() == 0
    ]

    # # Combine the two sets of registrations
    # for registration in queryset:
    #     if registration not in filtered_queryset:
    #         filtered_queryset.append(registration)

    # Combine the two sets of registrations
    united_queryset_pks = set(queryset_pks) | (set(filtered_queryset_pks))
    print(f"{united_queryset_pks=}")
    # Convert the list to a queryset
    return Registration.objects.filter(
        pk__in=[reg_pk for reg_pk in united_queryset_pks]
    ).order_by("entry_datetime")
