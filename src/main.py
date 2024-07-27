import pygame as pg
from assets.constants import *
from src.Openings.openingtree import Tree
from src.gamestate import Gamestate
from time import sleep, time
# INITIALISING WINDOW
from src.pieces.bishop import Bishop
from src.pieces.king import King
from src.pieces.knight import Knight
from src.pieces.pawn import Pawn
from src.pieces.queen import Queen
from src.pieces.rook import Rook

WINDOW = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")

# Dictionaries for translating pieces to human-readable names
rgb_to_colour = {WHITE: "white", BLACK: "black"}
index_to_column = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
index_to_row = {}
for row in range(8):
    index_to_row[row] = 8 - row


def main(version: int = 0):
    run = True
    clock = pg.time.Clock()
    white_pieces = [Rook(BP_WLROOK, WHITE), Rook(BP_WRROOK, WHITE), Knight(BP_WLKNIGHT, WHITE),
                    Bishop(BP_WRBISHOP, WHITE), Bishop((5, 7), WHITE),
                    Queen(BP_WQUEEN, WHITE), King(BP_WKING, WHITE)]
    for i in range(COLUMNS):
        if i != 3 and i != 5:
            white_pieces.append(Pawn((ROWS - 2, i), WHITE))
    black_pieces = [Rook(BP_BLROOK, BLACK), Rook(BP_BRROOK, BLACK),
                    Knight((5, 4), BLACK), Bishop(BP_BLBISHOP, BLACK), Bishop(BP_BRBISHOP, BLACK),
                    Queen(BP_BQUEEN, BLACK), King(BP_BKING, BLACK)]
    for i in range(COLUMNS-2):
        black_pieces.append(Pawn((1, i), BLACK))
    gs = Gamestate(white_pieces, black_pieces,move=31, load_images=True)
    openingTree = Tree()
    gs.computer_makes_move(7, openingTree)
    selected_piece = None
    gs.draw_board(WINDOW)
    pg.display.update()
    while run:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                start = time()
                gs.computer_makes_move(version, openingTree)
                print(time()-start)
                gs.draw_board(WINDOW)
                pg.display.update()
                if gs.white_wins():
                    run = False
                    print("White has won!")
                    sleep(3)
                elif gs.black_wins():
                    run = False
                    print("Black has won")
                    sleep(3)
                elif gs.stalemate():
                    run = False
                    print("The game has ended in a draw")
                    sleep(3)
                print(f"Turn {gs.move // 2}: Current evaluation is {gs.evaluate_better()}")
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
                        if selected_piece.colour == WHITE:
                            target_gs = Gamestate(
                                [piece for piece in gs.white_pieces if piece != selected_piece] + [target_piece],
                                gs.black_pieces, gs.move + 1)
                            if gs.is_legal(target_gs):
                                gs.update(target_gs)
                                print(f"Turn {gs.move // 2}: Current evaluation is {gs.evaluate_better()}")
                            else:
                                selected_piece = None
                        else:
                            target_gs = Gamestate(gs.white_pieces,
                                                  [piece for piece in gs.black_pieces if piece != selected_piece] + [
                                                      target_piece],
                                                  gs.move + 1)
                            if gs.is_legal(target_gs):
                                gs.update(target_gs)
                                print(f"Turn {(gs.move // 2) + 1}: Current evaluation is {gs.evaluate_better()}")
                            else:
                                selected_piece = None
                    gs.draw_board(WINDOW)
                    pg.display.update()
                    selected_piece = None
                    if gs.white_wins():
                        print(len(gs.legal_moves_faster(BLACK)))
                        run = False
                        print("White has won!")
                        sleep(3)
                    elif gs.black_wins():
                        print(len(gs.legal_moves_faster(WHITE)))
                        run = False
                        print("Black has won")
                        sleep(3)
                    elif gs.stalemate():
                        run = False
                        print("The game has ended in a draw")
                        sleep(3)
    pg.quit()


if __name__ == '__main__':
    v = int(input("Which version would you like the computer to have? "))
    main(v)
