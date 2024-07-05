import pygame as pg
from assets.constants import *
from pieces.rook import Rook
from pieces.pawn import Pawn
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.queen import Queen


# INITIALISING WINDOW
WINDOW = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")


def main(version: int = 0):
    run = True
    clock = pg.time.Clock()

    while run:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

            if event.type == pg.MOUSEBUTTONDOWN:
                pass

    pg.quit()


if __name__ == '__main__':
    main()
