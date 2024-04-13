from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.urls import reverse


# Imaginary function to handle an uploaded file.
from .repository import handle_uploaded_file


def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            upload_url = reverse("upload")
            return HttpResponseRedirect(upload_url)
    else:
        form = UploadFileForm()
    return render(request, "photos/upload.html", {"form": form})


def main(request):
    # ваш код для обробки запиту тут
    return render(
        request, "photos/main.html"
    )  # або інша логіка відповідно до вашого проекту
