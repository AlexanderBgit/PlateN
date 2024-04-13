def handle_uploaded_file(f, type: str | None):
    if f and type:
        print(f"File accepted, sizes: {len(f) // 1024} KB, {type=}")
    # with open("aaa.png", "wb+") as destination:
    #     for chunk in f.chunks():
    #         destination.write(chunk)
