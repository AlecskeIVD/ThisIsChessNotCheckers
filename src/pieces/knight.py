from .abstract_piece import *
from assets.constants import *


class Knight(Piece):
    def __init__(self, position: (int, int), colour: (int, int, int)):
        super().__init__(position, colour, KNIGHT)

    def generate_possible_moves(self):
        moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        output = []
        for move in moves:
            new_i, new_j = self.i + move[0], self.j+move[1]
            if (0 <= new_i < 8) and (0 <= new_j < 8):
                output.append(Knight((new_i, new_j), self.colour))
        return output
