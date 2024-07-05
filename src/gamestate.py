from assets.constants import *
import pygame as pg


class Gamestate:
    def __init__(self):
        self.white_pieces = []
        self.black_pieces = []
        self.turn = 1

    def draw_board(self, window):
        window.fill(GREEN)
        for col in range(COLUMNS):
            for row in range(col % 2, ROWS, 2):
                pg.draw.rect(window, BEIGE, (row * SQUAREWIDTH, col * SQUAREWIDTH, SQUAREWIDTH, SQUAREWIDTH))

