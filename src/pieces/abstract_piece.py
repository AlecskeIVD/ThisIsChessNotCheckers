from abc import ABC, abstractmethod


class Piece(ABC):
    @abstractmethod
    def __init__(self, position: (int, int), colour: (int, int, int), value: int):
        self.x, self.y = position
        self.colour = colour
        self.value = value
