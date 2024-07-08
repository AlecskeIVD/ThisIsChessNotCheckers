from .abstract_piece import *
from assets.constants import *


class King(Piece):
    def __init__(self, position: (int, int), colour: (int, int, int), has_moved=False):
        super().__init__(position, colour, KING)
        self.has_moved = has_moved

    def generate_possible_moves(self):
        output = [King((self.i+i, self.j+j), self.colour, True) for i in range(-1, 2, 1)
                  for j in range(-1, 2, 1) if 0 <= self.i+i < 8 and 0 <= self.j+j < 8 and not (i == j == 0)]

        # Castling
        if not self.has_moved:
            output += [King((self.i, self.j+2), self.colour, True), King((self.i, self.j-2), self.colour, True)]
        return output
