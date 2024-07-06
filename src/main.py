import pygame as pg
import pygame.mouse

from assets.constants import *
from pieces.rook import Rook
from pieces.pawn import Pawn
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.queen import Queen
from src.gamestate import Gamestate


# INITIALISING WINDOW
WINDOW = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")


def main(version: int = 0):
    run = True
    clock = pg.time.Clock()
    gs = Gamestate()
    selected_piece = None
    print(Pawn((6, 1), BLACK).generate_possible_moves())

    while run:
        clock.tick(FPS)

        gs.draw_board(WINDOW)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                i = pos[1] // SQUAREWIDTH
                j = pos[0] // SQUAREWIDTH
                if not selected_piece:
                    selected_piece = gs.get_piece(i, j)
                else:
                    selected_piece.i = i
                    selected_piece.j = j
                    selected_piece = None
                    gs.move += 1

    pg.quit()


if __name__ == '__main__':
    main()
