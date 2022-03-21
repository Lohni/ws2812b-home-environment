import neopixel
import machine

#
# 0  -  1  -  2
# |     |     |
# 3  -  4  -  5
# |     |     |
# 6  -  7  -  8
# |     |     |
# 9  -  10 -  11
# |     |     |
# 12 -  13 -  14
#
import time

import uasyncio

font = {
    "A": [1, 3, 5, 6, 7, 8, 9, 11, 12, 14],
    "B": [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    "C": [1, 2, 3, 6, 9, 13, 14],
    "D": [0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14],
    "E": [0, 1, 2, 3, 6, 7, 8, 9, 12, 13, 14],
    "F": [0, 1, 2, 3, 6, 7, 8, 9, 12],
    "G": [0, 1, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    "H": [0, 2, 3, 5, 6, 7, 8, 9, 11, 12, 14],
    "I": [0, 1, 2, 4, 7, 10, 12, 13, 14],
    "J": [2, 5, 8, 9, 11, 12, 13, 14],
    "K": [0, 2, 3, 4, 6, 9, 10, 12, 14],
    "L": [0, 3, 6, 9, 12, 13, 14],
    "M": [0, 2, 3, 4, 5, 6, 8, 9, 11, 12, 14],
    "N": [0, 1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14],
    "O": [0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14],
    "P": [0, 1, 2, 3, 5, 6, 7, 8, 9, 12],
    "Q": [0, 1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14],
    "R": [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 14],
    "S": [1, 2, 3, 7, 11, 12, 13],
    "T": [0, 1, 2, 4, 7, 10, 13],
    "U": [0, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14],
    "V": [0, 2, 3, 5, 6, 8, 9, 11, 13],
    "W": [0, 2, 3, 5, 6, 8, 9, 10, 11, 12, 14],
    "X": [0, 2, 3, 5, 7, 9, 11, 12, 14],
    "Y": [0, 2, 3, 5, 7, 10, 13],
    "Z": [0, 1, 2, 5, 7, 8, 9, 12, 13, 14],
    "1": [2, 5, 8, 11, 14],
    "2": [0, 1, 2, 5, 6, 7, 8, 9, 12, 13, 14],
    "3": [0, 1, 2, 5, 6, 7, 8, 11, 12, 13, 14],
    "4": [0, 3, 5, 6, 7, 8, 11, 14],
    "5": [0, 1, 2, 3, 6, 7, 8, 11, 12, 13, 14],
    "6": [0, 1, 2, 3, 6, 7, 8, 9, 11, 12, 13, 14],
    "7": [0, 1, 2, 3, 5, 8, 11, 14],
    "8": [0, 1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14],
    "9": [0, 1, 2, 3, 5, 6, 7, 8, 11, 12, 13, 14],
    "0": [0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14],
    "°": [1, 3, 5, 7],
    ".": [13],
    "%": [0, 5, 7, 9, 14]
}


class LEDUtils:
    def __init__(self, led_count: int):
        self.np = neopixel.NeoPixel(machine.Pin(2), led_count)
        self.rotation = 1

    async def writeStringToMatrix(self, s: str):
        self.np.fill((0, 0, 0))
        for pos, char in enumerate(s):
            seperator = True
            if s == '.':
                seperator = False

            position = font.get(char)
            self.writeCharToMatrix(position, pos, seperator)
        self.np.write()

    def writeCharToMatrix(self, char: [], char_position, seperator: bool):
        # width of matrix : 32, char width : 3 + 1 padding
        # -> max. 8 fonts on matrix
        matrixWidth = 32
        startIndex = char_position * 3

        if seperator:
            # 1 led padding between letters
            startIndex += char_position

        if self.rotation == 0:
            for pos in char:
                if pos < 3:
                    self.np[startIndex + pos] = (10, 5, 6)
                elif pos < 6:
                    self.np[-startIndex + (matrixWidth * 2 - 1) + (3 - pos)] = (10, 5, 6)
                elif pos < 9:
                    self.np[startIndex + (matrixWidth * 2) + (6 - pos) * -1] = (10, 5, 6)
                elif pos < 12:
                    self.np[-startIndex + (matrixWidth * 4 - 1) + (9 - pos)] = (10, 5, 6)
                else:
                    self.np[startIndex + (matrixWidth * 4) + (12 - pos) * -1] = (10, 5, 6)
        else:
            startIndex = 224 + startIndex
            row_pos = matrixWidth - (256 - startIndex)
            for pos in char:
                if pos < 3:
                    self.np[startIndex + pos] = (10, 5, 6)
                elif pos < 6:
                    self.np[startIndex - (row_pos * 2 - 1) - (pos - 3) - 2] = (10, 5, 6)
                elif pos < 9:
                    self.np[startIndex - matrixWidth*2 + (pos - 6)] = (10, 5, 6)
                elif pos < 12:
                    self.np[startIndex - (row_pos + matrixWidth) * 2 - 1 - (pos - 9)] = (10, 5, 6)
                else:
                    self.np[startIndex - matrixWidth * 4 + (pos - 12)] = (10, 5, 6)

        return

    async def runningText(self, s, padding):
        self.np.fill((0, 0, 0))
        matrixWidth = 32
        for char_position, letter in enumerate(s):
            char = font.get(letter)

            startIndex = char_position * 3 + char_position + padding
            for pos in char:
                if pos < 3:
                    index = startIndex + pos
                    if index >= matrixWidth:
                        index = index - matrixWidth

                elif pos < 6:
                    index = -startIndex + (matrixWidth * 2 - 1) + (3 - pos)
                    if index < matrixWidth:
                        index = (matrixWidth * 2 - 1) - (matrixWidth - 1 - index)

                elif pos < 9:
                    index = startIndex + (matrixWidth * 2) + (6 - pos) * -1
                    if index >= matrixWidth * 3:
                        index = matrixWidth * 2 + (index - matrixWidth * 3)

                elif pos < 12:
                    index = -startIndex + (matrixWidth * 4 - 1) + (9 - pos)
                    if index < matrixWidth * 3:
                        index = (matrixWidth * 4 - 1) - (matrixWidth * 3 - 1 - index)

                else:
                    index = startIndex + (matrixWidth * 4) + (12 - pos) * -1
                    if index >= matrixWidth * 5:
                        index = matrixWidth * 4 + (index - matrixWidth * 5)

                self.np[index] = (10, 10, 10)