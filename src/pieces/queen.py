from .abstract_piece import *
from assets.constants import *


class Queen(Piece):
    def __init__(self, position: (int, int), colour: (int, int, int)):
        super().__init__(position, colour, QUEEN)

    def generate_possible_moves(self):
        output = [Queen((n, self.j), self.colour) for n in range(8) if n != self.i] +\
               [Queen((self.i, n), self.colour) for n in range(8) if n != self.j]

        # TO BOTTOM RIGHT
        for i in range(1, 8):
            if not (self.i + i < 8 and self.j + i < 8):
                break
            output.append(Queen((self.i + i, self.j + i), self.colour))

        # TO BOTTOM LEFT
        for i in range(1, 8):
            if not (self.i + i < 8 and self.j - i >= 0):
                break
            output.append(Queen((self.i + i, self.j - i), self.colour))

        # TO TOP RIGHT
        for i in range(1, 8):
            if not (self.i - i >= 0 and self.j + i < 8):
                break
            output.append(Queen((self.i - i, self.j + i), self.colour))

        # TO TOP LEFT
        for i in range(1, 8):
            if not (self.i - i >= 0 and self.j - i >= 0):
                break
            output.append(Queen((self.i - i, self.j - i), self.colour))

        return output
