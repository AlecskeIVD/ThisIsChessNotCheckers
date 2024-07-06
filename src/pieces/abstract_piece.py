from abc import ABC, abstractmethod


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
        return self.i == other.i and self.j == other.j and self.colour == other.colour and self.value == other.value
