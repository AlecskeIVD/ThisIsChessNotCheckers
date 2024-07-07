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
from random import randint


# INITIALISING WINDOW
WINDOW = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")


def main(version: int = 0):
    run = True
    clock = pg.time.Clock()
    gs = Gamestate([King((0, 0), WHITE)], [King((5, 5), BLACK)])
    selected_piece = None
    gs.draw_board(WINDOW)
    pg.display.update()

    while run:
        clock.tick(FPS)
        if gs.move % 2 == 1:
            lm = gs.legal_moves(WHITE)
        else:
            lm = gs.legal_moves(BLACK)
        newmove = lm[randint(0, len(lm)-1)]
        gs.update(newmove)
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
                    generated_moves = selected_piece.generate_possible_moves()
                    for move in generated_moves:
                        pg.draw.circle(WINDOW, BLACK, ((move.j + 0.5)*SQUAREWIDTH, (move.i + 0.5)*SQUAREWIDTH), 0.1*SQUAREWIDTH)
                        pg.display.update()
                else:
                    selected_piece.i = i
                    selected_piece.j = j
                    gs.draw_board(WINDOW)
                    pg.display.update()
                    selected_piece = None
                    print(gs.king_under_attack(WHITE))
                    gs.move += 1

    pg.quit()


if __name__ == '__main__':
    main()
