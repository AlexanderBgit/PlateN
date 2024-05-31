import base64
from conf.config import settings

if settings.api_use_plate_ds:
    from services.ds.predict_num import get_num_auto_png_io, model_load_status
else:
    model_load_status = True


def build_base64_image(binary_image_data):
    return base64.b64encode(binary_image_data).decode("utf-8")


async def plate_recognize_tf(image):
    # image = BytesIO(image)
    if settings.api_use_plate_ds:
        predict = await get_num_auto_png_io(image)
    else:
        predict = {
            "num_avto_str": "FASTAPI DISABLED DS",
            "accuracy": 0.0,
            "num_img": None,
        }
    # print(f"{predict=}")
    image_size = len(image)
    if predict:
        if predict.get("num_img"):
            predict["num_img"] = build_base64_image(predict["num_img"])
    else:
        predict = {
            "num_avto_str": f"FASTAPI {image_size=} bytes",
            "accuracy": 0.0,
            "num_img": None,
        }
    return predict
