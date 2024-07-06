from assets.constants import *
import pygame as pg
from pieces.rook import Rook
from pieces.pawn import Pawn
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.queen import Queen


class Gamestate:
    def __init__(self):
        white_pieces = [Rook(BP_WLROOK, WHITE), Rook(BP_WRROOK, WHITE), Knight(BP_WLKNIGHT, WHITE),
                        Knight(BP_WRKNIGHT, WHITE), Bishop(BP_WLBISHOP, WHITE), Bishop(BP_WRBISHOP, WHITE),
                        Queen(BP_WQUEEN, WHITE), King(BP_WKING, WHITE)]
        for i in range(COLUMNS):
            white_pieces.append(Pawn((ROWS - 2, i), WHITE))
        self.white_pieces = white_pieces

        black_pieces = [Rook(BP_BLROOK, BLACK), Rook(BP_BRROOK, BLACK), Knight(BP_BLKNIGHT, BLACK),
                        Knight(BP_BRKNIGHT, BLACK), Bishop(BP_BLBISHOP, BLACK), Bishop(BP_BRBISHOP, BLACK),
                        Queen(BP_BQUEEN, BLACK), King(BP_BKING, BLACK)]
        for i in range(COLUMNS):
            black_pieces.append(Pawn((1, i), BLACK))
        self.black_pieces = black_pieces

        # LOAD IMAGES
        pieces = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
        self.images = {}
        for piece in pieces:
            self.images[f"{piece}_black"] = pg.transform.scale(pg.image.load("assets/images/" + piece + "_black.png"),
                                                               (SQUAREWIDTH, SQUAREWIDTH))
            # white_image = convert_black_to_white(self.images.get(f"{piece}_black"))
            # pg.image.save(white_image, "assets/images/" + piece + "_white.png")
            self.images[f"{piece}_white"] = pg.transform.scale(pg.image.load("assets/images/" + piece + "_white.png"),
                                                               (SQUAREWIDTH, SQUAREWIDTH))
        self.move = 1

    def draw_board(self, window):
        # Draw Board
        window.fill(GREEN)
        for col in range(COLUMNS):
            for row in range(col % 2, ROWS, 2):
                pg.draw.rect(window, BEIGE, (row * SQUAREWIDTH, col * SQUAREWIDTH, SQUAREWIDTH, SQUAREWIDTH))

        value_to_name = {1: "pawn", 3: "knight", 4: "bishop", 5: "rook", 8: "queen", 9: "king"}
        for piece in self.white_pieces:
            window.blit(self.images[value_to_name.get(piece.value) + "_white"],
                        (piece.j * SQUAREWIDTH, piece.i * SQUAREWIDTH))

        for piece in self.black_pieces:
            window.blit(self.images[value_to_name.get(piece.value) + "_black"],
                        (piece.j * SQUAREWIDTH, piece.i * SQUAREWIDTH))


def convert_black_to_white(image):
    white_image = image.copy()
    width, height = white_image.get_size()
    for x in range(width):
        for y in range(height):
            r, g, b, a = white_image.get_at((x, y))
            # Invert the colors to create a white piece
            if r + g + b < 50:
                r, g, b = WHITE
                white_image.set_at((x, y), (r, g, b, a))
    return white_image
