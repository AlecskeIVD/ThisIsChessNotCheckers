import pygame as pg
from assets.constants import *
from src.gamestate import Gamestate
from random import randint
from time import sleep


# INITIALISING WINDOW
WINDOW = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")

# Dictionaries for translating pieces to human-readable names
value_to_name = {1: "pawn", 3: "knight", 4: "bishop", 5: "rook", 8: "queen", 9: "king"}
rgb_to_colour = {WHITE: "white", BLACK: "black"}
index_to_column = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
index_to_row = {}
for row in range(8):
    index_to_row[row] = 8-row


def main(version: int = 0):
    run = True
    clock = pg.time.Clock()
    gs = Gamestate(load_images=True)
    selected_piece = None
    gs.draw_board(WINDOW)
    pg.display.update()

    while run:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                print(gs.move)
                if gs.move % 2 == 1:
                    lm = gs.legal_moves(WHITE)
                else:
                    lm = gs.legal_moves(BLACK)
                newmove = lm[randint(0, len(lm) - 1)]
                gs.update(newmove)
                gs.draw_board(WINDOW)
                pg.display.update()
                if gs.white_wins():
                    run = False
                    print("White has won!")
                elif gs.black_wins():
                    run = False
                    print("Black has won")
                elif gs.stalemate():
                    run = False
                    print("Stalemate; no more legal moves")
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                i = pos[1] // SQUAREWIDTH
                j = pos[0] // SQUAREWIDTH
                if selected_piece is None:
                    selected_piece = gs.get_piece(i, j)
                    if selected_piece is not None:
                        print(f"Selected the {rgb_to_colour.get(selected_piece.colour)} "
                              f"{value_to_name[selected_piece.value]} piece at {index_to_column[selected_piece.j]}"
                              f"{index_to_row[selected_piece.i]}")
                else:
                    target_piece = None
                    for piece in selected_piece.generate_possible_moves():
                        if piece.i == i and piece.j == j:
                            target_piece = piece
                    if target_piece is None:
                        selected_piece = None
                    else:
                        print(f"Found the target piece: {rgb_to_colour.get(target_piece.colour)} "
                              f"{value_to_name[target_piece.value]} piece at {index_to_column[target_piece.j]}"
                              f"{index_to_row[target_piece.i]}")
                        if selected_piece.colour == WHITE:
                            target_gs = Gamestate([piece for piece in gs.white_pieces if piece != selected_piece]+[target_piece], gs.black_pieces, gs.move+1)
                            print("Created the target_gs")
                            if gs.is_legal(target_gs):
                                print('target_gs is legal')
                                gs.update(target_gs)
                                print("Gs is updated to target_gs")
                            else:
                                selected_piece = None
                        else:
                            target_gs = Gamestate(gs.white_pieces,
                                [piece for piece in gs.black_pieces if piece != selected_piece] + [target_piece],
                                gs.move + 1)
                            print("Created the target_gs")
                            if gs.is_legal(target_gs):
                                print('target_gs is legal')
                                gs.update(target_gs)
                                print("Gs is updated to target_gs")
                            else:
                                selected_piece = None
                    gs.draw_board(WINDOW)
                    pg.display.update()
                    selected_piece = None
                    print('Checking if black has legal moves')
                    gs.legal_moves(BLACK)
                    print('Checking if white has legal moves')
                    gs.legal_moves(WHITE)
                    print('Checking if white has won')
                    if gs.white_wins():
                        run = False
                        print("White has won!")
                        sleep(3)
                    print('Checking if black has won')
                    if gs.black_wins():
                        run = False
                        print("Black has won")
                        sleep(3)
                    print('Checking if it is a draw')
                    if gs.stalemate():
                        run = False
                        print("Stalemate; no more legal moves")
                        sleep(3)

    pg.quit()


if __name__ == '__main__':
    main()
