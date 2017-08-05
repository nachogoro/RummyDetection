import cv2
import numpy as np
import PossibleDigit

class DetectedDigit:
    """
    A class containing information on a detected digit (on its contour,
    estimated value and color)
    """
    def __init__(self, pos_digit, value, color):
        self.intCenterX = pos_digit.intCenterX
        self.intCenterY = pos_digit.intCenterY
        self.intHeight = pos_digit.intBoundingRectHeight
        self.value = value
        self.color = color
