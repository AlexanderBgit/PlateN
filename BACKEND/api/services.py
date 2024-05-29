# from ds.predict_num import get_num_auto_png_io
from io import BytesIO


def plate_recognize_tf(image):
    # image = BytesIO(image)
    # predict = get_num_auto_png_io(image)
    image_size = len(image)
    predict = {
        "num_avto_str": f"FASTAPI {image_size=} bytes",
        "accuracy": 0.0,
        "num_img": None,
    }
    return predict
