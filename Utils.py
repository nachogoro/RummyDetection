import cv2
import numpy as np
import PossibleDigit
from DetectedDigit import DetectedDigit

# Possible colors to find in a tile (BGR!)
TILE_COLORS = {'ORANGE': ([11, 191, 101], [19, 255, 255]),
               'BLACK': ([0, 0, 0], [70, 255, 45]),
               'PINK': ([173, 125, 65], [185, 240, 235]),
               'BLUE': ([83, 81, 32], [119, 210, 151]),
               }


def group_by_height(list_of_possible_digits):
    """
    It takes a list of PossibleDigit's and groups them by height. Since each
    group of heights has some tolerance, it is possible for a PossibleDigit to
    be in two groups at the same time.
    """
    height_digits = {}

    for digit in list_of_possible_digits:
        margins = (digit.intBoundingRectHeight*0.78,
                   digit.intBoundingRectHeight*1.22)
        appended_to_group = False
        for height, items in height_digits.items():
            if margins[0] < height < margins[1]:
                items.append(digit)
                appended_to_group = True

        if not appended_to_group:
            height_digits[digit.intBoundingRectHeight] = [digit]

    return height_digits


def _get_digit_color(image):
    """
    Returns the name of the color of the digit.
    """
    color = None
    maximum = 0
    for name, (lower, upper) in TILE_COLORS.items():
        lower = np.array(lower, dtype='uint8')
        upper = np.array(upper, dtype='uint8')

        # Find the colors within the specified boundaries and apply the mask
        mask = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV),lower,upper)
        non_zero = np.count_nonzero(mask)
        if non_zero > maximum:
            color = name
            maximum = non_zero

    return color


def detect_digit_color(digits, image):
    """
    Given a list of pairs (PossibleDigit, value) it returns a list of
    DetectedDigit's (i.e. it finds the color of each tile)
    """
    result = []
    for pos_digit, value in digits:
        roi = crop_possible_digit_from_image(pos_digit, image)
        color = _get_digit_color(roi)
        result.append(DetectedDigit(pos_digit, value, color))
    return result


def crop_possible_digit_from_image(possible_digit, image):
    """
    Crops the contour of possible_digit from image and returns it.
    """
    y_min = possible_digit.intBoundingRectY
    y_max = y_min + possible_digit.intBoundingRectHeight
    x_min = possible_digit.intBoundingRectX
    x_max = x_min + possible_digit.intBoundingRectWidth
    return image[y_min : y_max, x_min : x_max]
