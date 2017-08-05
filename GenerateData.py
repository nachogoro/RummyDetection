import sys
import numpy as np
import cv2
import os


"""
Program to generate the training data for KNN.
It takes one argument: the path to an image containing the characters to be
recognized. It will loop over the characters in the image and ask the user to
classify them. It will then generate two output files which will be used by the
main program to train KNN.

NOTE: This script is not necessary to use the tool, since it is already
distributed with the necessary training data. This script is only provided in
case someone wants to re-train it with their own images.
"""


MIN_CONTOUR_AREA = 100

RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30


def main():
    img_training_numbers = cv2.imread(sys.argv[1])

    if img_training_numbers is None:
        print('Error: image not read from file')
        return

    img_gray = cv2.cvtColor(img_training_numbers, cv2.COLOR_BGR2GRAY)
    img_blurred = cv2.GaussianBlur(img_gray, (5,5), 0)

    img_thresh = cv2.adaptiveThreshold(img_blurred,
                                       255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV,
                                       11,
                                       2)

    # Show threshold image for reference
    cv2.imshow('img_thresh', img_thresh)

    # Find contours on a copy of the image
    img_thresh_copy = img_thresh.copy()

    # Retrieve outermost contours
    _, npa_contours, _ = cv2.findContours(img_thresh_copy,
                                          cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)

    npa_flattened_imgs =  np.empty(
        (0, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))

    int_classifications = []

    # We are interested in digits and jokers, which we represent as a j
    int_valid_chars = [ord('j'), ord('1'), ord('2'), ord('3'), ord('4'),
                       ord('5'), ord('6'), ord('7'), ord('8'), ord('9')]

    for npa_contour in npa_contours:
        if cv2.contourArea(npa_contour) > MIN_CONTOUR_AREA:
            [intX, intY, intW, intH] = cv2.boundingRect(npa_contour)

            cv2.rectangle(img_training_numbers,
                          (intX, intY),
                          (intX+intW,intY+intH),
                          (0, 0, 255),
                          2)

            img_ROI = img_thresh[intY:intY+intH, intX:intX+intW]
            img_ROI_resized = cv2.resize(
                img_ROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))

            # Show image for reference
            cv2.imshow('img_ROI', img_ROI)
            cv2.imshow('img_ROI_resized', img_ROI_resized)
            cv2.imshow('Training numbers', img_training_numbers)

            int_char = cv2.waitKey(0)

            # Exit program if user pressed 'Esc'
            if int_char == 27:
                sys.exit()
            elif int_char in int_valid_chars:
                int_classifications.append(int_char)
                # Flatten image to 1d numpy array so we can write to file later
                npa_flattened_img = img_ROI_resized.reshape(
                    (1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
                npa_flattened_imgs = np.append(
                    npa_flattened_imgs, npa_flattened_img, 0)

    flt_classifications = np.array(int_classifications, np.float32)

    npa_classifications = flt_classifications.reshape(
        (flt_classifications.size, 1))

    print('Training complete!')

    np.savetxt('classifications.txt', npa_classifications)
    np.savetxt('flattened_images.txt', npa_flattened_imgs)

    cv2.destroyAllWindows()

    return


if __name__ == '__main__':
    main()
