from random import randint
from time import time

from assets.constants import *
import pygame as pg
from pieces.rook import Rook
from pieces.pawn import Pawn
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.queen import Queen
from src.Openings.openingtree import Tree


def mop_up_eval(white_material_value: int, black_material_value: int, white_king: King, black_king: King,
                endgame_weight: float):
    PawnValue = 100
    # As game transitions to endgame, and if up material, then encourage moving king closer to opponent king
    if white_material_value > black_material_value + 2 * PawnValue and endgame_weight > 0:
        return int(endgame_weight * 4 * (14 - abs(white_king.i - black_king.i) - abs(white_king.j - black_king.j)))
    elif white_material_value < black_material_value - 2 * PawnValue and endgame_weight > 0:
        return -int(endgame_weight * 4 * (14 - abs(white_king.i - black_king.i) - abs(white_king.j - black_king.j)))
    return 0


def king_pawn_shield(white_pawn_positions, white_king, black_pawn_positions, black_king, endgameWeight):
    if endgameWeight >= 0.9:
        return 0
    weights = [0.8, 1.2, 1.1, 0.5, 0.5, 0.7, 1.3, 1]
    kingSafetyValueWhite = 0
    kingSafetyValueBlack = 0
    output = 0
    # Check safety of white king
    if white_king.i == 7:
        kingSafetyValueWhite = 90
    if white_king.i - 1 in white_pawn_positions.get(white_king.j, []):
        kingSafetyValueWhite += 40
    if white_king.i - 1 in white_pawn_positions.get(white_king.j - 1, []):
        kingSafetyValueWhite += 30
    if white_king.i - 1 in white_pawn_positions.get(white_king.j + 1, []):
        kingSafetyValueWhite += 30
    output += kingSafetyValueWhite * weights[white_king.j]
    if black_king.i == 0:
        kingSafetyValueBlack = 90
    if black_king.i + 1 in black_pawn_positions.get(black_king.j, []):
        kingSafetyValueBlack += 40
    if black_king.i + 1 in black_pawn_positions.get(black_king.j - 1, []):
        kingSafetyValueBlack += 30
    if black_king.i + 1 in black_pawn_positions.get(black_king.j + 1, []):
        kingSafetyValueBlack += 30
    return output - kingSafetyValueBlack * weights[black_king.j]


class Gamestate:
    def __init__(self, white_pieces=None, black_pieces=None, move=1, load_images=False, last_non_drawing_turn=1,
                 previous_states: ['Gamestate'] = None):
        if black_pieces is None:
            black_pieces = []
        if white_pieces is None:
            white_pieces = []
        if not white_pieces:
            white_pieces = [Rook(BP_WLROOK, WHITE), Rook(BP_WRROOK, WHITE), Knight(BP_WLKNIGHT, WHITE),
                            Knight(BP_WRKNIGHT, WHITE), Bishop(BP_WLBISHOP, WHITE), Bishop(BP_WRBISHOP, WHITE),
                            Queen(BP_WQUEEN, WHITE), King(BP_WKING, WHITE)]
            for i in range(COLUMNS):
                white_pieces.append(Pawn((ROWS - 2, i), WHITE))
            white_pieces.reverse()  # To promote pawn moves in opening
        self.white_pieces = white_pieces
        if not black_pieces:
            black_pieces = [Rook(BP_BLROOK, BLACK), Rook(BP_BRROOK, BLACK), Knight(BP_BLKNIGHT, BLACK),
                            Knight(BP_BRKNIGHT, BLACK), Bishop(BP_BLBISHOP, BLACK), Bishop(BP_BRBISHOP, BLACK),
                            Queen(BP_BQUEEN, BLACK), King(BP_BKING, BLACK)]
            for i in range(COLUMNS):
                black_pieces.append(Pawn((1, i), BLACK))
            # To promote pawn moves in opening
            black_pieces.reverse()
        self.black_pieces = black_pieces
        self.images = {}
        if load_images:
            # LOAD IMAGES
            pieces = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
            self.images = {}
            for piece in pieces:
                self.images[f"{piece}_black"] = pg.transform.scale(
                    pg.image.load("assets/images/" + piece + "_black.png"),
                    (SQUAREWIDTH, SQUAREWIDTH))
                # white_image = convert_black_to_white(self.images.get(f"{piece}_black"))
                # pg.image.save(white_image, "assets/images/" + piece + "_white.png")
                self.images[f"{piece}_white"] = pg.transform.scale(
                    pg.image.load("assets/images/" + piece + "_white.png"),
                    (SQUAREWIDTH, SQUAREWIDTH))
        self.move = move
        self.last_non_drawing_turn = last_non_drawing_turn
        self.moves = ""
        if previous_states is None:
            self.previous_states = [self.deep_copy_without_previous_states()]
        else:
            self.previous_states = previous_states.copy()
        self.white_dict = {}
        self.black_dict = {}
        for piece in self.white_pieces:
            self.white_dict[(piece.i, piece.j)] = piece
        for piece in self.black_pieces:
            self.black_dict[(piece.i, piece.j)] = piece

    def __eq__(self, other):
        if not isinstance(other, Gamestate):
            return False
        if len(other.white_pieces) != len(self.white_pieces) or len(other.black_pieces) != len(self.black_pieces):
            return False
        for piece in self.white_pieces:
            if piece not in other.white_pieces:
                return False
        for piece in self.black_pieces:
            if piece not in other.black_pieces:
                return False
        return True

    def get_piece(self, i, j, colour=None):
        if colour is None:
            result = self.white_dict.get((i, j), None)
            return result if result is not None else self.black_dict.get((i, j), None)
        elif colour == WHITE:
            return self.white_dict.get((i, j), None)
        else:
            return self.black_dict.get((i, j), None)

    def white_wins(self):
        if self.move % 2 == 0 and len(self.legal_moves(BLACK)) == 0 and self.king_under_attack(BLACK):
            return True
        return False

    def black_wins(self):
        if self.move % 2 == 1 and len(self.legal_moves(WHITE)) == 0 and self.king_under_attack(WHITE):
            return True
        return False

    def stalemate(self):
        if (self.move % 2 == 1 and len(self.legal_moves(WHITE)) == 0 and not self.king_under_attack(WHITE)) or \
                (self.move % 2 == 0 and len(self.legal_moves(BLACK)) == 0 and not self.king_under_attack(BLACK)):
            return True

        # 50 MOVE RULE
        if self.move - self.last_non_drawing_turn >= 100:
            return True

        # THREEPEAT RULE
        if self.previous_states.count(self) >= 3:
            return True

        # CHECK FOR INSUFFICIENT MATERIAL
        if len(self.black_pieces) == len(self.white_pieces) == 1:
            return True
        wknight_count, wbishop_count = 0, 0
        bknight_count, bbishop_count = 0, 0
        black_bishop = None
        white_bishop = None
        for piece in self.white_pieces:
            if piece.value == PAWN:
                return False
            elif piece.value == KNIGHT:
                wknight_count += 1
            elif piece.value == ROOK:
                return False
            elif piece.value == QUEEN:
                return False
            elif piece.value == BISHOP:
                wbishop_count += 1
                white_bishop = piece

        for piece in self.black_pieces:
            if piece.value == PAWN:
                return False
            elif piece.value == KNIGHT:
                bknight_count += 1
            elif piece.value == ROOK:
                return False
            elif piece.value == QUEEN:
                return False
            elif piece.value == BISHOP:
                bbishop_count += 1
                black_bishop = piece

        # bishop vs knight is a draw
        if bbishop_count == 1 and bknight_count == 0 and wbishop_count == 0 and wknight_count == 1:
            return True
        if wbishop_count == 1 and wknight_count == 0 and bbishop_count == 0 and bknight_count == 1:
            return True

        # only a knight can never force checkmate
        if bbishop_count == 0 and bknight_count == 0 and wbishop_count == 0 and wknight_count == 1:
            return True
        if bbishop_count == 0 and bknight_count == 1 and wbishop_count == 0 and wknight_count == 0:
            return True
        if bbishop_count == 0 and bknight_count == 1 and wbishop_count == 0 and wknight_count == 1:
            return True

        # bishops on same diagonal can't force checkmate
        if bbishop_count == 1 and bknight_count == 0 and wbishop_count == 1 and wknight_count == 0 and \
                (white_bishop.i + white_bishop.j % 2) == (black_bishop.i + black_bishop.j % 2):
            return True

        # 2 knights can't force a checkmate
        if bbishop_count == 0 and bknight_count == 2 and wbishop_count == 0 and wknight_count == 0:
            return True
        if bbishop_count == 0 and bknight_count == 0 and wbishop_count == 0 and wknight_count == 2:
            return True

        # lone bishop can't force a checkmate
        if bbishop_count == 1 and bknight_count == 0 and wbishop_count == 0 and wknight_count == 0:
            return True
        if bbishop_count == 0 and bknight_count == 0 and wbishop_count == 1 and wknight_count == 0:
            return True
        return False

    def legal_moves(self, colour, sort_by_heuristic=False) -> list['Gamestate']:
        """
A function that returns ALL possible valid gamestates after colour makes a move. If 'sort_by_heuristic' is True, moves
will be ordered by captures, forward moves and ending with backwards moves
        :param sort_by_heuristic:
        :param colour: WHITE or BLACK
        :return: list[Gamestate]
        """
        if sort_by_heuristic:
            captures, forward, backward = [], [], []
            for move, moved_piece_old, moved_piece_new in self.generate_all_moves(colour, return_moved_pieces=True):
                if self.is_legal(move):
                    capture_flag = False
                    if colour == WHITE:
                        # CHECK FOR CAPTURE
                        for piece in self.black_pieces:
                            if (piece.i == moved_piece_new.i and piece.j == moved_piece_new.j) or (
                                    piece.value == moved_piece_new.value == PAWN and piece.en_passantable and moved_piece_new.i == piece.i - 1 and moved_piece_new.j == piece.j):
                                captures.append(move)
                                capture_flag = True
                                break
                        if not capture_flag:
                            if moved_piece_old.i > moved_piece_new.i:
                                # FORWARD MOVE
                                forward.append(move)
                            else:
                                # BACKWARD MOVE
                                backward.append(move)
                    else:
                        for piece in self.white_pieces:
                            if (piece.i == moved_piece_new.i and piece.j == moved_piece_new.j) or (
                                    piece.value == moved_piece_new.value == PAWN and piece.en_passantable and moved_piece_new.i == piece.i + 1 and moved_piece_new.j == piece.j):
                                captures.append(move)
                                capture_flag = True
                                break
                        if not capture_flag:
                            if moved_piece_old.i < moved_piece_new.i:
                                # FORWARD MOVE
                                forward.append(move)
                            else:
                                # BACKWARD MOVE
                                backward.append(move)
            return captures + forward + backward
        output = []
        for move in self.generate_all_moves(colour):
            if self.is_legal(move):
                output.append(move)
        return output

    def legal_moves_faster(self, colour):
        output = []
        if colour == WHITE:
            for piece in self.white_pieces:
                if piece.value == KING:
                    for new_king in piece.generate_possible_moves():
                        new_gs = Gamestate([new_king] + [wp for wp in self.white_pieces if wp != piece],
                                           self.black_pieces, self.move + 1)
                        if self.is_legal(new_gs) and self.get_piece(new_king.i, new_king.j, BLACK) is None :
                            output.append(new_gs)
                elif piece.value == KNIGHT:
                    for temp_knight in piece.generate_possible_moves():
                        temp_gs = Gamestate([temp_knight] + [wp for wp in self.white_pieces if wp != piece],
                                           self.black_pieces, self.move + 1)
                        if self.is_legal(temp_gs) and self.get_piece(temp_knight.i, temp_knight.j, BLACK) is None:
                            output.append(temp_gs)
                elif piece.value == PAWN:
                    new_pawn = Pawn((piece.i-1, piece.j), WHITE, False)
                    new_gs = Gamestate([new_pawn] + [wp for wp in self.white_pieces if wp != piece],
                                           self.black_pieces, self.move + 1)
                    if self.is_legal(new_gs):
                        output.append(new_gs)
                    if piece.i == 6:
                        new_pawn2 = Pawn((piece.i - 2, piece.j), WHITE, True)
                        new_gs2 = Gamestate([new_pawn2] + [wp for wp in self.white_pieces if wp != piece],
                                           self.black_pieces, self.move + 1)
                        if self.is_legal(new_gs2):
                            output.append(new_gs2)
                elif piece.value == ROOK:
                    index_up = 1
                    index_left = 1
                    index_right = 1
                    index_down = 1

                    # UP
                    if True:
                        while piece.i - index_up >= 0:
                            if self.get_piece(piece.i - index_up, piece.j):
                                break
                            # elif self.get_piece(piece.i - index_up, piece.j, BLACK):
                            #    CAPTURES WILL BE GENERATED BY GENERATE_CAPTURES
                            #    new_gs = Gamestate(
                            #        [Rook((piece.i - index_up, piece.j), WHITE, True)] + [wp for wp in self.white_pieces
                            #                                                              if wp != piece],
                            #        self.black_pieces, self.move + 1)
                            #    output.append(new_gs)
                            #    break
                            else:
                                new_gs = Gamestate(
                                    [Rook((piece.i - index_up, piece.j), WHITE, True)] + [wp for wp in self.white_pieces
                                                                                          if wp != piece],
                                    self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_up += 1

                    # DOWN
                    if True:
                        # ROOK IS NOT PINNED IN THIS DIRECTION
                        while piece.i + index_down < 8:
                            if self.get_piece(piece.i + index_down, piece.j):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Rook((piece.i + index_down, piece.j), WHITE, True)] + [wp for wp in
                                                                                            self.white_pieces
                                                                                            if wp != piece],
                                    self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_down += 1

                    # LEFT
                    if True:
                        # ROOK IS NOT PINNED IN THIS DIRECTION
                        while piece.j - index_left >= 0:
                            if self.get_piece(piece.i, piece.j - index_left):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Rook((piece.i, piece.j - index_left), WHITE, True)] + [wp for wp in
                                                                                            self.white_pieces
                                                                                            if wp != piece],
                                    self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_left += 1

                    # RIGHT
                    if True:
                        # ROOK IS NOT PINNED IN THIS DIRECTION
                        while piece.j + index_right < 8:
                            if self.get_piece(piece.i, piece.j + index_right):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Rook((piece.i, piece.j + index_right), WHITE, True)] + [wp for wp in
                                                                                             self.white_pieces
                                                                                             if wp != piece],
                                    self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_right += 1

                elif piece.value == BISHOP:
                    index_top_right = 1
                    index_bottom_right = 1
                    index_top_left = 1
                    index_bottom_left = 1

                    # BOTTOM RIGHT
                    if True:
                        # BISHOP IS NOT PINNED IN THIS DIRECTION
                        while piece.i + index_bottom_right < 8 and piece.j + index_bottom_right < 8:
                            if self.get_piece(piece.i + index_bottom_right, piece.j + index_bottom_right):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Bishop((piece.i + index_bottom_right, piece.j + index_bottom_right), WHITE)] + [wp
                                                                                                                     for
                                                                                                                     wp
                                                                                                                     in
                                                                                                                     self.white_pieces
                                                                                                                     if
                                                                                                                     wp != piece],
                                    self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_bottom_right += 1

                    # TOP RIGHT
                    if True:
                        # BISHOP IS NOT PINNED IN THIS DIRECTION
                        while piece.i - index_top_right >= 0 and piece.j + index_top_right < 8:
                            if self.get_piece(piece.i - index_top_right, piece.j + index_top_right):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Bishop((piece.i - index_top_right, piece.j + index_top_right), WHITE)] +
                                    [wp for wp in self.white_pieces if wp != piece], self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_top_right += 1

                    # TOP LEFT
                    if True:
                        # BISHOP IS NOT PINNED IN THIS DIRECTION
                        while piece.i - index_top_left >= 0 and piece.j - index_top_left >= 0:
                            if self.get_piece(piece.i - index_top_left, piece.j - index_top_left):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Bishop((piece.i - index_top_left, piece.j - index_top_left), WHITE)] +
                                    [wp for wp in self.white_pieces if wp != piece], self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_top_left += 1

                    # BOTTOM LEFT
                    if True:
                        # BISHOP IS NOT PINNED IN THIS DIRECTION
                        while piece.i + index_bottom_left < 8 and piece.j - index_bottom_left >= 0:
                            if self.get_piece(piece.i + index_bottom_left, piece.j - index_bottom_left):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Bishop((piece.i + index_bottom_left, piece.j - index_bottom_left), WHITE)] +
                                    [wp for wp in self.white_pieces if wp != piece], self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_bottom_left += 1

                else:
                    # QUEEN
                    index_up = 1
                    index_left = 1
                    index_right = 1
                    index_down = 1
                    index_top_right = 1
                    index_bottom_right = 1
                    index_top_left = 1
                    index_bottom_left = 1

                    # UP
                    if True:
                        # QUEEN IS NOT PINNED IN THIS DIRECTION
                        while piece.i - index_up >= 0:
                            if self.get_piece(piece.i - index_up, piece.j):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Queen((piece.i - index_up, piece.j), WHITE)] + [wp for wp in self.white_pieces
                                                                                          if wp != piece],
                                    self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_up += 1

                    # DOWN
                    if True:
                        # QUEEN IS NOT PINNED IN THIS DIRECTION
                        while piece.i + index_down < 8:
                            if self.get_piece(piece.i + index_down, piece.j):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Queen((piece.i + index_down, piece.j), WHITE)] + [wp for wp in
                                                                                            self.white_pieces
                                                                                            if wp != piece],
                                    self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_down += 1

                    # LEFT
                    if True:
                        # QUEEN IS NOT PINNED IN THIS DIRECTION
                        while piece.j - index_left >= 0:
                            if self.get_piece(piece.i, piece.j - index_left):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Queen((piece.i, piece.j - index_left), WHITE)] + [wp for wp in
                                                                                            self.white_pieces
                                                                                            if wp != piece],
                                    self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_left += 1

                    # RIGHT

                    if True:
                        # QUEEN IS NOT PINNED IN THIS DIRECTION

                        while piece.j + index_right < 8:
                            if self.get_piece(piece.i, piece.j + index_right):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Queen((piece.i, piece.j + index_right), WHITE)] + [wp for wp in
                                                                                             self.white_pieces
                                                                                             if wp != piece],
                                    self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_right += 1

                    # BOTTOM RIGHT
                    if True:
                        # QUEEN IS NOT PINNED IN THIS DIRECTION

                        while piece.i + index_bottom_right < 8 and piece.j + index_bottom_right < 8:
                            if self.get_piece(piece.i + index_bottom_right, piece.j + index_bottom_right):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Queen((piece.i + index_bottom_right, piece.j + index_bottom_right), WHITE)] + [wp
                                                                                                                     for
                                                                                                                     wp
                                                                                                                     in
                                                                                                                     self.white_pieces
                                                                                                                     if
                                                                                                                     wp != piece],
                                    self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_bottom_right += 1

                    # TOP RIGHT
                    if True:
                        # QUEEN IS NOT PINNED IN THIS DIRECTION

                        while piece.i - index_top_right >= 0 and piece.j + index_top_right < 8:
                            if self.get_piece(piece.i - index_top_right, piece.j + index_top_right):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Queen((piece.i - index_top_right, piece.j + index_top_right), WHITE)] +
                                    [wp for wp in self.white_pieces if wp != piece], self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_top_right += 1

                    # TOP LEFT

                    if True:
                        while piece.i - index_top_left >= 0 and piece.j - index_top_left >= 0:
                            if self.get_piece(piece.i - index_top_left, piece.j - index_top_left):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Queen((piece.i - index_top_left, piece.j - index_top_left), WHITE)] +
                                    [wp for wp in self.white_pieces if wp != piece], self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_top_left += 1

                    # BOTTOM LEFT

                    if True:
                        # QUEEN IS NOT PINNED IN THIS DIRECTION
                        while piece.i + index_bottom_left < 8 and piece.j - index_bottom_left >= 0:
                            if self.get_piece(piece.i + index_bottom_left, piece.j - index_bottom_left):
                                break
                            else:
                                new_gs = Gamestate(
                                    [Queen((piece.i + index_bottom_left, piece.j - index_bottom_left), WHITE)] +
                                    [wp for wp in self.white_pieces if wp != piece], self.black_pieces, self.move + 1)
                                if not new_gs.king_under_attack(WHITE):
                                    output.append(new_gs)
                                index_bottom_left += 1
            return self.generate_captures(WHITE) + output

        else:
            for piece in self.black_pieces:
                if piece.value == KING:
                    for new_king in piece.generate_possible_moves():
                        new_gs = Gamestate(self.white_pieces, [new_king] + [bp for bp in self.black_pieces if bp != piece], self.move + 1)
                        if self.is_legal(new_gs) and self.get_piece(new_king.i, new_king.j, WHITE) is None:
                            output.append(new_gs)
                elif piece.value == KNIGHT:
                    for temp_knight in piece.generate_possible_moves():
                        temp_gs = Gamestate(self.white_pieces, [temp_knight] + [bp for bp in self.black_pieces if bp != piece]
                                             , self.move + 1)
                        if self.is_legal(temp_gs) and self.get_piece(temp_knight.i, temp_knight.j, WHITE) is None:
                            output.append(temp_gs)
                elif piece.value == PAWN:
                    new_pawn = Pawn((piece.i + 1, piece.j), BLACK, False)
                    new_gs = Gamestate(self.white_pieces, [new_pawn] + [bp for bp in self.black_pieces if bp != piece], self.move + 1)
                    if self.is_legal(new_gs):
                        output.append(new_gs)
                    if piece.i == 1:
                        new_pawn2 = Pawn((piece.i + 2, piece.j), BLACK, True)
                        new_gs2 = Gamestate(self.white_pieces, [new_pawn2] + [bp for bp in self.black_pieces if bp != piece],
                                            self.move + 1)
                        if self.is_legal(new_gs2):
                            output.append(new_gs2)
                elif piece.value == ROOK:
                    index_up = 1
                    index_left = 1
                    index_right = 1
                    index_down = 1

                    # UP
                    if True:
                        # ROOK IS NOT PINNED IN THIS DIRECTION
                        while piece.i - index_up >= 0:
                            if self.get_piece(piece.i - index_up, piece.j):
                                break
                            # elif self.get_piece(piece.i - index_up, piece.j, BLACK):
                            #    CAPTURES WILL BE GENERATED BY GENERATE_CAPTURES
                            #    new_gs = Gamestate(
                            #        [Rook((piece.i - index_up, piece.j), WHITE, True)] + [wp for wp in self.white_pieces
                            #                                                              if wp != piece],
                            #        self.black_pieces, self.move + 1)
                            #    output.append(new_gs)
                            #    break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Rook((piece.i - index_up, piece.j), BLACK, True)] + [bp for bp in self.black_pieces
                                                                                          if bp != piece],
                                    self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_up += 1

                    # DOWN
                    if True:
                        # ROOK IS NOT PINNED IN THIS DIRECTION
                        while piece.i + index_down < 8:
                            if self.get_piece(piece.i + index_down, piece.j):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Rook((piece.i + index_down, piece.j), BLACK, True)] + [bp for bp in
                                                                                            self.black_pieces
                                                                                            if bp != piece],
                                    self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_down += 1

                    # LEFT
                    if True:
                        # ROOK IS NOT PINNED IN THIS DIRECTION
                        while piece.j - index_left >= 0:
                            if self.get_piece(piece.i, piece.j - index_left):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Rook((piece.i, piece.j - index_left), BLACK, True)] + [bp for bp in
                                                                                            self.black_pieces
                                                                                            if bp != piece],
                                    self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_left += 1

                    # RIGHT
                    if True:
                        # ROOK IS NOT PINNED IN THIS DIRECTION
                        while piece.j + index_right < 8:
                            if self.get_piece(piece.i, piece.j + index_right):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Rook((piece.i, piece.j + index_right), BLACK, True)] + [bp for bp in
                                                                                             self.black_pieces
                                                                                             if bp != piece],
                                    self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_right += 1

                elif piece.value == BISHOP:
                    index_top_right = 1
                    index_bottom_right = 1
                    index_top_left = 1
                    index_bottom_left = 1

                    # BOTTOM RIGHT
                    if True:
                        # BISHOP IS NOT PINNED IN THIS DIRECTION
                        while piece.i + index_bottom_right < 8 and piece.j + index_bottom_right < 8:
                            if self.get_piece(piece.i + index_bottom_right, piece.j + index_bottom_right):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Bishop((piece.i + index_bottom_right, piece.j + index_bottom_right), BLACK)] + [bp
                                                                                                                     for
                                                                                                                     bp
                                                                                                                     in
                                                                                                                     self.black_pieces
                                                                                                                     if
                                                                                                                     bp != piece],
                                    self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_bottom_right += 1

                    # TOP RIGHT

                    if True:
                        # BISHOP IS NOT PINNED IN THIS DIRECTION

                        while piece.i - index_top_right >= 0 and piece.j + index_top_right < 8:
                            if self.get_piece(piece.i - index_top_right, piece.j + index_top_right):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Bishop((piece.i - index_top_right, piece.j + index_top_right), BLACK)] +
                                    [bp for bp in self.black_pieces if bp != piece], self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_top_right += 1

                    # TOP LEFT
                    if True:
                        # BISHOP IS NOT PINNED IN THIS DIRECTION
                        while piece.i - index_top_left >= 0 and piece.j - index_top_left >= 0:
                            if self.get_piece(piece.i - index_top_left, piece.j - index_top_left):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Bishop((piece.i - index_top_left, piece.j - index_top_left), BLACK)] +
                                    [bp for bp in self.black_pieces if bp != piece], self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_top_left += 1

                    # BOTTOM LEFT
                    if True:
                        # BISHOP IS NOT PINNED IN THIS DIRECTION
                        while piece.i + index_bottom_left < 8 and piece.j - index_bottom_left >= 0:
                            if self.get_piece(piece.i + index_bottom_left, piece.j - index_bottom_left):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Bishop((piece.i + index_bottom_left, piece.j - index_bottom_left), BLACK)] +
                                    [bp for bp in self.black_pieces if bp != piece], self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_bottom_left += 1

                else:
                    # QUEEN
                    index_up = 1
                    index_left = 1
                    index_right = 1
                    index_down = 1
                    index_top_right = 1
                    index_bottom_right = 1
                    index_top_left = 1
                    index_bottom_left = 1

                    # UP
                    if True:
                        # QUEEN IS NOT PINNED IN THIS DIRECTION

                        while piece.i - index_up >= 0:
                            if self.get_piece(piece.i - index_up, piece.j):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Queen((piece.i - index_up, piece.j), BLACK)] + [bp for bp in self.black_pieces
                                                                                     if bp != piece],
                                    self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_up += 1

                    # DOWN
                    if True:
                        # QUEEN IS NOT PINNED IN THIS DIRECTION

                        while piece.i + index_down < 8:
                            if self.get_piece(piece.i + index_down, piece.j):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Queen((piece.i + index_down, piece.j), BLACK)] + [bp for bp in
                                                                                       self.black_pieces
                                                                                       if bp != piece],
                                    self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_down += 1

                    # LEFT
                    if True:
                        while piece.j - index_left >= 0:
                            if self.get_piece(piece.i, piece.j - index_left):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Queen((piece.i, piece.j - index_left), BLACK)] + [bp for bp in
                                                                                       self.black_pieces
                                                                                       if bp != piece],
                                    self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_left += 1

                    # RIGHT
                    if True:
                        while piece.j + index_right < 8:
                            if self.get_piece(piece.i, piece.j + index_right):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Queen((piece.i, piece.j + index_right), BLACK)] + [bp for bp in
                                                                                        self.black_pieces
                                                                                        if bp != piece],
                                    self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_right += 1

                    # BOTTOM RIGHT
                    if True:
                        while piece.i + index_bottom_right < 8 and piece.j + index_bottom_right < 8:
                            if self.get_piece(piece.i + index_bottom_right, piece.j + index_bottom_right):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Queen((piece.i + index_bottom_right, piece.j + index_bottom_right), BLACK)] + [bp
                                                                                                                    for
                                                                                                                    bp
                                                                                                                    in
                                                                                                                    self.black_pieces
                                                                                                                    if
                                                                                                                    bp != piece],
                                    self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_bottom_right += 1

                    # TOP RIGHT
                    if True:
                        while piece.i - index_top_right >= 0 and piece.j + index_top_right < 8:
                            if self.get_piece(piece.i - index_top_right, piece.j + index_top_right):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Queen((piece.i - index_top_right, piece.j + index_top_right), BLACK)] +
                                    [bp for bp in self.black_pieces if bp != piece], self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_top_right += 1

                    # TOP LEFT
                    if True:
                        while piece.i - index_top_left >= 0 and piece.j - index_top_left >= 0:
                            if self.get_piece(piece.i - index_top_left, piece.j - index_top_left):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Queen((piece.i - index_top_left, piece.j - index_top_left), BLACK)] +
                                    [bp for bp in self.white_pieces if bp != piece], self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_top_left += 1

                    # BOTTOM LEFT
                    if True:
                        while piece.i + index_bottom_left < 8 and piece.j - index_bottom_left >= 0:
                            if self.get_piece(piece.i + index_bottom_left, piece.j - index_bottom_left):
                                break
                            else:
                                new_gs = Gamestate(self.white_pieces,
                                    [Queen((piece.i + index_bottom_left, piece.j - index_bottom_left), BLACK)] +
                                    [bp for bp in self.black_pieces if bp != piece], self.move + 1)
                                if not new_gs.king_under_attack(BLACK):
                                    output.append(new_gs)
                                index_bottom_left += 1
            return self.generate_captures(BLACK) + output

    def king_under_attack(self, colour):
        """
Checks if the king of team 'colour' is in check
        :param colour: WHITE or BLACK
        :return: True or False
        """
        king = None
        for piece in self.white_pieces:
            if piece.colour == colour and piece.value == KING:
                king = piece
                break
        if king is None:
            for piece in self.black_pieces:
                if piece.colour == colour and piece.value == KING:
                    king = piece
                    break
        if king is None:
            raise Exception
        # Check if a rook or queen can attack king from horizontal line
        blocking_piece_found = False
        horizontal_index_left = king.j - 1
        horizontal_index_right = king.j + 1
        while horizontal_index_left >= 0 and not blocking_piece_found:
            piece = self.get_piece(king.i, horizontal_index_left, opposite(colour))
            if piece is not None and (piece.value == ROOK or piece.value == QUEEN) and piece.colour != colour:
                if self.get_piece(piece.i, piece.j, colour) is None:
                    return True
            if piece is not None or self.get_piece(king.i, horizontal_index_left, colour) is not None:
                blocking_piece_found = True
            horizontal_index_left -= 1
        blocking_piece_found = False
        while horizontal_index_right < 8 and not blocking_piece_found:
            piece = self.get_piece(king.i, horizontal_index_right, opposite(colour))
            if piece is not None and (piece.value == ROOK or piece.value == QUEEN) and piece.colour != colour:
                if self.get_piece(piece.i, piece.j, colour) is None:
                    return True
            if piece is not None or self.get_piece(king.i, horizontal_index_right, colour) is not None:
                blocking_piece_found = True
            horizontal_index_right += 1

        # Check if a rook or queen can attack king from vertical line
        blocking_piece_found = False
        vertical_index_up = king.i - 1
        vertical_index_down = king.i + 1
        while vertical_index_up >= 0 and not blocking_piece_found:
            piece = self.get_piece(vertical_index_up, king.j, opposite(colour))
            if piece is not None and (piece.value == ROOK or piece.value == QUEEN) and piece.colour != colour:
                if self.get_piece(piece.i, piece.j, colour) is None:
                    return True
            if piece is not None or self.get_piece(vertical_index_up, king.j, colour) is not None:
                blocking_piece_found = True
            vertical_index_up -= 1
        blocking_piece_found = False
        while vertical_index_down < 8 and not blocking_piece_found:
            piece = self.get_piece(vertical_index_down, king.j, opposite(colour))
            if piece is not None and (piece.value == ROOK or piece.value == QUEEN) and piece.colour != colour:
                if self.get_piece(piece.i, piece.j, colour) is None:
                    return True
            if piece is not None or self.get_piece(vertical_index_down, king.j, colour) is not None:
                blocking_piece_found = True
            vertical_index_down += 1

        # Check if bishop or queen can attack from diagonal:
        blocking_piece_found = False
        index_tr = 1
        index_tl = 1
        index_br = 1
        index_bl = 1

        # Bottom right
        while king.i + index_br < 8 and king.j + index_br < 8 and not blocking_piece_found:
            piece = self.get_piece(king.i + index_br, king.j + index_br, opposite(colour))
            if piece is not None and (piece.value == BISHOP or piece.value == QUEEN) and piece.colour != colour:
                if self.get_piece(piece.i, piece.j, colour) is None:
                    return True
            if piece is not None or self.get_piece(king.i + index_br, king.j + index_br, colour) is not None:
                blocking_piece_found = True
            index_br += 1
        blocking_piece_found = False
        # Bottom left
        while king.i + index_bl < 8 and king.j - index_bl >= 0 and not blocking_piece_found:
            piece = self.get_piece(king.i + index_bl, king.j - index_bl, opposite(colour))
            if piece is not None and (piece.value == BISHOP or piece.value == QUEEN) and piece.colour != colour:
                if self.get_piece(piece.i, piece.j, colour) is None:
                    return True
            if piece is not None or self.get_piece(king.i + index_bl, king.j - index_bl, colour) is not None:
                blocking_piece_found = True
            index_bl += 1
        blocking_piece_found = False
        # Top right
        while king.i - index_tr >= 0 and king.j + index_tr < 8 and not blocking_piece_found:
            piece = self.get_piece(king.i - index_tr, king.j + index_tr, opposite(colour))
            if piece is not None and (piece.value == BISHOP or piece.value == QUEEN) and piece.colour != colour:
                if self.get_piece(piece.i, piece.j, colour) is None:
                    return True
            if piece is not None or self.get_piece(king.i - index_tr, king.j + index_tr, colour) is not None:
                blocking_piece_found = True
            index_tr += 1
        blocking_piece_found = False
        # Top left
        while king.i - index_tl >= 0 and king.j - index_tl >= 0 and not blocking_piece_found:
            piece = self.get_piece(king.i - index_tl, king.j - index_tl, opposite(colour))
            if piece is not None and (piece.value == BISHOP or piece.value == QUEEN) and piece.colour != colour:
                if self.get_piece(piece.i, piece.j, colour) is None:
                    return True
            if piece is not None or self.get_piece(king.i - index_tl, king.j - index_tl, colour) is not None:
                blocking_piece_found = True
            index_tl += 1
        piece_top_left = self.get_piece(king.i - 1, king.j - 1, opposite(colour))
        piece_top_right = self.get_piece(king.i - 1, king.j + 1, opposite(colour))
        piece_bottom_left = self.get_piece(king.i + 1, king.j - 1, opposite(colour))
        piece_bottom_right = self.get_piece(king.i + 1, king.j + 1, opposite(colour))

        # Check if a pawn can attack king
        if (king.colour == WHITE and (
                (piece_top_left is not None and piece_top_left.colour == BLACK and piece_top_left.value == PAWN and
                 self.get_piece(king.i - 1, king.j - 1, colour) is None and not (
                                piece_top_left.en_passantable and self.get_piece(king.i - 2, king.j - 1,
                                                                                 colour) is not None)) or (
                        piece_top_right is not None and piece_top_right.colour == BLACK and piece_top_right.value ==
                        PAWN and self.get_piece(king.i - 1, king.j + 1, colour) is None and not (
                        piece_top_right.en_passantable and self.get_piece(king.i - 2, king.j + 1,
                                                                          colour) is not None)))) or \
                (king.colour == BLACK and ((
                                                   piece_bottom_left is not None and piece_bottom_left.colour == WHITE and piece_bottom_left.value == PAWN and self.get_piece(
                                               king.i + 1, king.j - 1, colour) is None and not (
                                                   piece_bottom_left.en_passantable and self.get_piece(king.i + 2,
                                                                                                       king.j - 1,
                                                                                                       colour) is not None)) or (
                                                   piece_bottom_right is not None and piece_bottom_right.colour == WHITE
                                                   and piece_bottom_right.value == PAWN and
                                                   self.get_piece(king.i + 1, king.j + 1, colour) is None and not (
                                                   piece_bottom_right.en_passantable and self.get_piece(king.i + 2,
                                                                                                        king.j + 1,
                                                                                                        colour) is not None)))):
            return True

        # Check if a knight can attack king
        if colour == WHITE:
            for piece in self.black_pieces:
                if piece.value == KNIGHT and ((abs(piece.i - king.i) == 2 and abs(piece.j - king.j) == 1) or (
                        abs(piece.i - king.i) == 1 and abs(piece.j - king.j) == 2)):
                    captured = False
                    for own_piece in self.white_pieces:
                        if own_piece.i == piece.i and own_piece.j == piece.j:
                            captured = True
                    if not captured:
                        return True
        else:
            for piece in self.white_pieces:
                if piece.value == KNIGHT and ((abs(piece.i - king.i) == 2 and abs(piece.j - king.j) == 1) or (
                        abs(piece.i - king.i) == 1 and abs(piece.j - king.j) == 2)):
                    captured = False
                    for own_piece in self.black_pieces:
                        if own_piece.i == piece.i and own_piece.j == piece.j:
                            captured = True
                    if not captured:
                        return True

        # Check if other king can attack king
        if colour == WHITE:
            for piece in self.black_pieces:
                if piece.value == KING and (abs(piece.i - king.i) <= 1 and abs(piece.j - king.j) <= 1):
                    return True
        else:
            for piece in self.white_pieces:
                if piece.value == KING and (abs(piece.i - king.i) <= 1 and abs(piece.j - king.j) <= 1):
                    return True
        return False

    def is_legal(self, new_board: 'Gamestate'):
        """
Checks if it is legal to go from this Gamestate to the given gamestate. Assumes only one piece has changed position
        :param new_board: Gamestate
        :return: True or False
        """

        # CHECK IF MOVE COUNT IS CORRECT
        if new_board.move != self.move + 1:
            return False

        # FIND MOVED PIECE:
        moved_piece_old = None
        moved_piece_new = None
        for piece in self.white_pieces:
            if piece not in new_board.white_pieces:
                moved_piece_old = piece
                break
        if moved_piece_old is None:
            for piece in self.black_pieces:
                if piece not in new_board.black_pieces:
                    moved_piece_old = piece
                    break

        for piece in new_board.white_pieces:
            if piece not in self.white_pieces:
                moved_piece_new = piece
                break
        if moved_piece_new is None:
            for piece in new_board.black_pieces:
                if piece not in self.black_pieces:
                    moved_piece_new = piece
                    break

        # Check if nothing has moved
        if moved_piece_old is None or moved_piece_new is None:
            return False

        # Check if new position is still on the board:
        if moved_piece_new.i < 0 or moved_piece_new.i >= 8 or moved_piece_new.j < 0 or moved_piece_new.j >= 8:
            return False

        # Check if wrong colour was moved
        if (moved_piece_old.colour == WHITE and self.move % 2 == 0) or \
                (moved_piece_old.colour == BLACK and self.move % 2 == 1):
            return False

        # Check if moved piece has same new position as other piece of same colour (so no capture)
        count = 0
        if moved_piece_old.colour == WHITE:
            for piece in new_board.white_pieces:
                if piece.i == moved_piece_new.i and piece.j == moved_piece_new.j:
                    count += 1
        else:
            for piece in new_board.black_pieces:
                if piece.i == moved_piece_new.i and piece.j == moved_piece_new.j:
                    count += 1
        if count != 1:
            return False

        # Check if king is capturable after move made (or attempt to castle, which needs different kind of check)
        if new_board.king_under_attack(moved_piece_old.colour) and not (moved_piece_old.value == KING and not
        self.king_under_attack(moved_piece_old.colour)
                                                                        and moved_piece_old.i == moved_piece_new.i and
                                                                        abs(moved_piece_old.j - moved_piece_new.j) == 2
                                                                        and not moved_piece_old.has_moved):
            return False

        if moved_piece_old.value == PAWN:
            # CHECK IF LEGAL PAWN MOVE
            if moved_piece_old.colour == WHITE:
                # WHITE PAWNS MOVE UP, SO DECREASING I VALUE
                if moved_piece_old.j == moved_piece_new.j:
                    # if it moved forward, there can be no piece of either colour in front
                    if moved_piece_new.i == moved_piece_old.i - 1:
                        for piece in self.white_pieces:
                            if piece.i == moved_piece_new.i and piece.j == moved_piece_new.j:
                                return False
                        for piece in self.black_pieces:
                            if piece.i == moved_piece_new.i and piece.j == moved_piece_new.j:
                                return False
                        return True
                    elif moved_piece_new.i == moved_piece_old.i - 2 and moved_piece_old.i == 6:
                        # First move of the pawn, so it's allowed to move two positions up if there's nothing in between
                        for piece in self.white_pieces:
                            if (
                                    piece.i == moved_piece_new.i or piece.i == moved_piece_new.i + 1) and piece.j == moved_piece_new.j:
                                return False
                        for piece in self.black_pieces:
                            if (
                                    piece.i == moved_piece_new.i or piece.i == moved_piece_new.i + 1) and piece.j == moved_piece_new.j:
                                return False
                        moved_piece_new.en_passantable = True
                        return True
                    else:
                        # Moved up (or down) too many spaces
                        return False
                elif (
                        moved_piece_old.j == moved_piece_new.j + 1 or moved_piece_old.j == moved_piece_new.j - 1) and moved_piece_new.i == moved_piece_old.i - 1:
                    # Moved diagonally to capture something
                    for piece in new_board.black_pieces:
                        if (piece.i == moved_piece_new.i and piece.j == moved_piece_new.j) or (
                                piece.value == PAWN and piece.en_passantable and piece.i == moved_piece_new.i + 1 and piece.j == moved_piece_new.j):
                            return True

                    # No capturable piece on this spot
                    return False
                # Moved sideways illegally
                return False

            else:
                # BLACK PAWNS MOVE DOWN, SO INCREASING I VALUE
                if moved_piece_old.j == moved_piece_new.j:
                    # if it moved forward, there can be no piece of either colour in front
                    if moved_piece_new.i == moved_piece_old.i + 1:
                        for piece in self.white_pieces:
                            if piece.i == moved_piece_new.i and piece.j == moved_piece_new.j:
                                return False
                        for piece in self.black_pieces:
                            if piece.i == moved_piece_new.i and piece.j == moved_piece_new.j:
                                return False
                        return True
                    elif moved_piece_new.i == moved_piece_old.i + 2 and moved_piece_old.i == 1:
                        # First move of the pawn, so it's allowed to move two positions up if there's nothing in between
                        for piece in self.white_pieces:
                            if (
                                    piece.i == moved_piece_new.i or piece.i == moved_piece_new.i - 1) and piece.j == moved_piece_new.j:
                                return False
                        for piece in self.black_pieces:
                            if (
                                    piece.i == moved_piece_new.i or piece.i == moved_piece_new.i - 1) and piece.j == moved_piece_new.j:
                                return False
                        moved_piece_new.en_passantable = True
                        return True
                    else:
                        # Moved up (or down) too many spaces
                        return False
                elif (
                        moved_piece_old.j == moved_piece_new.j + 1 or moved_piece_old.j == moved_piece_new.j - 1) and moved_piece_new.i == moved_piece_old.i + 1:
                    # Moved diagonally to capture something
                    for piece in new_board.white_pieces:
                        if (piece.i == moved_piece_new.i and piece.j == moved_piece_new.j) or (
                                piece.value == PAWN and piece.en_passantable and piece.i == moved_piece_new.i - 1 and piece.j == moved_piece_new.j):
                            return True

                    # No capturable piece on this spot
                    return False
                # Moved sideways illegally
                return False

        elif moved_piece_old.value == BISHOP:
            # CHECK IF LEGAL BISHOP MOVE
            # Check if it was moved in a straight diagonal line
            if not (abs(moved_piece_old.i - moved_piece_new.i) == abs(moved_piece_old.j - moved_piece_new.j)):
                return False

            # Check if there were no positions occupied by other pieces between old and new position
            if moved_piece_old.i < moved_piece_new.i and moved_piece_old.j < moved_piece_new.j:
                # Went to bottom right
                for n in range(1, moved_piece_new.i - moved_piece_old.i):
                    if self.get_piece(moved_piece_old.i + n, moved_piece_old.j + n) is not None:
                        return False
                return True
            elif moved_piece_old.i < moved_piece_new.i and moved_piece_old.j > moved_piece_new.j:
                # Went to bottom left
                for n in range(1, moved_piece_new.i - moved_piece_old.i):
                    if self.get_piece(moved_piece_old.i + n, moved_piece_old.j - n) is not None:
                        return False
                return True
            elif moved_piece_old.i > moved_piece_new.i and moved_piece_old.j < moved_piece_new.j:
                # Went to top right
                for n in range(1, moved_piece_old.i - moved_piece_new.i):
                    if self.get_piece(moved_piece_old.i - n, moved_piece_old.j + n) is not None:
                        return False
                return True
            else:
                # Went to top left
                for n in range(1, moved_piece_old.i - moved_piece_new.i):
                    if self.get_piece(moved_piece_old.i - n, moved_piece_old.j - n) is not None:
                        return False
                return True

        elif moved_piece_old.value == ROOK:
            # CHECK IF LEGAL ROOK MOVE
            # Check if it was moved in a straight horizontal or vertical line
            if moved_piece_old.i != moved_piece_new.i and moved_piece_old.j != moved_piece_new.j:
                return False

            # Check if there were no positions occupied by other pieces between old and new position
            if moved_piece_old.j < moved_piece_new.j:
                # Went to right
                for n in range(1, moved_piece_new.j - moved_piece_old.j):
                    if self.get_piece(moved_piece_old.i, moved_piece_old.j + n) is not None:
                        return False
                return True
            elif moved_piece_old.j > moved_piece_new.j:
                # Went to left
                for n in range(1, moved_piece_old.j - moved_piece_new.j):
                    if self.get_piece(moved_piece_old.i, moved_piece_old.j - n) is not None:
                        return False
                return True
            elif moved_piece_old.i < moved_piece_new.i:
                for n in range(1, moved_piece_new.i - moved_piece_old.i):
                    if self.get_piece(moved_piece_old.i + n, moved_piece_old.j) is not None:
                        return False
                return True
            else:
                # Went to top
                for n in range(1, moved_piece_old.i - moved_piece_new.i):
                    if self.get_piece(moved_piece_old.i - n, moved_piece_old.j) is not None:
                        return False
                return True

        elif moved_piece_old.value == KNIGHT:
            # CHECK IF LEGAL KNIGHT MOVE
            return (abs(moved_piece_old.i - moved_piece_new.i) == 2 and abs(
                moved_piece_old.j - moved_piece_new.j) == 1) or \
                   (abs(moved_piece_old.i - moved_piece_new.i) == 1 and abs(moved_piece_old.j - moved_piece_new.j) == 2)

        elif moved_piece_old.value == QUEEN:
            # CHECK IF LEGAL QUEEN MOVE
            # Check if it was moved in a straight diagonal, horizontal or vertical line
            if abs(moved_piece_old.i - moved_piece_new.i) != abs(moved_piece_old.j - moved_piece_new.j) and \
                    moved_piece_old.i != moved_piece_new.i and moved_piece_old.j != moved_piece_new.j:
                return False

            if moved_piece_old.i != moved_piece_new.i and moved_piece_old.j != moved_piece_new.j:
                # Diagonal check (Bishop)
                # Check if there were no positions occupied by other pieces between old and new position
                if moved_piece_old.i < moved_piece_new.i and moved_piece_old.j < moved_piece_new.j:
                    # Went to bottom right
                    for n in range(1, moved_piece_new.i - moved_piece_old.i):
                        if self.get_piece(moved_piece_old.i + n, moved_piece_old.j + n) is not None:
                            return False
                    return True
                elif moved_piece_old.i < moved_piece_new.i and moved_piece_old.j > moved_piece_new.j:
                    # Went to bottom left
                    for n in range(1, moved_piece_new.i - moved_piece_old.i):
                        if self.get_piece(moved_piece_old.i + n, moved_piece_old.j - n) is not None:
                            return False
                    return True
                elif moved_piece_old.i > moved_piece_new.i and moved_piece_old.j < moved_piece_new.j:
                    # Went to top right
                    for n in range(1, moved_piece_old.i - moved_piece_new.i):
                        if self.get_piece(moved_piece_old.i - n, moved_piece_old.j + n) is not None:
                            return False
                    return True
                else:
                    # Went to top left
                    for n in range(1, moved_piece_old.i - moved_piece_new.i):
                        if self.get_piece(moved_piece_old.i - n, moved_piece_old.j - n) is not None:
                            return False
                    return True
            else:
                # Vertical and horizontal check (Rook)
                # Check if there were no positions occupied by other pieces between old and new position
                if moved_piece_old.j < moved_piece_new.j:
                    # Went to right
                    for n in range(1, moved_piece_new.j - moved_piece_old.j):
                        if self.get_piece(moved_piece_old.i, moved_piece_old.j + n) is not None:
                            return False
                    return True
                elif moved_piece_old.j > moved_piece_new.j:
                    # Went to left
                    for n in range(1, moved_piece_old.j - moved_piece_new.j):
                        if self.get_piece(moved_piece_old.i, moved_piece_old.j - n) is not None:
                            return False
                    return True
                elif moved_piece_old.i < moved_piece_new.i:
                    for n in range(1, moved_piece_new.i - moved_piece_old.i):
                        if self.get_piece(moved_piece_old.i + n, moved_piece_old.j) is not None:
                            return False
                    return True
                else:
                    # Went to top
                    for n in range(1, moved_piece_old.i - moved_piece_new.i):
                        if self.get_piece(moved_piece_old.i - n, moved_piece_old.j) is not None:
                            return False
                    return True

        elif moved_piece_old.value == KING:
            # CHECK IF LEGAL KING MOVE
            if abs(moved_piece_old.i - moved_piece_new.i) <= 1 and abs(moved_piece_old.j - moved_piece_new.j) <= 1:
                return True

            # CHECK IF CASTLED
            if self.king_under_attack(moved_piece_old.colour):
                return False
            if moved_piece_old.i == moved_piece_new.i and abs(moved_piece_old.j - moved_piece_new.j) == 2 and \
                    not moved_piece_old.has_moved:
                if moved_piece_old.j > moved_piece_new.j:
                    # WENT TO THE LEFT
                    # CHECK IF THE NEXT PIECE IN LEFT DIRECTION IS AN UNMOVED ROOK
                    index = moved_piece_old.j
                    while index > 1:
                        index -= 1
                        if self.get_piece(moved_piece_old.i, index) is not None:
                            return False
                    # No blocking piece found
                    possible_rook = self.get_piece(moved_piece_old.i, 0)
                    if possible_rook is None or possible_rook.value != ROOK or possible_rook.colour != moved_piece_old.colour or possible_rook.has_moved:
                        return False
                    # CHECK IF KING IS SAFE AFTER MOVING ROOK
                    correct_gs = Gamestate([piece for piece in new_board.white_pieces if piece != possible_rook] + [
                        Rook((possible_rook.i, moved_piece_new.j + 1), WHITE, True) for _ in range(1) if
                        moved_piece_old.colour == WHITE],
                                           [piece for piece in new_board.black_pieces if piece != possible_rook] + [
                                               Rook((possible_rook.i, moved_piece_new.j + 1), BLACK, True) for _ in
                                               range(1) if
                                               moved_piece_old.colour == BLACK])
                    if correct_gs.king_under_attack(moved_piece_old.colour):
                        return False

                    # CHECK IF 2 SQUARES ARE NOT ATTACKABLE

                    check_gs_1 = Gamestate([piece for piece in self.white_pieces if piece != moved_piece_old] + [
                        King((moved_piece_old.i, moved_piece_old.j - 1), WHITE, True) for i in range(1) if
                        moved_piece_old.colour == WHITE],
                                           [piece for piece in self.black_pieces if piece != moved_piece_old] + [
                                               King((moved_piece_old.i, moved_piece_old.j - 1), BLACK, True) for i in
                                               range(1) if
                                               moved_piece_old.colour == BLACK])

                    check_gs_2 = Gamestate(
                        [piece for piece in self.white_pieces if piece != moved_piece_old] + [
                            King((moved_piece_old.i, moved_piece_old.j - 2), WHITE, True) for _ in range(1) if
                            moved_piece_old.colour == WHITE],
                        [piece for piece in self.black_pieces if piece != moved_piece_old] + [
                            King((moved_piece_old.i, moved_piece_old.j - 2), BLACK, True) for _ in range(1) if
                            moved_piece_old.colour == BLACK])

                    return not check_gs_1.king_under_attack(moved_piece_old.colour) and not \
                        check_gs_2.king_under_attack(moved_piece_old.colour)
                else:
                    # WENT TO THE RIGHT
                    index = moved_piece_old.j
                    while index < 6:
                        index += 1
                        if self.get_piece(moved_piece_old.i, index) is not None:
                            return False
                    # No blocking piece found
                    possible_rook = self.get_piece(moved_piece_old.i, 7)
                    if possible_rook is None or possible_rook.value != ROOK or possible_rook.colour != moved_piece_old.colour or possible_rook.has_moved:
                        return False
                    # CHECK IF KING IS SAFE AFTER MOVING ROOK
                    correct_gs = Gamestate([piece for piece in new_board.white_pieces if piece != possible_rook] + [
                        Rook((possible_rook.i, moved_piece_new.j - 1), WHITE, True) for _ in range(1) if
                        moved_piece_old.colour == WHITE],
                                           [piece for piece in new_board.black_pieces if piece != possible_rook] + [
                                               Rook((possible_rook.i, moved_piece_new.j - 1), BLACK, True) for _ in
                                               range(1) if
                                               moved_piece_old.colour == BLACK])
                    if correct_gs.king_under_attack(moved_piece_old.colour):
                        return False

                    # CHECK IF 2 SQUARES ARE NOT ATTACKABLE

                    check_gs_1 = Gamestate([piece for piece in self.white_pieces if piece != moved_piece_old] + [
                        King((moved_piece_old.i, moved_piece_old.j + 1), WHITE, True) for i in range(1) if
                        moved_piece_old.colour == WHITE],
                                           [piece for piece in self.black_pieces if piece != moved_piece_old] + [
                                               King((moved_piece_old.i, moved_piece_old.j + 1), BLACK, True) for i in
                                               range(1) if
                                               moved_piece_old.colour == BLACK])

                    check_gs_2 = Gamestate(
                        [piece for piece in self.white_pieces if piece != moved_piece_old] + [
                            King((moved_piece_old.i, moved_piece_old.j + 2), WHITE, True) for _ in range(1) if
                            moved_piece_old.colour == WHITE],
                        [piece for piece in self.black_pieces if piece != moved_piece_old] + [
                            King((moved_piece_old.i, moved_piece_old.j + 2), BLACK, True) for _ in range(1) if
                            moved_piece_old.colour == BLACK])

                    return not check_gs_1.king_under_attack(moved_piece_old.colour) and not \
                        check_gs_2.king_under_attack(moved_piece_old.colour)
            return False

        # NO LEGAL VALUE
        return False

    def generate_captures(self, colour) -> list['Gamestate']:
        pawn_captures = []
        knight_captures = []
        bishop_captures = []
        rook_captures = []
        queen_captures = []
        king_captures = []
        if colour == WHITE:
            for piece in self.white_pieces:
                if piece.value == PAWN:
                    possible_en_passanted_pawn_right = self.get_piece(piece.i, piece.j + 1, BLACK)
                    possible_en_passanted_pawn_left = self.get_piece(piece.i, piece.j - 1, BLACK)
                    if self.get_piece(piece.i - 1, piece.j + 1, BLACK) is not None or (
                            possible_en_passanted_pawn_right is not None and possible_en_passanted_pawn_right.value == PAWN and possible_en_passanted_pawn_right.en_passantable):
                        white_pieces = [temp_piece for temp_piece in self.white_pieces if temp_piece != piece] + [
                            Pawn((piece.i - 1, piece.j + 1), WHITE)]
                        new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False, self.move)
                        if self.is_legal(new_gs):
                            pawn_captures += [new_gs]
                    if self.get_piece(piece.i - 1, piece.j - 1, BLACK) is not None or (
                            possible_en_passanted_pawn_left is not None and possible_en_passanted_pawn_left.value == PAWN and possible_en_passanted_pawn_left.en_passantable):
                        white_pieces = [temp_piece for temp_piece in self.white_pieces if temp_piece != piece] + [
                            Pawn((piece.i - 1, piece.j - 1), WHITE)]
                        new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False, self.move)
                        if self.is_legal(new_gs):
                            pawn_captures += [new_gs]

                elif piece.value == KNIGHT:
                    for position in piece.generate_possible_moves():
                        if self.get_piece(position.i, position.j, BLACK) is not None:
                            white_pieces = [temp_piece for temp_piece in self.white_pieces if temp_piece != piece] + [
                                position]
                            new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False,
                                               self.last_non_drawing_turn)
                            if self.is_legal(new_gs):
                                knight_captures += [new_gs]

                elif piece.value == BISHOP:
                    for temp_piece in self.black_pieces:
                        if abs(piece.i - temp_piece.i) == abs(piece.j - temp_piece.j):
                            white_pieces = [temp2_piece for temp2_piece in self.white_pieces if
                                            temp2_piece != piece] + [
                                               Bishop((temp_piece.i, temp_piece.j), WHITE)]
                            new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False,
                                               self.last_non_drawing_turn)
                            if self.is_legal(new_gs):
                                bishop_captures += [new_gs]
                elif piece.value == ROOK:
                    for temp_piece in self.black_pieces:
                        if piece.i == temp_piece.i or piece.j == temp_piece.j:
                            white_pieces = [temp2_piece for temp2_piece in self.white_pieces if
                                            temp2_piece != piece] + [
                                               Rook((temp_piece.i, temp_piece.j), WHITE, True)]
                            new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False,
                                               self.last_non_drawing_turn)
                            if self.is_legal(new_gs):
                                rook_captures += [new_gs]
                elif piece.value == QUEEN:
                    for temp_piece in self.black_pieces:
                        if piece.i == temp_piece.i or piece.j == temp_piece.j or abs(piece.i - temp_piece.i) == abs(
                                piece.j - temp_piece.j):
                            white_pieces = [temp2_piece for temp2_piece in self.white_pieces if
                                            temp2_piece != piece] + [
                                               Queen((temp_piece.i, temp_piece.j), WHITE)]
                            new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False,
                                               self.last_non_drawing_turn)
                            if self.is_legal(new_gs):
                                queen_captures += [new_gs]
                else:
                    for temp_piece in self.black_pieces:
                        if abs(piece.i - temp_piece.i) <= 1 and abs(piece.j - temp_piece.j) <= 1:
                            white_pieces = [temp2_piece for temp2_piece in self.white_pieces if
                                            temp2_piece != piece] + [
                                               King((temp_piece.i, temp_piece.j), WHITE, True)]
                            new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False,
                                               self.last_non_drawing_turn)
                            if self.is_legal(new_gs):
                                king_captures += [new_gs]
        else:
            for piece in self.black_pieces:
                if piece.value == PAWN:
                    possible_en_passanted_pawn_right = self.get_piece(piece.i, piece.j + 1, WHITE)
                    possible_en_passanted_pawn_left = self.get_piece(piece.i, piece.j - 1, WHITE)
                    if self.get_piece(piece.i + 1, piece.j + 1, WHITE) is not None or (
                            possible_en_passanted_pawn_right is not None and possible_en_passanted_pawn_right.value == PAWN and possible_en_passanted_pawn_right.en_passantable):
                        black_pieces = [temp_piece for temp_piece in self.black_pieces if temp_piece != piece] + [
                            Pawn((piece.i + 1, piece.j + 1), BLACK)]
                        new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False, self.move)
                        if self.is_legal(new_gs):
                            pawn_captures += [new_gs]
                    if self.get_piece(piece.i + 1, piece.j - 1, WHITE) is not None or (
                            possible_en_passanted_pawn_left is not None and possible_en_passanted_pawn_left.value == PAWN and possible_en_passanted_pawn_left.en_passantable):
                        black_pieces = [temp_piece for temp_piece in self.black_pieces if temp_piece != piece] + [
                            Pawn((piece.i + 1, piece.j - 1), BLACK)]
                        new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False, self.move)
                        if self.is_legal(new_gs):
                            pawn_captures += [new_gs]

                elif piece.value == KNIGHT:
                    for position in piece.generate_possible_moves():
                        if self.get_piece(position.i, position.j, WHITE) is not None:
                            black_pieces = [temp_piece for temp_piece in self.black_pieces if temp_piece != piece] + [
                                position]
                            new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False,
                                               self.last_non_drawing_turn)
                            if self.is_legal(new_gs):
                                knight_captures += [new_gs]

                elif piece.value == BISHOP:
                    for temp_piece in self.white_pieces:
                        if abs(piece.i - temp_piece.i) == abs(piece.j - temp_piece.j):
                            black_pieces = [temp2_piece for temp2_piece in self.black_pieces if
                                            temp2_piece != piece] + [
                                               Bishop((temp_piece.i, temp_piece.j), BLACK)]
                            new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False,
                                               self.last_non_drawing_turn)
                            if self.is_legal(new_gs):
                                bishop_captures += [new_gs]

                elif piece.value == ROOK:
                    for temp_piece in self.white_pieces:
                        if piece.i == temp_piece.i or piece.j == temp_piece.j:
                            black_pieces = [temp2_piece for temp2_piece in self.black_pieces if
                                            temp2_piece != piece] + [
                                               Rook((temp_piece.i, temp_piece.j), BLACK, True)]
                            new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False,
                                               self.last_non_drawing_turn)
                            if self.is_legal(new_gs):
                                rook_captures += [new_gs]

                elif piece.value == QUEEN:
                    for temp_piece in self.white_pieces:
                        if piece.i == temp_piece.i or piece.j == temp_piece.j or abs(piece.i - temp_piece.i) == abs(
                                piece.j - temp_piece.j):
                            black_pieces = [temp2_piece for temp2_piece in self.black_pieces if
                                            temp2_piece != piece] + [
                                               Queen((temp_piece.i, temp_piece.j), BLACK)]
                            new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False,
                                               self.last_non_drawing_turn)
                            if self.is_legal(new_gs):
                                queen_captures += [new_gs]

                else:
                    for temp_piece in self.white_pieces:
                        if abs(piece.i - temp_piece.i) <= 1 and abs(piece.j - temp_piece.j) <= 1:
                            black_pieces = [temp2_piece for temp2_piece in self.black_pieces if
                                            temp2_piece != piece] + [
                                               King((temp_piece.i, temp_piece.j), BLACK, True)]
                            new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False,
                                               self.last_non_drawing_turn)
                            if self.is_legal(new_gs):
                                king_captures += [new_gs]
        return pawn_captures + knight_captures + bishop_captures + rook_captures + queen_captures + king_captures

    def generate_all_moves(self, colour, return_moved_pieces=False):
        """
A function that returns ALL possible gamestates after colour makes a move
        :param return_moved_pieces: List to return the new Gamestate and the moved piece
        :param colour: WHITE or BLACK
        :return: list[Gamestate] or list[(Gamestate, Piece, Piece)]
        """
        if return_moved_pieces:
            output = []
            if colour == WHITE:
                for piece in self.white_pieces:
                    for new_possible_piece in piece.generate_possible_moves():
                        new_gs = Gamestate([new_possible_piece] + [wp for wp in self.white_pieces if wp != piece],
                                           self.black_pieces, self.move + 1)
                        output.append((new_gs, piece, new_possible_piece))
            elif colour == BLACK:
                for piece in self.black_pieces:
                    for new_possible_piece in piece.generate_possible_moves():
                        new_gs = Gamestate(self.white_pieces,
                                           [new_possible_piece] + [bp for bp in self.black_pieces if bp != piece],
                                           self.move + 1)
                        output.append((new_gs, piece, new_possible_piece))
            return output
        output = []
        if colour == WHITE:
            for piece in self.white_pieces:
                for new_possible_piece in piece.generate_possible_moves():
                    new_gs = Gamestate([new_possible_piece] + [wp for wp in self.white_pieces if wp != piece],
                                       self.black_pieces, self.move + 1)
                    output.append(new_gs)
        elif colour == BLACK:
            for piece in self.black_pieces:
                for new_possible_piece in piece.generate_possible_moves():
                    new_gs = Gamestate(self.white_pieces,
                                       [new_possible_piece] + [bp for bp in self.black_pieces if bp != piece],
                                       self.move + 1)
                    output.append(new_gs)
        return output

    def update(self, target_gamestate: 'Gamestate', trust_me=False, update_string=True):
        """
Updates this gamestate to make the move to 'transform to target_gamestate', while incrementing move counter,
removing captured elements and restoring en-passantable values for pawns of colour that just made move
        :param trust_me: Check to see if move is legal
        :param target_gamestate: desired gamestate
        """
        old_len_white = len(self.white_pieces)
        old_len_black = len(self.black_pieces)
        if not trust_me:
            if not self.is_legal(target_gamestate):
                raise Exception
        moved_piece_old = None
        moved_piece_new = None
        for piece in self.white_pieces:
            if piece not in target_gamestate.white_pieces:
                moved_piece_old = piece
                break
        if moved_piece_old is None:
            for piece in self.black_pieces:
                if piece not in target_gamestate.black_pieces:
                    moved_piece_old = piece
                    break

        for piece in target_gamestate.white_pieces:
            if piece not in self.white_pieces:
                moved_piece_new = piece
                break
        if moved_piece_new is None:
            for piece in target_gamestate.black_pieces:
                if piece not in self.black_pieces:
                    moved_piece_new = piece
        if moved_piece_new.colour == BLACK:
            self.black_pieces = [moved_piece_new] + [piece for piece in self.black_pieces if piece != moved_piece_old]
            self.black_dict.pop((moved_piece_old.i, moved_piece_old.j))
            self.black_dict[(moved_piece_new.i, moved_piece_new.j)] = moved_piece_new
            if moved_piece_old.value == KING and abs(moved_piece_new.j - moved_piece_old.j) == 2:
                # Castle, so we have to update rook that castled
                if moved_piece_new.j > moved_piece_old.j:
                    # MOVED TO RIGHT
                    self.black_pieces.remove(Rook((0, 7), BLACK, False))
                    self.black_pieces.append(Rook((0, moved_piece_new.j - 1), BLACK, True))
                    self.black_dict.pop((0, 7))
                    self.black_dict[0, moved_piece_new.j - 1] = self.black_pieces[-1]
                else:
                    # MOVED TO LEFT
                    self.black_pieces.remove(Rook((0, 0), BLACK, False))
                    self.black_pieces.append(Rook((0, moved_piece_new.j + 1), BLACK, True))
                    self.black_dict.pop((0, 0))
                    self.black_dict[0, moved_piece_new.j + 1] = self.black_pieces[-1]
            # Remove white piece if it's captured
            new_pieces = []
            for piece in self.white_pieces:
                if piece.i == moved_piece_new.i and piece.j == moved_piece_new.j:
                    self.white_dict.pop((piece.i, piece.j))
                else:
                    new_pieces.append(piece)
            self.white_pieces = new_pieces
            for piece in self.white_pieces[:]:
                if piece.value == PAWN:
                    # CHECK IF IT GOT EN-PASSANTED
                    if piece.en_passantable and moved_piece_new.value == PAWN and moved_piece_new.i == piece.i + 1 and moved_piece_new.j == piece.j:
                        self.white_pieces.remove(piece)
                        self.white_dict.pop((piece.i, piece.j))
                    else:
                        piece.en_passantable = False
        else:
            self.white_pieces = [moved_piece_new] + [piece for piece in self.white_pieces if piece != moved_piece_old]
            self.white_dict.pop((moved_piece_old.i, moved_piece_old.j))
            self.white_dict[(moved_piece_new.i, moved_piece_new.j)] = moved_piece_new
            if moved_piece_old.value == KING and abs(moved_piece_new.j - moved_piece_old.j) == 2:
                # Castle, so we have to update rook that castled
                if moved_piece_new.j > moved_piece_old.j:
                    # MOVED TO RIGHT
                    self.white_pieces.remove(Rook((7, 7), WHITE, False))
                    self.white_pieces.append(Rook((7, moved_piece_new.j - 1), WHITE, True))
                    self.white_dict.pop((7, 7))
                    self.white_dict[7, moved_piece_new.j - 1] = self.white_pieces[-1]
                else:
                    # MOVED TO LEFT
                    self.white_pieces.remove(Rook((7, 0), WHITE, False))
                    self.white_pieces.append(Rook((7, moved_piece_new.j + 1), WHITE, True))
                    self.white_dict.pop((7, 0))
                    self.white_dict[7, moved_piece_new.j + 1] = self.white_pieces[-1]
            # Remove black piece if it's captured
            new_pieces = []
            for piece in self.black_pieces:
                if piece.i == moved_piece_new.i and piece.j == moved_piece_new.j:
                    self.black_dict.pop((piece.i, piece.j))
                else:
                    new_pieces.append(piece)
            self.black_pieces = new_pieces
            for piece in self.black_pieces[:]:
                if piece.value == PAWN:
                    # CHECK IF IT GOT EN-PASSANTED
                    if piece.en_passantable and moved_piece_new.value == PAWN and moved_piece_new.i == piece.i - 1 and moved_piece_new.j == piece.j:
                        self.black_pieces.remove(piece)
                        self.black_dict.pop((piece.i, piece.j))
                    else:
                        piece.en_passantable = False
        capture = len(self.white_pieces) != old_len_white or len(self.black_pieces) != old_len_black
        if capture or \
                moved_piece_old.value == PAWN:
            # UPDATE LAST_NON_DRAWING_TURN IF CAPTURE OR PAWN MOVE
            self.last_non_drawing_turn = self.move
        self.move += 1
        if update_string:
            if moved_piece_new.value == KING:
                if moved_piece_new.j - moved_piece_old.j == 2:
                    self.moves += "O-O "
                elif moved_piece_new.j - moved_piece_old.j == -2:
                    self.moves += "O-O-O "
                else:
                    if capture:
                        self.moves += "Kx" + index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
                    else:
                        self.moves += "K" + index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
            elif moved_piece_old.value == PAWN:
                if capture:
                    self.moves += index_to_column[moved_piece_old.j] + "x" + index_to_column[moved_piece_new.j] + \
                                  index_to_row[moved_piece_new.i] + " "
                else:
                    self.moves += index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
            elif moved_piece_old.value == ROOK:
                if capture:
                    self.moves += "Rx" + index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
                else:
                    self.moves += "R" + index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
            elif moved_piece_old.value == QUEEN:
                if capture:
                    self.moves += "Qx" + index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
                else:
                    self.moves += "Q" + index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
            elif moved_piece_old.value == KNIGHT:
                if capture:
                    self.moves += "Nx" + index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
                else:
                    self.moves += "N" + index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
            elif moved_piece_old.value == BISHOP:
                if capture:
                    self.moves += "Bx" + index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
                else:
                    self.moves += "B" + index_to_column[moved_piece_new.j] + index_to_row[moved_piece_new.i] + " "
        self.previous_states.append(self.deep_copy_without_previous_states())

    def draw_board(self, window):
        # Draw Board
        window.fill(GREEN)
        for col in range(COLUMNS):
            for row in range(col % 2, ROWS, 2):
                pg.draw.rect(window, BEIGE, (row * SQUAREWIDTH, col * SQUAREWIDTH, SQUAREWIDTH, SQUAREWIDTH))

        value_to_name = {PAWN: "pawn", KNIGHT: "knight", BISHOP: "bishop", ROOK: "rook", QUEEN: "queen", KING: "king"}
        for piece in self.white_pieces:
            window.blit(self.images[value_to_name.get(piece.value) + "_white"],
                        (piece.j * SQUAREWIDTH, piece.i * SQUAREWIDTH))

        for piece in self.black_pieces:
            window.blit(self.images[value_to_name.get(piece.value) + "_black"],
                        (piece.j * SQUAREWIDTH, piece.i * SQUAREWIDTH))

    def deep_copy(self):
        """
Returns a copy of a gamestate where every piece is a copy of one of the pieces of 'self'
        """
        new_white_pieces = []
        for piece in self.white_pieces:
            if piece.value == PAWN:
                new_white_pieces.append(Pawn((piece.i, piece.j), piece.colour, piece.en_passantable))
            elif piece.value == KING:
                new_white_pieces.append(King((piece.i, piece.j), piece.colour, piece.has_moved))
            elif piece.value == QUEEN:
                new_white_pieces.append(Queen((piece.i, piece.j), piece.colour))
            elif piece.value == ROOK:
                new_white_pieces.append(Rook((piece.i, piece.j), piece.colour, piece.has_moved))
            elif piece.value == BISHOP:
                new_white_pieces.append(Bishop((piece.i, piece.j), piece.colour))
            elif piece.value == KNIGHT:
                new_white_pieces.append(Knight((piece.i, piece.j), piece.colour))
        new_black_pieces = []
        for piece in self.black_pieces:
            if piece.value == PAWN:
                new_black_pieces.append(Pawn((piece.i, piece.j), piece.colour, piece.en_passantable))
            elif piece.value == KING:
                new_black_pieces.append(King((piece.i, piece.j), piece.colour, piece.has_moved))
            elif piece.value == QUEEN:
                new_black_pieces.append(Queen((piece.i, piece.j), piece.colour))
            elif piece.value == ROOK:
                new_black_pieces.append(Rook((piece.i, piece.j), piece.colour, piece.has_moved))
            elif piece.value == BISHOP:
                new_black_pieces.append(Bishop((piece.i, piece.j), piece.colour))
            elif piece.value == KNIGHT:
                new_black_pieces.append(Knight((piece.i, piece.j), piece.colour))
        return Gamestate(new_white_pieces, new_black_pieces, self.move, False, self.last_non_drawing_turn,
                         self.previous_states)

    def computer_makes_move(self, version: int, tree: Tree = None):
        """
Updates 'self' to new gamestate where computer made move, based on 'version'
        :param tree: Tree for opening if necesarry
        :param version: chooses which version decides next move
        """
        if version == 0:
            # SUCKS BUT IS FAST
            self.random_move()
        elif version == 1:
            # SUCKS A LITTLE LESS AND STILL FAST, BUT CAN'T SEE AHEAD
            self.maximize_value()
        elif version == 2:
            # SEES AHEAD BETTER BUT IS SLOW
            if len(self.black_pieces) + len(self.white_pieces) <= 5:
                depth = 4
            elif len(self.black_pieces) + len(self.white_pieces) <= 16:
                depth = 3
            else:
                depth = 3
            move = self.minmax(depth=depth, maximise=(self.move % 2 == 1))[0]
            if move is None:
                self.maximize_value()
            else:
                self.update(move)
        elif version == 3:
            # CAN SEE BETTER AHEAD AND IS FASTER, BUT HAS TROUBLE CHECKMATING
            self.alpha_beta_search(4)
            # CURRENTLY, BEST VERSION WOULD BE ALPHA_BETA_SEARCH() WITH OPENING KNOWLEDGE AND ENDGAME KNOWLEDGE
        elif version == 4:
            if self.move <= 12:
                move_str = self.opening_move(tree)
                if move_str is None:
                    self.alpha_beta_search(3)
                else:
                    move = self.translate(move_str)
                    self.update(move)
            else:
                self.alpha_beta_search(3)

        elif version == 5:
            if self.move <= 12:
                move_str = self.opening_move(tree)
                if move_str is None:
                    self.iterative_deepening()
                else:
                    move = self.translate(move_str)
                    self.update(move)
            else:
                self.iterative_deepening()
        elif version == 6:
            if self.move <= 12:
                move_str = self.opening_move(tree)
                if move_str is None:
                    self.alpha_beta_best(3)
                else:
                    move = self.translate(move_str)
                    self.update(move)
            else:
                self.alpha_beta_best(4)
        elif version == 7:
            if self.move <= 20:
                move_str = self.opening_move(tree)
                if move_str is None:
                    self.iterative_deepening_better()
                else:
                    move = self.translate(move_str)
                    self.update(move)
            else:
                self.iterative_deepening_better()
        else:
            raise Exception

    def random_move(self):
        if self.move % 2 == 1:
            lm = self.legal_moves(WHITE)
        else:
            lm = self.legal_moves(BLACK)
        new_move = lm[randint(0, len(lm) - 1)]
        self.update(new_move)

    def maximize_value(self):
        """
Looks at every possible move it can make and selects one (random) which maximizes sum of values of pieces - sum of
values of pieces of other colour
        """
        best_moves = []
        best_value = None
        if self.move % 2 == 1:
            lm = self.legal_moves(WHITE)
            for move in lm:
                new_gs = self.deep_copy()
                new_gs.update(move, trust_me=True)
                value = new_gs.evaluate_better()
                if best_value is None or value > best_value:
                    best_moves = [move]
                    best_value = value
                elif best_value == value:
                    best_moves.append(move)
        else:
            lm = self.legal_moves(BLACK)
            for move in lm:
                new_gs = self.deep_copy()
                new_gs.update(move, trust_me=True)
                value = new_gs.evaluate(account_for_draw=True)
                if best_value is None or value < best_value:
                    best_moves = [move]
                    best_value = value
                elif best_value == value:
                    best_moves.append(move)
        chosen_move = best_moves[randint(0, len(best_moves) - 1)]
        self.update(chosen_move)

    def minmax(self, depth: int, maximise: bool) -> ('Gamestate', int or float):
        """
Returns the best possible move, based on next best possible move by opponent, based on next best possible move by self,
until depth is reached and simple move is chosen based on piece evaluation
        :param depth:
        :param maximise: Says if function has to minimise or maximum evaluation on this iteration
        """
        maximise_to_colour = {True: WHITE, False: BLACK}
        if depth == 0:
            return None, self.evaluate()
        else:
            # We have to update a gamestate to a new move, and then choose the one with the best eval based on maximise
            best_value = None
            best_move = None
            for move in self.legal_moves(maximise_to_colour.get(maximise)):
                new_gs = self.deep_copy()
                new_gs.update(move)
                # If we want to maximise, opponent wants to minimise and vice versa
                new_move, value = new_gs.minmax(depth=depth - 1, maximise=not maximise)
                if maximise:
                    if best_value is None or value > best_value:
                        best_value = value
                        best_move = move
                else:
                    if best_value is None or value < best_value:
                        best_value = value
                        best_move = move
            if best_value is None:
                if self.white_wins():
                    return None, float('inf')
                if self.black_wins():
                    return None, float('-inf')

                return None, 0
            return best_move, best_value

    def alpha_beta_search(self, max_depth):
        """
Performs a move based on a minmax tree, but in contrast to version 2 uses alpha-beta-pruning for speedup
        :param max_depth:
        """
        if self.move % 2 == 1:
            # WHITE MAKES MOVE
            value, chosen_move = self.alpha_beta_max(max_depth, float('-inf'), float('inf'))
        else:
            # BLACK MAKES MOVE
            value, chosen_move = self.alpha_beta_min(max_depth, float('-inf'), float('inf'))
        if chosen_move is None:
            # Every move leads to same checkmate
            self.maximize_value()
        else:
            # Found a move
            self.update(chosen_move)

    def alpha_beta_max(self, depth: int, alpha: float, beta: float):
        if depth == 0:
            return self.evaluate(), None
        moves = self.legal_moves(WHITE, sort_by_heuristic=True)
        if len(moves) == 0:
            if self.king_under_attack(WHITE):
                # LOSE DUE TO CHECKMATE
                return float('-inf'), None
            # DRAW
            return 0, None
        value = float('-inf')
        move = None
        for turn in moves:
            new_gs = self.deep_copy()
            new_gs.update(turn, trust_me=True, update_string=False)
            value2, turn2 = new_gs.alpha_beta_min(depth - 1, alpha, beta)
            if value2 > value:
                value, move = value2, turn
                alpha = max(alpha, value)
            if value >= beta:
                return value, move
        return value, move

    def alpha_beta_min(self, depth: int, alpha: float, beta: float):
        if depth == 0:
            return self.evaluate(), None
        moves = self.legal_moves(BLACK, sort_by_heuristic=True)
        if len(moves) == 0:
            if self.king_under_attack(BLACK):
                # LOSE DUE TO CHECKMATE
                return float('inf'), None
            # DRAW
            return 0, None
        value = float('inf')
        move = None
        for turn in moves:
            new_gs = self.deep_copy()
            new_gs.update(turn, trust_me=True, update_string=False)
            value2, turn2 = new_gs.alpha_beta_max(depth - 1, alpha, beta)
            if value2 < value:
                value, move = value2, turn
                beta = min(beta, value)
            if value <= alpha:
                return value, move
        return value, move

    def alpha_beta_best(self, max_depth):
        """
    Performs a move based on a minmax tree, but in contrast to version 2 uses alpha-beta-pruning for speedup. Uses
    quiescent search to handle horizon effect
        :param max_depth:
        """
        if self.move % 2 == 1:
            # WHITE MAKES MOVE
            value, chosen_move = self.alpha_beta_max_best(max_depth, float('-inf'), float('inf'))
        else:
            # BLACK MAKES MOVE
            value, chosen_move = self.alpha_beta_min_best(max_depth, float('-inf'), float('inf'))
        if chosen_move is None:
            # Every move leads to same checkmate
            self.maximize_value()
        else:
            # Found a move
            print(f'Current evaluation: {value}')
            self.update(chosen_move)

    def alpha_beta_max_best(self, depth: int, alpha: float, beta: float):
        if depth == 0:
            return self.quiescence_search(alpha, beta, True), None
        moves = self.legal_moves(WHITE, sort_by_heuristic=True)
        if len(moves) == 0:
            if self.king_under_attack(WHITE):
                # LOSE DUE TO CHECKMATE
                return float('-inf'), None
            # DRAW
            return 0, None
        value = float('-inf')
        move = None
        for turn in moves:
            new_gs = self.deep_copy()
            new_gs.update(turn, trust_me=True, update_string=False)
            value2, turn2 = new_gs.alpha_beta_min_best(depth - 1, alpha, beta)
            if value2 > value:
                value, move = value2, turn
                alpha = max(alpha, value)
            if value >= beta:
                return value, move
        return value, move

    def alpha_beta_min_best(self, depth: int, alpha: float, beta: float):
        if depth == 0:
            return self.quiescence_search(alpha, beta, False), None
        moves = self.legal_moves(BLACK, sort_by_heuristic=True)
        if len(moves) == 0:
            if self.king_under_attack(BLACK):
                # LOSE DUE TO CHECKMATE
                return float('inf'), None
            # DRAW
            return 0, None
        value = float('inf')
        move = None
        for turn in moves:
            new_gs = self.deep_copy()
            new_gs.update(turn, trust_me=True, update_string=False)
            value2, turn2 = new_gs.alpha_beta_max_best(depth - 1, alpha, beta)
            if value2 < value:
                value, move = value2, turn
                beta = min(beta, value)
            if value <= alpha:
                return value, move
        return value, move

    def quiescence_search(self, alpha: float, beta: float, is_maximizing: bool):
        """
        Quiescence search to evaluate positions with potential captures or tactical moves.

        :param alpha: Alpha value for pruning
        :param beta: Beta value for pruning
        :param is_maximizing: Boolean indicating if it's the maximizer's turn
        :return: Evaluation score of the quiescence search
        """
        evaluation = self.evaluate_better()
        if is_maximizing:
            if evaluation >= beta:
                return beta
            if evaluation > alpha:
                alpha = evaluation
        else:
            if evaluation <= alpha:
                return alpha
            if evaluation < beta:
                beta = evaluation

        moves = self.generate_captures(colour=WHITE if is_maximizing else BLACK)
        for move in moves:
            new_gs = self.deep_copy()
            new_gs.update(move, trust_me=True, update_string=False)
            evaluation = new_gs.quiescence_search(alpha, beta, not is_maximizing)
            if is_maximizing:
                if evaluation >= beta:
                    return beta
                if evaluation > alpha:
                    alpha = evaluation
            else:
                if evaluation <= alpha:
                    return alpha
                if evaluation < beta:
                    beta = evaluation

        return alpha if is_maximizing else beta

    # Ensure the following methods are defined elsewhere in your class:
    # - self.move
    # - self.evaluate()
    # - self.legal_moves(color=None, sort_by_heuristic=False, captures_only=False)
    # - self.king_under_attack(color)
    # - self.deep_copy()
    # - self.update(move, trust_me, update_string)
    # - self.maximize_value()

    def evaluate_better(self):
        black_king = None
        white_king = None
        output = 0
        if self.move - self.last_non_drawing_turn >= 100:
            return 0
        if self.previous_states.count(self) >= 3:
            return 0

        KnightValue = 300
        KnightValues = [
            [280, 285, 290, 290, 290, 290, 285, 280],
            [280, 285, 290, 290, 290, 290, 285, 280],
            [280, 295, 300, 300, 300, 300, 295, 280],
            [300, 300, 300, 300, 300, 300, 300, 300],
            [300, 300, 300, 300, 300, 300, 300, 300],
            [280, 295, 300, 300, 300, 300, 295, 280],
            [280, 285, 290, 290, 290, 290, 285, 280],
            [280, 285, 290, 290, 290, 290, 285, 280]
        ]
        BishopValue = 310
        RookValue = 500
        QueenValue = 900
        PawnValue = 100
        endgameMaterialStart = RookValue * 2 + BishopValue + KnightValue
        white_pawns = []
        white_pawn_positions = {}
        white_bishops = []
        white_rooks = []
        white_queens = []
        white_knights = []
        black_pawns = []
        black_pawn_positions = {}
        black_bishops = []
        black_rooks = []
        black_queens = []
        black_knights = []
        for piece in self.white_pieces:
            if piece.value == PAWN:
                white_pawns.append(piece)
                white_pawn_positions[piece.j] = white_pawn_positions.get(piece.j, []) + [piece.i]
            elif piece.value == BISHOP:
                white_bishops.append(piece)
            elif piece.value == KNIGHT:
                white_knights.append(piece)
                output += KnightValues[piece.i][piece.j]
            elif piece.value == ROOK:
                white_rooks.append(piece)
            elif piece.value == QUEEN:
                white_queens.append(piece)
            else:
                white_king = piece
        for piece in self.black_pieces:
            if piece.value == PAWN:
                black_pawns.append(piece)
                black_pawn_positions[piece.j] = black_pawn_positions.get(piece.j, []) + [piece.i]
            elif piece.value == BISHOP:
                black_bishops.append(piece)
            elif piece.value == KNIGHT:
                black_knights.append(piece)
                output -= KnightValues[piece.i][piece.j]
            elif piece.value == ROOK:
                black_rooks.append(piece)
            elif piece.value == QUEEN:
                black_queens.append(piece)
            else:
                black_king = piece
        if self.move % 2 == 0:
            opponentMaterialCountWithoutPawns = len(white_queens) * QueenValue + len(white_rooks) * RookValue + len(
                white_bishops) * BishopValue + len(white_knights) * KnightValue
        else:
            opponentMaterialCountWithoutPawns = len(black_queens) * QueenValue + len(black_rooks) * RookValue + len(
                black_bishops) * BishopValue + len(
                black_knights) * KnightValue
        endgameWeight = 1 - min(1.0, opponentMaterialCountWithoutPawns / endgameMaterialStart)
        output += evaluate_pawns(white_pawns, white_pawn_positions, black_pawns, black_pawn_positions)
        for bishop in white_bishops:
            if (bishop.i == bishop.j or bishop.i == 7 - bishop.j) and (bishop.j <= 1 or bishop.j <= 6):
                output += BishopValue + 45
            else:
                output += BishopValue
        for bishop in black_bishops:
            if bishop.i == bishop.j or bishop.i == 7 - bishop.j:
                output = output - (BishopValue + 45)
            else:
                output -= BishopValue
        output += (len(white_queens) - len(black_queens)) * QueenValue
        output += (len(white_rooks) - len(black_rooks)) * RookValue
        output += mop_up_eval(
            len(white_queens) * QueenValue + len(white_rooks) * RookValue + len(white_bishops) * BishopValue + len(
                white_knights) * KnightValue + len(white_pawns) * PawnValue,
            len(black_queens) * QueenValue + len(black_rooks) * RookValue + len(black_bishops) * BishopValue + len(
                black_knights) * KnightValue + len(black_pawns) * PawnValue, white_king, black_king, endgameWeight)
        output += king_pawn_shield(white_pawn_positions, white_king, black_pawn_positions, black_king, endgameWeight)
        return output

    def evaluate(self, account_for_draw=False) -> float:
        """
A heuristic function to make a guess on evaluation of current position without relying on generating on all next moves
        """
        value = 0
        king_under_attack_value = 0.5
        # promote checks
        kuab = self.king_under_attack(BLACK)
        kuaw = self.king_under_attack(WHITE)
        if account_for_draw and self.stalemate():
            return 0
        if kuab:
            lmb = self.legal_moves(BLACK)
            if self.move % 2 == 0 and len(lmb) == 0:
                # WHITE WINS
                return float('inf')
            value += king_under_attack_value
        if kuaw:
            lmw = self.legal_moves(WHITE)
            if self.move % 2 == 1 and len(lmw) == 0:
                # BLACK WINS
                return float('-inf')
            value -= king_under_attack_value

        value += sum(piece.value for piece in self.white_pieces)
        value -= sum(piece.value for piece in self.black_pieces)
        return value

    def opening_move(self, tree: Tree) -> str or None:
        next_known_moves = tree.getNextMoves(self.moves)
        if next_known_moves is None:
            return None
        chosen = next_known_moves[randint(0, len(next_known_moves) - 1)]
        return chosen

    def translate(self, move_str: str) -> 'Gamestate':
        # ASSUME EARLY POSITION SO NO PROMOTIONS YET
        if self.move % 2 == 1:
            # WHITE MOVE
            if move_str[0] == "K":
                white_pieces = [piece for piece in self.white_pieces if piece.value != KING] + [
                    King((row_to_index[move_str[-1]], column_to_index[move_str[-2]]), WHITE, True)]
                new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False, self.last_non_drawing_turn)
                return new_gs
            elif move_str[0] == "Q":
                white_pieces = [piece for piece in self.white_pieces if piece.value != QUEEN] + [
                    Queen((row_to_index[move_str[-1]], column_to_index[move_str[-2]]), WHITE)]
                new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False, self.last_non_drawing_turn)
                return new_gs
            elif move_str[0] == "R":
                for move in self.legal_moves(WHITE):
                    possible_moved_piece = move.get_piece(row_to_index[move_str[-1]], column_to_index[move_str[-2]],
                                                          WHITE)
                    if possible_moved_piece is not None and possible_moved_piece.value == ROOK:
                        return move
            elif move_str[0] == "B":
                white_pieces = [piece for piece in self.white_pieces if piece.value != BISHOP or (piece.i + piece.j) % 2
                                != (row_to_index[move_str[-1]] + column_to_index[move_str[-2]]) % 2] + [
                                   Bishop((row_to_index[move_str[-1]], column_to_index[move_str[-2]]), WHITE)]
                new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False, self.last_non_drawing_turn)
                return new_gs
            elif move_str[0] == "N":
                for move in self.legal_moves(WHITE):
                    possible_moved_piece = move.get_piece(row_to_index[move_str[-1]], column_to_index[move_str[-2]],
                                                          WHITE)
                    if possible_moved_piece is not None and possible_moved_piece.value == KNIGHT:
                        return move
            elif move_str == "O-O":
                white_pieces = [piece for piece in self.white_pieces if piece.value != KING] + [
                    King((7, 6), WHITE, True)]
                new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False, self.last_non_drawing_turn)
                return new_gs
            elif move_str == "O-O-O":
                white_pieces = [piece for piece in self.white_pieces if piece.value != KING] + [
                    King((7, 2), WHITE, True)]
                new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False, self.last_non_drawing_turn)
                return new_gs
            else:
                if len(move_str) == 2:
                    moved_pawn = None
                    double_jump = False
                    for piece in self.white_pieces:
                        if piece.value == PAWN and piece.j == column_to_index[move_str[-2]] and (
                                piece.i == row_to_index[move_str[-1]] + 1 or (
                                piece.i == row_to_index[move_str[-1]] + 2 and self.get_piece(piece.i - 1,
                                                                                             piece.j) is None)):
                            moved_pawn = piece
                            if piece.i == row_to_index[move_str[-1]] + 2:
                                double_jump = True
                    white_pieces = [piece for piece in self.white_pieces if piece != moved_pawn] + \
                                   [Pawn((row_to_index[move_str[-1]], column_to_index[move_str[-2]]), WHITE,
                                         double_jump)]
                    new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False,
                                       self.last_non_drawing_turn)
                    return new_gs
                else:
                    # capture
                    moved_pawn = None
                    for piece in self.white_pieces:
                        if piece.value == PAWN and piece.j == column_to_index[move_str[0]] and piece.i == row_to_index[
                            move_str[-1]] + 1:
                            moved_pawn = piece
                    white_pieces = [piece for piece in self.white_pieces if piece != moved_pawn] + \
                                   [Pawn((row_to_index[move_str[-1]], column_to_index[move_str[-2]]), WHITE,
                                         False)]
                    new_gs = Gamestate(white_pieces, self.black_pieces, self.move + 1, False,
                                       self.last_non_drawing_turn)
                    return new_gs
        else:
            # BLACK MOVE
            if move_str[0] == "K":
                black_pieces = [piece for piece in self.black_pieces if piece.value != KING] + [
                    King((row_to_index[move_str[-1]], column_to_index[move_str[-2]]), BLACK, True)]
                new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False, self.last_non_drawing_turn)
                return new_gs
            elif move_str[0] == "Q":
                black_pieces = [piece for piece in self.black_pieces if piece.value != QUEEN] + [
                    Queen((row_to_index[move_str[-1]], column_to_index[move_str[-2]]), BLACK)]
                new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False, self.last_non_drawing_turn)
                return new_gs
            elif move_str[0] == "R":
                for move in self.legal_moves(BLACK):
                    possible_moved_piece = move.get_piece(row_to_index[move_str[-1]], column_to_index[move_str[-2]],
                                                          BLACK)
                    if possible_moved_piece is not None and possible_moved_piece.value == ROOK:
                        return move
            elif move_str[0] == "B":
                black_pieces = [piece for piece in self.black_pieces if piece.value != BISHOP or (piece.i + piece.j) % 2
                                != (row_to_index[move_str[-1]] + column_to_index[move_str[-2]]) % 2] + [
                                   Bishop((row_to_index[move_str[-1]], column_to_index[move_str[-2]]), BLACK)]
                new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False, self.last_non_drawing_turn)
                return new_gs
            elif move_str[0] == "N":
                for move in self.legal_moves(BLACK):
                    possible_moved_piece = move.get_piece(row_to_index[move_str[-1]], column_to_index[move_str[-2]],
                                                          BLACK)
                    if possible_moved_piece is not None and possible_moved_piece.value == KNIGHT:
                        return move
            elif move_str == "O-O":
                black_pieces = [piece for piece in self.black_pieces if piece.value != KING] + [
                    King((0, 6), BLACK, True)]
                new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False, self.last_non_drawing_turn)
                return new_gs
            elif move_str == "O-O-O":
                black_pieces = [piece for piece in self.black_pieces if piece.value != KING] + [
                    King((0, 2), BLACK, True)]
                new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False, self.last_non_drawing_turn)
                return new_gs
            else:
                if len(move_str) == 2:
                    moved_pawn = None
                    double_jump = False
                    for piece in self.black_pieces:
                        if piece.value == PAWN and piece.j == column_to_index[move_str[-2]] and (
                                piece.i == row_to_index[move_str[-1]] - 1 or (
                                piece.i == row_to_index[move_str[-1]] - 2 and self.get_piece(piece.i + 1,
                                                                                             piece.j) is None)):
                            moved_pawn = piece
                            if piece.i == row_to_index[move_str[-1]] - 2:
                                double_jump = True
                    black_pieces = [piece for piece in self.black_pieces if piece != moved_pawn] + \
                                   [Pawn((row_to_index[move_str[-1]], column_to_index[move_str[-2]]), BLACK,
                                         double_jump)]
                    new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False,
                                       self.last_non_drawing_turn)
                    return new_gs
                else:
                    moved_pawn = None
                    for piece in self.black_pieces:
                        if piece.value == PAWN and piece.j == column_to_index[move_str[0]] and piece.i == row_to_index[
                            move_str[-1]] - 1:
                            moved_pawn = piece
                    black_pieces = [piece for piece in self.black_pieces if piece != moved_pawn] + \
                                   [Pawn((row_to_index[move_str[-1]], column_to_index[move_str[-2]]), BLACK,
                                         False)]
                    new_gs = Gamestate(self.white_pieces, black_pieces, self.move + 1, False,
                                       self.last_non_drawing_turn)
                    return new_gs

    def iterative_deepening(self):
        start_time = time()
        best_move = None
        depth = 1
        ordered_moves = None

        while time() - start_time < 1:
            # print(depth)
            if self.move % 2 == 1:
                # WHITE'S TURN
                _, ordered_moves = self.alpha_beta_max_all(depth, float('-inf'), float('inf'), ordered_moves)
            else:
                # BLACK'S TURN
                _, ordered_moves = self.alpha_beta_min_all(depth, float('-inf'), float('inf'), ordered_moves)
            depth += 1
        if ordered_moves:
            self.update(ordered_moves[0][1])
        else:
            raise Exception

    def alpha_beta_max_all(self, depth: int, alpha: float, beta: float, ordered_moves=None):
        if depth == 0:
            return self.evaluate_better(), None

        if ordered_moves is None:
            moves = list(self.legal_moves(WHITE, sort_by_heuristic=True))
        else:
            moves = [move[1] for move in ordered_moves]
        if len(moves) == 0:
            if self.king_under_attack(WHITE):
                return float('-inf'), None  # Lose due to checkmate
            return 0, None  # Draw

        move_values = []
        for turn in moves:
            new_gs = self.deep_copy()
            new_gs.update(turn, trust_me=True, update_string=False)
            value2, _ = new_gs.alpha_beta_min_all(depth - 1, alpha, beta)
            move_values.append((value2, turn))
            if value2 > alpha:
                alpha = value2
            if alpha >= beta:
                break

        move_values.sort(key=lambda x: x[0], reverse=True)
        return move_values[0][0], move_values

    def alpha_beta_min_all(self, depth: int, alpha: float, beta: float, ordered_moves=None):
        if depth == 0:
            return self.evaluate_better(), None

        if ordered_moves is None:
            moves = list(self.legal_moves(BLACK, sort_by_heuristic=True))
        else:
            moves = [move[1] for move in ordered_moves]
        if len(moves) == 0:
            if self.king_under_attack(BLACK):
                return float('inf'), None  # Lose due to checkmate
            return 0, None  # Draw

        move_values = []
        for turn in moves:
            new_gs = self.deep_copy()
            new_gs.update(turn, trust_me=True, update_string=False)
            value2, _ = new_gs.alpha_beta_max_all(depth - 1, alpha, beta)
            move_values.append((value2, turn))
            if value2 < beta:
                beta = value2
            if beta <= alpha:
                break

        move_values.sort(key=lambda x: x[0])
        return move_values[0][0], move_values

    def iterative_deepening_better(self):
        start_time = time()
        depth = 1
        ordered_moves = None

        while time() - start_time < MAX_TIME:
            print(f'Performing iterative deepening with depth {depth}')
            if self.move % 2 == 1:
                # WHITE'S TURN
                _, ordered_moves = self.alpha_beta_max_all_better(depth, float('-inf'), float('inf'), ordered_moves)
            else:
                # BLACK'S TURN
                _, ordered_moves = self.alpha_beta_min_all_better(depth, float('-inf'), float('inf'), ordered_moves)
            depth += 1
        if ordered_moves:
            self.update(ordered_moves[0][1])
        else:
            raise Exception

    def alpha_beta_max_all_better(self, depth, alpha, beta, ordered_moves=None):
        if depth == 0:
            return self.quiescence_search(alpha, beta, True), None

        if ordered_moves is None:
            moves = list(self.legal_moves(WHITE, sort_by_heuristic=True))
        else:
            moves = [move[1] for move in ordered_moves]
        if len(moves) == 0:
            if self.king_under_attack(WHITE):
                return float('-inf'), None  # Lose due to checkmate
            return 0, None  # Draw

        move_values = []
        for turn in moves:
            new_gs = self.deep_copy()
            new_gs.update(turn, trust_me=True, update_string=False)
            value2, _ = new_gs.alpha_beta_min_all_better(depth - 1, alpha, beta)
            move_values.append((value2, turn))
            if value2 > alpha:
                alpha = value2
            if alpha >= beta:
                break

        move_values.sort(key=lambda x: x[0], reverse=True)
        return move_values[0][0], move_values

    def alpha_beta_min_all_better(self, depth, alpha, beta, ordered_moves=None):
        if depth == 0:
            return self.quiescence_search(alpha, beta, False), None

        if ordered_moves is None:
            moves = list(self.legal_moves(BLACK, sort_by_heuristic=True))
        else:
            moves = [move[1] for move in ordered_moves]
        if len(moves) == 0:
            if self.king_under_attack(BLACK):
                return float('inf'), None  # Lose due to checkmate
            return 0, None  # Draw

        move_values = []
        for turn in moves:
            new_gs = self.deep_copy()
            new_gs.update(turn, trust_me=True, update_string=False)
            value2, _ = new_gs.alpha_beta_max_all_better(depth - 1, alpha, beta)
            move_values.append((value2, turn))
            if value2 < beta:
                beta = value2
            if beta <= alpha:
                break

        move_values.sort(key=lambda x: x[0])
        return move_values[0][0], move_values

    def deep_copy_without_previous_states(self):
        new_white_pieces = []
        for piece in self.white_pieces:
            if piece.value == PAWN:
                new_white_pieces.append(Pawn((piece.i, piece.j), piece.colour, piece.en_passantable))
            elif piece.value == KING:
                new_white_pieces.append(King((piece.i, piece.j), piece.colour, piece.has_moved))
            elif piece.value == QUEEN:
                new_white_pieces.append(Queen((piece.i, piece.j), piece.colour))
            elif piece.value == ROOK:
                new_white_pieces.append(Rook((piece.i, piece.j), piece.colour, piece.has_moved))
            elif piece.value == BISHOP:
                new_white_pieces.append(Bishop((piece.i, piece.j), piece.colour))
            elif piece.value == KNIGHT:
                new_white_pieces.append(Knight((piece.i, piece.j), piece.colour))
        new_black_pieces = []
        for piece in self.black_pieces:
            if piece.value == PAWN:
                new_black_pieces.append(Pawn((piece.i, piece.j), piece.colour, piece.en_passantable))
            elif piece.value == KING:
                new_black_pieces.append(King((piece.i, piece.j), piece.colour, piece.has_moved))
            elif piece.value == QUEEN:
                new_black_pieces.append(Queen((piece.i, piece.j), piece.colour))
            elif piece.value == ROOK:
                new_black_pieces.append(Rook((piece.i, piece.j), piece.colour, piece.has_moved))
            elif piece.value == BISHOP:
                new_black_pieces.append(Bishop((piece.i, piece.j), piece.colour))
            elif piece.value == KNIGHT:
                new_black_pieces.append(Knight((piece.i, piece.j), piece.colour))
        return Gamestate(new_white_pieces, new_black_pieces, self.move, False, self.last_non_drawing_turn,
                         [])


def evaluate_pawns(white_pawns, white_pawn_positions, black_pawns, black_pawn_positions):
    output = 0
    PawnValue = 100
    passedPawnBonuses = [0, 120, 80, 50, 30, 15, 15]
    isolatedPawnPenaltyByCount = [0, -10, -25, -50, -75, -75, -75, -75, -75]
    isolatedCountWhite = 0
    isolatedCountBlack = 0

    output += (len(white_pawns) - len(black_pawns)) * PawnValue
    for column in white_pawn_positions:
        for rij in white_pawn_positions[column]:
            # Promote passed pawns
            if not ((column in black_pawn_positions and min(black_pawn_positions[column]) < rij) or (
                    (column - 1) in black_pawn_positions and min(black_pawn_positions[column - 1]) < rij) or (
                            (column + 1) in black_pawn_positions and min(black_pawn_positions[column + 1]) < rij)):
                output += passedPawnBonuses[rij]

            # Punish isolated pawns
            if not ((column + 1) in white_pawn_positions or (column - 1) in white_pawn_positions):
                isolatedCountWhite += 1

    for column in black_pawn_positions:
        for rij in black_pawn_positions[column]:
            # Promote passed pawns
            if not ((column in white_pawn_positions and max(white_pawn_positions[column]) > rij) or (
                    (column - 1) in white_pawn_positions and max(white_pawn_positions[column - 1]) > rij) or (
                            (column + 1) in white_pawn_positions and max(white_pawn_positions[column + 1]) > rij)):
                output -= passedPawnBonuses[7 - rij]

            # Punish isolated pawns
            if not ((column + 1) in black_pawn_positions or (column - 1) in black_pawn_positions):
                isolatedCountBlack += 1

    output += isolatedPawnPenaltyByCount[isolatedCountWhite] - isolatedPawnPenaltyByCount[isolatedCountBlack]
    return output


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


def opposite(colour):
    if colour == WHITE:
        return BLACK
    return WHITE
