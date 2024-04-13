import base64

from ds.predict_num import get_num_auto_png_io


def handle_uploaded_file(f, type: str | None) -> dict[str, dict]:
    if f and type:
        info = f"File accepted, sizes: {len(f) // 1024} KB, {type=}"
        predict = get_num_auto_png_io(f)
        binary_image_data = predict.get("num_img")
        if binary_image_data:
            base64_image = base64.b64encode(binary_image_data).decode("utf-8")
            predict["num_img"] = base64_image
        return {"info": info, "predict": predict}
    # with open("aaa.png", "wb+") as destination:
    #     for chunk in f.chunks():
    #         destination.write(chunk)
