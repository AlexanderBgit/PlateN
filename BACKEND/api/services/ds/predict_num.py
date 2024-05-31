import asyncio
import os
import io
from pathlib import Path

# import matplotlib.pyplot as plt
import numpy as np
import cv2
from keras import saving

from services.ds.image_ops import extract_plate, segment_to_contours, fix_dimension

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
models_path = Path(__file__).resolve().parent.joinpath("models")
file_model = "ua-license-plate-recognition-model-37x.h5"
file_cascade = "haarcascade_russian_plate_number.xml"

full_path_models = models_path.joinpath(file_model)
full_path_cascade = str(models_path.joinpath(file_cascade))

# Завантаження моделі та каскадного класифікатора
try:
    model = saving.load_model(full_path_models)
    plate_cascade = cv2.CascadeClassifier(full_path_cascade)
    model_load_status = True
except Exception:
    model_load_status = None


async def predict_result(ch_contours, model):
    """
    # Predicting the output string number by contours
    """
    dic = {}
    characters = "#0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, c in enumerate(characters):
        dic[i] = c

    total_accuracy = 1.0

    output = []
    for i, ch in enumerate(ch_contours):
        img_ = cv2.resize(ch, (28, 28))  # interpolation=cv2.INTER_LINEAR by default

        img = fix_dimension(img_)
        img = img.reshape(1, 28, 28, 3)  # preparing image for the model

        prediction = await asyncio.to_thread(model.predict, img, verbose=0)
        # prediction = model.predict(img, verbose=0)

        y_ = np.argmax(prediction, axis=-1)[0]  # predicting the class

        # print(y_, prediction.shape, prediction)
        character = dic[y_]
        # accuracy = prediction[0][y_]
        # print(f'{accuracy=}')
        # total_accuracy *= accuracy
        # print(f'{total_accuracy=}')

        output.append(character)

    plate_number = "".join(output)
    return plate_number, total_accuracy


async def get_num_avto(img_avto):
    img = img_avto.copy()
    output_img, num_img = extract_plate(img, plate_cascade)

    if num_img is not None:
        chars = segment_to_contours(num_img)

        predicted_str, total_accuracy = await predict_result(chars, model)
        num_avto_str = str.replace(predicted_str, "#", "")

        return {
            "num_avto_str": num_avto_str,
            "accuracy": total_accuracy,
            "num_img": num_img,
        }
    else:
        return {}


def decode_io_file(f):
    io_buf = io.BytesIO(f)
    # io_buf.seek(0)
    decode_img = cv2.imdecode(np.frombuffer(io_buf.getbuffer(), np.uint8), -1)
    return decode_img


async def get_num_auto_png_io(f) -> dict:
    img = decode_io_file(f)
    return await get_num_auto_png(img)


async def get_num_auto_png(img) -> dict:
    """get_num_auto_png

    :param img: _description_
    :type img: _type_
    :return: _description_
    :rtype: dict {
            "num_avto_str": num_avto_str,
            "accuracy": total_accuracy,
            "num_img": num_img,
        }
    """
    num_result = await get_num_avto(img)
    img = num_result.get("num_img", None)
    is_success = img is not None

    if is_success:
        try:
            is_success, im_buf_arr = cv2.imencode(
                ".png", img, params=[cv2.IMWRITE_PNG_COMPRESSION, 5]
            )
        except Exception:
            is_success = False

    if is_success:
        io_buf = io.BytesIO(im_buf_arr)
        num_result["num_img"] = io_buf.getvalue()
        im_buf_arr = np.zeros(0)

        # tune output accuracy
        if not num_result["num_avto_str"]:
            num_result["accuracy"] = 0
        elif len(num_result["num_avto_str"]) < 6:
            num_result["accuracy"] *= 0.3

    else:
        num_result["num_img"] = None
        num_result["accuracy"] = 0
        print("num_result[num_img] = None")

    return num_result


################################################################################

if __name__ == "__main__":
    img_path = (
        Path(__file__)
        .resolve()
        .parent.parent.parent.parent.joinpath("DS")
        .joinpath("img")
    )
    file_img = "AM0074BB.png"
    full_path_img = str(img_path.joinpath(file_img))

    original = cv2.imread(full_path_img)
    if original is None:
        print("Помилка завантаження зображення. Перевірте шлях до файлу.")
        exit(1)

    # num_result = get_num_avto(original)
    num_result = get_num_auto_png(original)
    print(num_result)
