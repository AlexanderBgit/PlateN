import cv2
import numpy as np


def resize_img(img, target_height=720):
    """
    # зменшення зображення по висоті 720
    """
    # Отримання висоти та ширини вихідного зображення
    height, width = img.shape[:2]
    if height <= target_height:
        return img
    # Розрахунок пропорційної ширини
    target_width = int(width * (target_height / height))
    # Зменшення розміру зображення до нових розмірів
    resized_img = cv2.resize(img, (target_width, target_height))
    return resized_img


def extract_plate(img, plate_cascade, text=""):
    """
    # Визначає та виконує розмиття на номерних знаках
    """
    # Завантажує дані, необхідні для виявлення номерних знаків, з каскадного класифікатора.
    # plate_cascade = cv2.CascadeClassifier(full_path_cascad)
    # plate_cascade = cv2.CascadeClassifier('D:\Python\github\PlateN\DS\models\haarcascade_russian_plate_number.xml')

    plate_img = img.copy()
    roi = img.copy()
    plate = None
    # Виявляє номерні знаки та повертає координати та розміри контурів виявлених номерних знаків.
    plate_rect = plate_cascade.detectMultiScale(
        plate_img, scaleFactor=1.05, minNeighbors=8
    )

    width_max = 0  # використовується для сортування за шириною
    plate_max = None
    x_max = 0
    y_max = 0

    for x, y, w, h in plate_rect:
        # виконує пропорційне зміщення пікселів
        a, b = (int(0.1 * h), int(0.1 * w))
        aa, bb = (int(0.1 * h), int(0.1 * w))

        if h > 75:  # пропускає розбиття за шириною високоякісного зображення
            b = 0
            bb = 0

        plate = roi[y + a : y + h - aa, x + b : x + w - bb, :]

        if width_max < w:
            plate_max = plate
            width_max = w
            x_max = x
            y_max = y

        # представлення виявлених контурів за допомогою малювання прямокутників навколо країв:
        cv2.rectangle(plate_img, (x + 2, y), (x + w - 3, y + h - 5), (51, 224, 172), 3)
    if text != "":
        h = plate_max.shape[0]
        plate_img = cv2.putText(
            plate_img,
            text,
            (x_max, y_max - h // 3),
            cv2.FONT_HERSHEY_COMPLEX_SMALL,
            1.5,
            (51, 224, 172),
            2,
            cv2.LINE_AA,
        )

    return plate_img, plate_max


def find_contours(dimensions, img, debug=False):
    """
    Відповідність контурів номерному або символьному шаблону
    """
    i_width_threshold = 6

    # Знайдіть всі контури на зображенні
    cntrs, _ = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Отримайте потенційні розміри
    lower_width = dimensions[0]
    upper_width = dimensions[1]
    lower_height = dimensions[2]
    upper_height = dimensions[3]

    # Перевірте найбільші 16 контурів на номерний або символьний шаблон
    cntrs = sorted(cntrs, key=cv2.contourArea, reverse=True)[:16]

    # бінарне зображення номерного знака на вхід: щоб перетворити img.shape(h,w) на img.shape(h,w,3)
    ii = np.dstack([img] * 3)

    x_cntr_list = []
    target_contours = []
    img_res = []
    for cntr in cntrs:
        # виявлення контуру на бінарному зображенні і повернення координат прямокутника, який його оточує
        intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)

        # перевірка розмірів контуру для фільтрації символів за розміром контуру
        if (
            intWidth >= i_width_threshold
            and intWidth < upper_width
            and intHeight > lower_height
            and intHeight < upper_height
        ):
            x_cntr_list.append(
                intX
            )  # stores the x coordinate of the character's contour, to used later for indexing the contours

            char_copy = np.zeros((44, 24))
            # видобуття кожного символу, використовуючи координати прямокутника, що його оточує.
            char = img[intY : intY + intHeight, intX : intX + intWidth]

            if intWidth >= i_width_threshold and intWidth < lower_width:
                i_char = cv2.resize(
                    char, (intWidth, 42), interpolation=cv2.INTER_LINEAR_EXACT
                )

                char = np.full((42, 22), 255, dtype=np.uint8)
                begin = int((22 - intWidth) / 2)  # center alignment
                char[:, begin : begin + intWidth] = i_char[:, :]
            else:
                char = cv2.resize(char, (22, 42), interpolation=cv2.INTER_LINEAR_EXACT)

            cv2.rectangle(
                ii, (intX, intY), (intWidth + intX, intY + intHeight), (50, 21, 200), 2
            )
            # plt.imshow(ii, cmap='gray')

            # Make result formatted for classification: invert colors
            char = cv2.subtract(255, char)

            # Resize the image to 24x44 with black border
            char_copy[1:43, 1:23] = char
            char_copy[0:1, :] = 0
            char_copy[:, 0:1] = 0
            char_copy[43:44, :] = 0
            char_copy[:, 23:24] = 0

            img_res.append(
                char_copy
            )  # List that stores the character's binary image (unsorted)
            if len(img_res) >= 10:
                break

    # Return characters on ascending order with respect to the x-coordinate (most-left character first)
    # if debug:
    #     plt.show()
    # arbitrary function that stores sorted list of character indeces
    indices = sorted(range(len(x_cntr_list)), key=lambda k: x_cntr_list[k])
    img_res_copy = []
    for idx in indices:
        img_res_copy.append(
            img_res[idx]
        )  # stores character images according to their index
    img_res = np.array(img_res_copy)

    return img_res


def segment_to_contours(image, debug: bool = False):
    """
    Find characters in the resulting images
    """
    new_height = 75  # set fixed height
    # print("original plate[w,h]:", image.shape[1], image.shape[0], "new_shape:333,", new_height)

    # Preprocess cropped license plate image
    img_lp = cv2.resize(image, (333, new_height), interpolation=cv2.INTER_LINEAR_EXACT)

    img_gray_lp = cv2.cvtColor(img_lp, cv2.COLOR_BGR2GRAY)
    _, img_binary_lp = cv2.threshold(
        img_gray_lp, 112, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    LP_WIDTH = img_binary_lp.shape[1]
    LP_HEIGHT = img_binary_lp.shape[0]

    # Make borders white
    img_binary_lp[0:3, :] = 255
    img_binary_lp[:, 0:3] = 255
    img_binary_lp[new_height - 3 : new_height, :] = 255
    img_binary_lp[:, 330:333] = 255

    # Estimations of character contours sizes of cropped license plates
    dimensions = [LP_WIDTH / 24, LP_WIDTH / 8, LP_HEIGHT / 3, 2 * LP_HEIGHT / 3]
    # if debug:
    #     plt.imshow(img_binary_lp, cmap='gray')
    #     plt.title("original plate contour (binary)")
    #     plt.show()

    # Get contours within cropped license plate
    char_list = find_contours(dimensions, img_binary_lp)
    return char_list


def fix_dimension(img):
    new_img = np.zeros((28, 28, 3))
    for i in range(3):
        new_img[:, :, i] = img
    return new_img
