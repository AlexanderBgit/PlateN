from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.urls import resolve, reverse


# Imaginary function to handle an uploaded file.
from .repository import handle_uploaded_file, TYPES


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
        tt = request.POST.get("type")
        if tt:
            target_type = {"type": tt, "desc": TYPES.get(tt)}
        print(f"{request.POST=}")
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES.get("photo")
            if uploaded_file:
                filename = uploaded_file.name
            type_of_photo = request.POST.get("type")
            file_in = request.FILES.get("photo")
            if file_in:
                registration_id = request.POST.get("registration_id")
                img_predict = handle_uploaded_file(
                    file_in, type_of_photo, filename, registration_id
                )
                info = img_predict.get("info")
                predict = img_predict.get("predict")
                registration = img_predict.get("registration")
                context = {
                    "active_menu": active_menu,
                    # "form": form,
                    "target_type": target_type,
                    "info": info,
                    "predict": predict,
                    "registration": registration,
                }
                # print(f"{info}")
                if info:
                    return render(request, "photos/upload_result.html", context)
            # upload_url = reverse("upload")
            return HttpResponseRedirect("")
    else:
        initial = None
        if target_type:
            initial = {"type": target_type.get("type")}
        form = UploadFileForm(initial=initial)
    context = {"active_menu": active_menu, "form": form, "target_type": target_type}
    return render(request, "photos/upload.html", context)


def main(request):
    active_menu = "photos"
    # ваш код для обробки запиту тут
    return render(
        request, "photos/main.html", {"active_menu": active_menu}
    )  # або інша логіка відповідно до вашого проекту
