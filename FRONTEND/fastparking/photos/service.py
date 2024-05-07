from pathlib import Path
import base64
from io import BytesIO
from django.core import signing


import cv2
import qrcode


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


def scan_qr_code(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Initialize the QRCode detector
    detector = cv2.QRCodeDetector()

    # Detect and decode QR codes
    data, bbox, _ = detector.detectAndDecode(gray)

    # If QR code is detected, print the data
    if bbox is not None:
        print("Data:", data)
        # Convert bbox to integers
        bbox = bbox.astype(int)

        # Draw bounding box around the QR code
        for i in range(len(bbox)):
            box = bbox[i]
            cv2.polylines(image, [box], isClosed=True, color=(0, 255, 0), thickness=10)

        # Display the image
        cv2.imshow("QR Code Scanner", image)
        cv2.waitKey(30000)
        cv2.destroyAllWindows()
    else:
        print("No QR code found")


if __name__ == "__main__":
    # Example usage
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    img_file = str(BASE_DIR.joinpath("readme", "Photos IN_v2.png"))
    print(img_file)
    scan_qr_code(img_file)
