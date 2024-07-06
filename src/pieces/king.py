from .abstract_piece import *
from assets.constants import *


class King(Piece):
    def __init__(self, position: (int, int), colour: (int, int, int)):
        super().__init__(position, colour, KING)

    def generate_possible_moves(self):
        return [King((self.i+i, self.j+j), self.colour) for i in range(-1, 2, 1)
                for j in range(-1, 2, 1) if 0 <= self.i+i < 8 and 0 <= self.j+j < 8 and not (i == j == 0)]
