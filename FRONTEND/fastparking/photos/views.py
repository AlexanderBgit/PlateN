import datetime

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from parking.services import format_registration_id, format_datetime
from .forms import UploadFileForm, UploadScanQRForm
from django.urls import resolve, reverse
from django.conf import settings


# Imaginary function to handle an uploaded file.
from .repository import handle_uploaded_file, TYPES, get_registration_info
from finance.repository import calculate_total_payments
from .services import handle_uploaded_file_qr_code


def upload_file(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    target_type = None
    filename = None
    if request.method == "GET":
        tt = request.GET.get("type")
        if tt:
            target_type = {"type": tt, "desc": TYPES.get(tt)}
    if request.method == "POST":
        tt = request.POST.get("t_photo")
        if tt:
            target_type = {"type": tt, "desc": TYPES.get(tt)}
        # print(f"{request.POST=}")
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            currency = settings.PAYMENT_CURRENCY[0]
            uploaded_file = request.FILES.get("photo")
            if uploaded_file:
                filename = uploaded_file.name
            type_of_photo = form.cleaned_data.get("t_photo")
            file_in = request.FILES.get("photo")
            if file_in:
                registration_id = form.cleaned_data.get("registration_id")
                # MAIN ENGINE !!!
                img_predict = handle_uploaded_file(
                    file_in, type_of_photo, filename, registration_id
                )
                info = img_predict.get("info")
                predict = img_predict.get("predict")
                registration = img_predict.get("registration")
                context = {
                    "active_menu": active_menu,
                    "title": f"Photos | { target_type.get('desc') }",
                    "target_type": target_type,
                    "info": info,
                    "predict": predict,
                    "registration": registration,
                    "currency": currency,
                }
                # print(f"{info}")
                if info:
                    return render(request, "photos/upload_result.html", context)
                else:
                    context = {
                        "active_menu": active_menu,
                        "title": "",
                        "target_type": {"type": 0},
                        "info": "Not recognized",
                        "predict": {
                            "num_avto_str": "Number not recognized",
                            "accuracy": "0",
                        },
                        "registration": "NOT registered",
                    }
                    return render(request, "photos/upload_result.html", context)
            # upload_url = reverse("upload")
            return HttpResponseRedirect("")
    else:
        initial = None
        if target_type:
            initial = {"t_photo": target_type.get("type")}
        form = UploadFileForm(initial=initial)
    context = {
        "active_menu": active_menu,
        "title": f"Photos | {target_type.get('desc')}",
        "form": form,
        "target_type": target_type,
    }
    return render(request, "photos/upload.html", context)


def main(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    # ваш код для обробки запиту тут
    return render(
        request, "photos/main.html", {"active_menu": active_menu, "title": "Photos"}
    )  # або інша логіка відповідно до вашого проекту


def scan_qr(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    if request.method == "POST":
        form = UploadScanQRForm(request.POST, request.FILES)
        r_json = request.POST.get("r_json")
        if form.is_valid():
            r_json = form.cleaned_data.get("r_json")
            file_in = request.FILES.get("photo")
            if file_in:
                # filename = file_in.name
                qr_info = handle_uploaded_file_qr_code(file_in)
                if qr_info.get("date") and isinstance(
                    qr_info["date"], datetime.datetime
                ):
                    qr_info["date"] = format_datetime(qr_info["date"])
                registration_fmt = qr_info.get("id")
                registration_info = None
                if registration_fmt:
                    registration_fmt = format_registration_id(registration_fmt)
                    registration_info = get_registration_info(qr_info.get("id"))
                info = {
                    "description": qr_info.get("result"),
                    "parking_place": qr_info.get("place"),
                    "date": qr_info.get("date"),
                    "registration": registration_fmt,
                }
                if registration_info:
                    info.update(registration_info)
                context = {
                    "active_menu": active_menu,
                    "title": f"Scan QR code result",
                    "info": info,
                }
                # print(f"{info}")
                if info:
                    if r_json:
                        return JsonResponse(context["info"])
                    else:
                        return render(request, "photos/qr_result.html", context)
                else:
                    context = {
                        "active_menu": active_menu,
                        "title": "",
                        "info": {"description": "Not recognized"},
                    }
                    return render(request, "photos/upload_result.html", context)
            # upload_url = reverse("upload")
        if r_json:
            context = {"error": form.errors.as_json()}
            return JsonResponse(context)
        else:
            return HttpResponseRedirect("")
    else:
        form = UploadScanQRForm()
        # form.initial["r_json"] = True
    context = {
        "active_menu": active_menu,
        "form": form,
    }
    return render(request, "photos/scan_qr.html", context)
