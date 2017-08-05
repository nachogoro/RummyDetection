import cv2
import numpy as np
import Main

import Preprocess
import DetectDigits
from DetectedDigit import DetectedDigit
from Tile import Tile
from utils import crop_possible_digit_from_image, TILE_COLORS
import utils


def _group_digits_in_tiles(detected_digits):
    """
    Given a list of DetectedDigit's, it returns a list of Tile's
    (i.e. it goes from single digits to potentially multi-digit tiles).
    """
    tiles = []
    for color in TILE_COLORS.keys():
        of_color = [e for e in detected_digits if e.color == color]

        to_remove = []

        for digit in of_color:
            if digit.value == 'j' or int(digit.value) >= 4:
                tiles.append(Tile(digit))
                to_remove.append(digit)

        of_color = [e for e in of_color if e not in to_remove]
        # of_color now contains only 0s, 1s, 2s and 3s
        ones = [e for e in of_color if int(e.value) == 1]
        of_color = [e for e in of_color if e not in ones]
        # of_color now contains only 0s, 2s and 3s
        unmatched_ones = []
        for one in ones:
            o_ctrX = one.intCenterX
            o_ctrY = one.intCenterY
            o_height = one.intHeight

            match = None
            for candidate in of_color:
                c_ctrX = candidate.intCenterX
                c_ctrY = candidate.intCenterY

                if (abs(o_ctrY - c_ctrY) < o_height
                        and 0 < c_ctrX - o_ctrX < o_height):
                    tiles.append(Tile(one, candidate))

                    match = candidate
                    break

            of_color = [e for e in of_color if e is not match]

            if match is None:
                # The '1' is not part of a multi-digit tile, so just add it
                unmatched_ones.append(one)

        # of_color contains the 2s and 3s which are not part of multi-digit
        # tile
        for remaining in of_color:
            tiles.append(Tile(remaining))

            if remaining.value == '0':
                print('ERROR: A 0 digit was not grouped to any 1!')

        # Finally check if any one matches any other one
        added = []
        for one in unmatched_ones:
            if one in added:
                continue

            o_ctrX = one.intCenterX
            o_ctrY = one.intCenterY
            o_height = one.intHeight

            for candidate in unmatched_ones:
                if one is candidate or candidate in added:
                    continue

                c_ctrX = candidate.intCenterX
                c_ctrY = candidate.intCenterY

                if (abs(o_ctrY - c_ctrY) < o_height
                        and 0 < c_ctrX - o_ctrX < o_height):
                    tiles.append(Tile(one, candidate))

                    added.append(one)
                    added.append(candidate)
                    break

        for one in unmatched_ones:
            if one not in added:
                tiles.append(Tile(one))

    return tiles


def detect_tiles_in_image(image, canon_img_dir):
    """
    It detects all the tiles in an image and returns them as a list of Tile's.
    canon_img_dir is the directory containing the images of each digit
    (necessary to discard unwanted KNN matches)
    """

    height, width, _ = image.shape

    cv2.destroyAllWindows()

    if Main.show_steps:
        cv2.imshow('0', image)

    img_grayscale, img_thresh = Preprocess.preprocess(image)

    if Main.show_steps:
        cv2.imshow('1a', img_grayscale)
        cv2.imshow('1b', img_thresh)
        cv2.waitKey(0)

    # Find all possible digits in the scene.
    # This function first finds all contours, then only includes contours that
    # could be digits (without comparison to other digits yet)
    list_of_possible_digits = DetectDigits.find_possible_digits(img_thresh)

    if Main.show_steps:
        img_contours = np.zeros((height, width, 3), np.uint8)

        contours = []

        for possible_digit in list_of_possible_digits:
            contours.append(possible_digit.contour)

        cv2.drawContours(img_contours, contours, -1, Main.SCALAR_WHITE)
        cv2.imshow('2b', img_contours)
        cv2.waitKey(0)

    # All digits should be roughly of the same height. Group contours by
    # height.
    possible_digits_by_height = utils.group_by_height(list_of_possible_digits)

    for k in possible_digits_by_height:
        possible_digits_by_height[k] = (
            DetectDigits.remove_inner_overlapping_digits(
                possible_digits_by_height[k]))

    if Main.show_steps:
        for k, v in possible_digits_by_height.items():
            img_contours = np.zeros((height, width, 3), np.uint8)

            contours = []

            for possible_digit in v:
                contours.append(possible_digit.contour)

            cv2.drawContours(img_contours, contours, - 1, Main.SCALAR_WHITE)
            cv2.imshow('2c', img_contours)
            cv2.waitKey(0)


    # We sort the different groups by number of elements because we assume
    # we have identified more digits than non-digits.
    sets_to_try = [v for k,v in possible_digits_by_height.items()]
    sets_to_try.sort(key=len, reverse=True)

    for chosen_set in sets_to_try:
        recognized_digits = DetectDigits.recognize_digits(img_thresh,
                                                          chosen_set)
        # KNN chooses the nearest neighbour, which means it won't be able to
        # filter out contours which are actually very far away from their
        # closest neighbour. We now compare each contour with the digit it
        # supposedly represents, and discard it if they are too far apart.
        filtered_digits = DetectDigits.filter_detected_digits(
            recognized_digits, img_thresh, canon_img_dir)

        # We assume we are good to go if we have discarded either less than 3
        # or less than 25% of the original contours
        if ((len(recognized_digits) - len(filtered_digits)) < 3
                or len(filtered_digits) > 0.75 * len(recognized_digits)):
            recognized_digits = filtered_digits
            break

    # Get the color of the detected digits as a list of DetectedDigit's
    detected_digits = utils.detect_digit_color(recognized_digits, image)

    # Go from individual digits to tiles
    return _group_digits_in_tiles(detected_digits)
