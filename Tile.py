import DetectedDigit

class Tile:
    """
    A class containing information on a tile
    """
    def __init__(self, digit1, digit2=None):
        self.intHeight = digit1.intHeight
        self.intCenterY = digit1.intCenterY
        self.color = digit1.color

        if not digit2:
            self.intCenterX = digit1.intCenterX
            self.value = digit1.value
        else:
            self.intCenterX = int((digit1.intCenterX + digit2.intCenterX) / 2)
            self.value = str(int(digit1.value)*10 + int(digit2.value))
