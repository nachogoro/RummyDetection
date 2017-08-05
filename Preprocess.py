import cv2
import numpy as np

# module level variables
GAUSSIAN_SMOOTH_FILTER_SIZE = (5, 5)
ADAPTIVE_THRESH_BLOCK_SIZE = 19
ADAPTIVE_THRESH_WEIGHT = 9


def preprocess(img_original):
    img_gray = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)

    img_max_contrast_gray = maximize_contrast(img_gray)

    height, width = img_gray.shape

    img_blur = np.zeros((height, width, 1), np.uint8)

    img_blur = cv2.GaussianBlur(img_max_contrast_gray,
                                GAUSSIAN_SMOOTH_FILTER_SIZE,
                                0)

    img_thresh = cv2.adaptiveThreshold(
        img_blur,
        255.0,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        ADAPTIVE_THRESH_BLOCK_SIZE,
        ADAPTIVE_THRESH_WEIGHT)

    # Orange numbers fail to be recognized in the thresholded image, so we want
    # to apply a mask which keeps only them
    converted = cv2.cvtColor(img_original, cv2.COLOR_BGR2HSV)

    # Define the list of boundaries
    boundaries = [([11, 191, 101], [19, 255, 255]),     #ORANGE
                  ([0, 0, 0], [70, 255, 45]),           # BLACK
                  ([173, 125, 65], [185, 240, 235]),    # PINK
                  ([83, 81, 32], [119, 210, 151]),      # BLUE
                  ]

    for (lower, upper) in boundaries:
        lower = np.array(lower, dtype='uint8')
        upper = np.array(upper, dtype='uint8')

        # Find the colors within the specified boundaries and apply the mask
        mask = cv2.inRange(converted, lower, upper)
        img_thresh = cv2.bitwise_or(img_thresh, mask)

    return img_gray, img_thresh


def maximize_contrast(img_gray):
    height, width = img_gray.shape

    img_top_hat = np.zeros((height, width, 1), np.uint8)
    img_black_hat = np.zeros((height, width, 1), np.uint8)

    structuring_elem = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    img_top_hat = cv2.morphologyEx(
        img_gray, cv2.MORPH_TOPHAT, structuring_elem)

    img_black_hat = cv2.morphologyEx(
        img_gray, cv2.MORPH_BLACKHAT, structuring_elem)

    img_gray_plus_top_hat = cv2.add(img_gray, img_top_hat)

    img_gray_plus_top_hat_minus_black_hat = cv2.subtract(
        img_gray_plus_top_hat, img_black_hat)

    return img_gray_plus_top_hat_minus_black_hat
