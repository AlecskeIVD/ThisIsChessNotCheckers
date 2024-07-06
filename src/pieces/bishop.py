from .abstract_piece import *
from assets.constants import *


class Bishop(Piece):
    def __init__(self, position: (int, int), colour: (int, int, int)):
        super().__init__(position, colour, BISHOP)

    def generate_possible_moves(self):
        output = []

        # TO BOTTOM RIGHT
        for i in range(1, 8):
            if not (self.i + i < 8 and self.j + i < 8):
                break
            output.append(Bishop((self.i + i, self.j + i), self.colour))

        # TO BOTTOM LEFT
        for i in range(1, 8):
            if not (self.i + i < 8 and self.j - i >= 0):
                break
            output.append(Bishop((self.i - i, self.j - i), self.colour))

        # TO TOP RIGHT
        for i in range(1, 8):
            if not (self.i - i >= 0 and self.j + i < 8):
                break
            output.append(Bishop((self.i - i, self.j - i), self.colour))

        # TO TOP LEFT
        for i in range(1, 8):
            if not (self.i - i >= 0 and self.j - i >= 0):
                break
            output.append(Bishop((self.i - i, self.j - i), self.colour))
        return output

