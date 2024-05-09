import io
import os
from datetime import datetime
from pathlib import Path
import base64
from io import BytesIO

import numpy as np
from django.core import signing


import cv2
import qrcode
from pdf2image import convert_from_bytes
from pdf2image.exceptions import PDFInfoNotInstalledError


def sign_text(text):
    signer = signing.Signer()
    encoded_text = signer.sign(text)
    return encoded_text


def unsigned_text(text):
    signer = signing.Signer()
    try:
        original = signer.unsign(text)
        return original
    except signing.BadSignature:
        print("Tampering detected!")
        return None


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


def scan_qr_code(image, debug: bool = False) -> str | None:
    # Read the image
    if isinstance(image, str):
        image = cv2.imread(image)
    if image is None or not image.any():
        return None
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Initialize the QRCode detector
    detector = cv2.QRCodeDetector()
    # Detect and decode QR codes
    data_qr, bbox, _ = detector.detectAndDecode(gray)
    print(f"{data_qr=}")
    # If QR code is detected, print the data
    if data_qr and bbox is not None:
        # print("Data:", data)
        if debug:
            # Convert bbox to integers
            bbox = bbox.astype(int)
            # Draw bounding box around the QR code
            for i in range(len(bbox)):
                box = bbox[i]
                cv2.polylines(
                    image, [box], isClosed=True, color=(0, 255, 0), thickness=10
                )
            # Display the image
            cv2.imshow("QR Code Scanner", image)
            cv2.waitKey(30000)
            cv2.destroyAllWindows()
        return data_qr


def read_pdf_image(in_bytes):
    try:
        pages = convert_from_bytes(in_bytes)
        in_mem = io.BytesIO()
        for page in pages:
            page.save(in_mem, format="png")
            break
        in_mem.seek(0)
        return in_mem
    except PDFInfoNotInstalledError as err:
        print(
            "read_pdf_image: Installed poppler os app? (https://pypi.org/project/pdf2image)",
            err,
        )
        return None


def decode_io_file(f):
    if isinstance(f, str):
        return cv2.imread(f)
    content_type = f.content_type
    print(f"{content_type=}")
    if content_type == "application/pdf":
        io_buf = read_pdf_image(f.read())
        if io_buf is None:
            return None
    else:
        io_buf = io.BytesIO(f.read())
        io_buf.seek(0)
    decode_img = cv2.imdecode(np.frombuffer(io_buf.getbuffer(), np.uint8), -1)
    return decode_img


def get_qr_code_data(f: object) -> dict | None:
    data_decoded = {
        "result": "Not found information",
    }
    img = decode_io_file(f)
    if img is None:
        return None
    data_qr = scan_qr_code(img)
    if data_qr:
        data_decoded_text = unsigned_text(data_qr)
        if data_decoded_text:
            key_value_pairs = [
                item.strip() for item in data_decoded_text.rstrip("|").split(",")
            ]
            try:
                data_decoded = dict(pair.split(":") for pair in key_value_pairs)
            except ValueError:
                ...
            if data_decoded.get("date"):
                try:
                    data_decoded["date"] = datetime.utcfromtimestamp(
                        int(data_decoded["date"])
                    )
                except ValueError:
                    ...
            if data_decoded and isinstance(data_decoded.get("date"), datetime):
                data_decoded["result"] = "Success"
        else:
            data_decoded["result"] = "Error. Wrong QR code, maybe it's not our code?"
    return data_decoded


def handle_uploaded_file_qr_code(f) -> dict | None:
    if not f:
        return None
    return get_qr_code_data(f)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
    # Example usage
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    # img_file = str(BASE_DIR.joinpath("readme", "Photos IN_v2.png"))
    img_file = str(BASE_DIR.joinpath("img", "test", "qr_example_text.png"))
    print(img_file)
    data = get_qr_code_data(img_file)
    print(data)
