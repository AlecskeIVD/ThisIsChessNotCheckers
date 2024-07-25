from abc import ABC, abstractmethod
from assets.constants import *


class Piece(ABC):
    @abstractmethod
    def __init__(self, position: (int, int), colour: (int, int, int), value: int):
        self.i, self.j = position
        self.colour = colour
        self.value = value

    @abstractmethod
    def generate_possible_moves(self) -> []:
        """
Generates a list of new Piece-objects that correspond to all possible moves a piece can make and remain on the board
        """
        pass

    def __eq__(self, other):
        if other is None:
            return False
        return self.i == other.i and self.j == other.j and self.colour == other.colour and self.value == other.value

    def __str__(self):
        return f'{value_to_name.get(self.value)} at ({self.i},{self.j})'
