from pathlib import Path

import cv2


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
        cv2.waitKey(8000)
        cv2.destroyAllWindows()
    else:
        print("No QR code found")


if __name__ == "__main__":
    # Example usage
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    img_file = str(BASE_DIR.joinpath("readme", "Photos IN_v2.png"))
    print(img_file)
    scan_qr_code(img_file)
