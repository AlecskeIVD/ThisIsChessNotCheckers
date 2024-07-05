from .abstract_piece import Piece
from assets.constants import *


class Rook(Piece):
    def __init__(self, position: (int, int), colour: (int, int, int)):
        super().__init__(position, colour, ROOK)