from .abstract_piece import *
from assets.constants import *


class Bishop(Piece):
    def __init__(self, position: (int, int), colour: (int, int, int)):
        super().__init__(position, colour, BISHOP)