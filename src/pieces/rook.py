from .abstract_piece import Piece
from assets.constants import *


class Rook(Piece):
    def __init__(self, position: (int, int), colour: (int, int, int), has_moved=False):
        super().__init__(position, colour, ROOK)
        self.has_moved = has_moved

    def generate_possible_moves(self):
        return [Rook((n, self.j), self.colour, True) for n in range(8) if n != self.i] +\
               [Rook((self.i, n), self.colour, True) for n in range(8) if n != self.j]
