from abc import ABC, abstractmethod


class Piece(ABC):
    @abstractmethod
    def __init__(self, position: (int, int), colour: (int, int, int), value: int):
        self.i, self.j = position
        self.colour = colour
        self.value = value

    def __eq__(self, other):
        return self.i == other.i and self.j == other.j and self.colour == other.colour and self.value == other.value
