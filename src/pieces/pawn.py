from .abstract_piece import *
from assets.constants import *
from .queen import Queen


class Pawn(Piece):
    def __init__(self, position: (int, int), colour: (int, int, int)):
        super().__init__(position, colour, PAWN)
        self.en_passantable = False

    def generate_possible_moves(self):
        output = []
        if self.colour == BLACK:
            if self.i == 1:
                output.append(Pawn((3, self.j), self.colour))
            if self.i == 6:
                output += [Queen((7, self.j+n), self.colour) for n in range(-1, 2) if 0 <= self.j+n < 8]
            else:
                output += [Pawn((self.i+1, self.j + n), self.colour) for n in range(-1, 2) if 0 <= self.j + n < 8]

        else:
            if self.i == 6:
                output.append(Pawn((4, self.j), self.colour))
            if self.i == 1:
                output += [Queen((0, self.j + n), self.colour) for n in range(-1, 2) if 0 <= self.j + n < 8]
            else:
                output += [Pawn((self.i - 1, self.j + n), self.colour) for n in range(-1, 2) if 0 <= self.j + n < 8]
        return output
