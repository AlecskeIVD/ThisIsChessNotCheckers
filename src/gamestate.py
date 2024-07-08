from assets.constants import *
import pygame as pg
from pieces.rook import Rook
from pieces.pawn import Pawn
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.queen import Queen


class Gamestate:
    def __init__(self, white_pieces=None, black_pieces=None, move=1, load_images=False):
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
        self.white_pieces = white_pieces
        if not black_pieces:
            black_pieces = [Rook(BP_BLROOK, BLACK), Rook(BP_BRROOK, BLACK), Knight(BP_BLKNIGHT, BLACK),
                            Knight(BP_BRKNIGHT, BLACK), Bishop(BP_BLBISHOP, BLACK), Bishop(BP_BRBISHOP, BLACK),
                            Queen(BP_BQUEEN, BLACK), King(BP_BKING, BLACK)]
            for i in range(COLUMNS):
                black_pieces.append(Pawn((1, i), BLACK))
        self.black_pieces = black_pieces
        self.images = {}
        if load_images:
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
        self.move = move

    def get_piece(self, i, j):
        for piece in self.white_pieces:
            if piece.i == i and piece.j == j:
                return piece
        for piece in self.black_pieces:
            if piece.i == i and piece.j == j:
                return piece
        return None

    def white_wins(self):
        if self.move % 2 == 0 and len(self.legal_moves(BLACK)) == 0 and self.king_under_attack(BLACK):
            return True
        return False

    def black_wins(self):
        if self.move % 2 == 1 and len(self.legal_moves(WHITE)) == 0 and self.king_under_attack(WHITE):
            return True
        return False

    def stalemate(self):
        return (self.move % 2 == 1 and len(self.legal_moves(WHITE)) == 0 and not self.king_under_attack(WHITE)) or \
               (self.move % 2 == 0 and len(self.legal_moves(BLACK)) == 0 and not self.king_under_attack(BLACK))

    def legal_moves(self, colour) -> list['Gamestate']:
        """
A function that returns ALL possible valid gamestates after colour makes a move
        :param colour: WHITE or BLACK
        :return: list[Gamestate]
        """
        output = []
        for move in self.generate_all_moves(colour):
            if self.is_legal(move):
                output.append(move)
        return output

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
        for piece in self.black_pieces:
            if piece.colour == colour and piece.value == KING:
                king = piece
        if king is None:
            raise Exception
        # Check if a rook or queen can attack king from horizontal line
        blocking_piece_found = False
        horizontal_index_left = king.j-1
        horizontal_index_right = king.j+1
        while horizontal_index_left >= 0 and not blocking_piece_found:
            piece = self.get_piece(king.i, horizontal_index_left)
            if piece is not None and (piece.value == ROOK or piece.value == QUEEN) and piece.colour != colour:
                return True
            elif piece is not None:
                blocking_piece_found = True
            else:
                horizontal_index_left -= 1
        blocking_piece_found = False
        while horizontal_index_right < 8 and not blocking_piece_found:
            piece = self.get_piece(king.i, horizontal_index_right)
            if piece is not None and (piece.value == ROOK or piece.value == QUEEN) and piece.colour != colour:
                return True
            elif piece is not None:
                blocking_piece_found = True
            else:
                horizontal_index_right += 1

        # Check if a rook or queen can attack king from vertical line
        blocking_piece_found = False
        vertical_index_up = king.i - 1
        vertical_index_down = king.i + 1
        while vertical_index_up >= 0 and not blocking_piece_found:
            piece = self.get_piece(vertical_index_up, king.j)
            if piece is not None and (piece.value == ROOK or piece.value == QUEEN) and piece.colour != colour:
                return True
            elif piece is not None:
                blocking_piece_found = True
            else:
                vertical_index_up -= 1
        blocking_piece_found = False
        while vertical_index_down < 8 and not blocking_piece_found:
            piece = self.get_piece(vertical_index_down, king.j)
            if piece is not None and (piece.value == ROOK or piece.value == QUEEN) and piece.colour != colour:
                return True
            elif piece is not None:
                blocking_piece_found = True
            else:
                vertical_index_down += 1

        # Check if bishop or queen can attack from diagonal:
        blocking_piece_found = False
        index_tr = 1
        index_tl = 1
        index_br = 1
        index_bl = 1

        # Bottom right
        while king.i + index_br < 8 and king.j + index_br < 8 and not blocking_piece_found:
            piece = self.get_piece(king.i+index_br, king.j+index_br)
            if piece is not None and (piece.value == BISHOP or piece.value == QUEEN) and piece.colour != colour:
                return True
            elif piece is not None:
                blocking_piece_found = True
            else:
                index_br += 1
        blocking_piece_found = False
        # Bottom left
        while king.i + index_bl < 8 and king.j - index_bl >= 0 and not blocking_piece_found:
            piece = self.get_piece(king.i+index_bl, king.j-index_bl)
            if piece is not None and (piece.value == BISHOP or piece.value == QUEEN) and piece.colour != colour:
                return True
            elif piece is not None:
                blocking_piece_found = True
            else:
                index_bl += 1
        blocking_piece_found = False
        # Top right
        while king.i - index_tr >= 0 and king.j + index_tr < 8 and not blocking_piece_found:
            piece = self.get_piece(king.i-index_tr, king.j+index_tr)
            if piece is not None and (piece.value == BISHOP or piece.value == QUEEN) and piece.colour != colour:
                return True
            elif piece is not None:
                blocking_piece_found = True
            else:
                index_tr += 1
        blocking_piece_found = False
        # Top left
        while king.i - index_tl >= 0 and king.j - index_tl >= 0 and not blocking_piece_found:
            piece = self.get_piece(king.i - index_tl, king.j - index_tl)
            if piece is not None and (piece.value == BISHOP or piece.value == QUEEN) and piece.colour != colour:
                return True
            elif piece is not None:
                blocking_piece_found = True
            else:
                index_tl += 1
        piece_top_left = self.get_piece(king.i - 1, king.j - 1)
        piece_top_right = self.get_piece(king.i - 1, king.j + 1)
        piece_bottom_left = self.get_piece(king.i + 1, king.j - 1)
        piece_bottom_right = self.get_piece(king.i + 1, king.j + 1)
        # Check if a pawn can attack king
        if (king.colour == WHITE and ((piece_top_left is not None and piece_top_left.colour == BLACK and piece_top_left.value == PAWN) or (piece_top_right is not None and piece_top_right.colour == BLACK and piece_top_right.value == PAWN))) or (king.colour == BLACK and ((piece_bottom_left is not None and piece_bottom_left.colour == WHITE and piece_bottom_left.value == PAWN) or (piece_bottom_right is not None and piece_bottom_right.colour == WHITE and piece_bottom_right.value == PAWN))):
            return True

        # Check if a knight can attack king
        if colour == WHITE:
            for piece in self.black_pieces:
                if piece.value == KNIGHT and ((abs(piece.i-king.i) == 2 and abs(piece.j-king.j) == 1) or (abs(piece.i-king.i) == 1 and abs(piece.j-king.j) == 2)):
                    return True
        else:
            for piece in self.white_pieces:
                if piece.value == KNIGHT and ((abs(piece.i-king.i) == 2 and abs(piece.j-king.j) == 1) or (abs(piece.i-king.i) == 1 and abs(piece.j-king.j) == 2)):
                    return True

        # Check if other king can attack knight
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
        for piece in self.black_pieces:
            if piece not in new_board.black_pieces:
                moved_piece_old = piece

        for piece in new_board.white_pieces:
            if piece not in self.white_pieces:
                moved_piece_new = piece
        for piece in new_board.black_pieces:
            if piece not in self.black_pieces:
                moved_piece_new = piece

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

        # Check if king is capturable after move made
        if new_board.king_under_attack(moved_piece_old.colour):
            return False

        if moved_piece_old.value == PAWN:
            # CHECK IF LEGAL PAWN MOVE
            if moved_piece_old.colour == WHITE:
                # WHITE PAWNS MOVE UP, SO DECREASING I VALUE
                if moved_piece_old.j == moved_piece_new.j:
                    # if it moved forward, there can be no piece of either colour in front
                    if moved_piece_new.i == moved_piece_old.i-1:
                        for piece in self.white_pieces:
                            if piece.i == moved_piece_new.i and piece.j == moved_piece_new.j:
                                return False
                        for piece in self.black_pieces:
                            if piece.i == moved_piece_new.i and piece.j == moved_piece_new.j:
                                return False
                        return True
                    elif moved_piece_new.i == moved_piece_old.i-2 and moved_piece_old.i == 6:
                        # First move of the pawn, so it's allowed to move two positions up if there's nothing in between
                        for piece in self.white_pieces:
                            if (piece.i == moved_piece_new.i or piece.i == moved_piece_new.i+1) and piece.j == moved_piece_new.j:
                                return False
                        for piece in self.black_pieces:
                            if (piece.i == moved_piece_new.i or piece.i == moved_piece_new.i+1) and piece.j == moved_piece_new.j:
                                return False
                        moved_piece_new.en_passantable = True
                        return True
                    else:
                        # Moved up (or down) too many spaces
                        return False
                elif (moved_piece_old.j == moved_piece_new.j + 1 or moved_piece_old.j == moved_piece_new.j - 1) and moved_piece_new.i == moved_piece_old.i-1:
                    # Moved diagonally to capture something
                    for piece in new_board.black_pieces:
                        if (piece.i == moved_piece_new.i and piece.j == moved_piece_new.j) or (piece.value == PAWN and piece.en_passantable and piece.i == moved_piece_new.i+1 and piece.j == moved_piece_new.j):
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
                            if (piece.i == moved_piece_new.i or piece.i == moved_piece_new.i - 1) and piece.j == moved_piece_new.j:
                                return False
                        for piece in self.black_pieces:
                            if (piece.i == moved_piece_new.i or piece.i == moved_piece_new.i - 1) and piece.j == moved_piece_new.j:
                                return False
                        moved_piece_new.en_passantable = True
                        return True
                    else:
                        # Moved up (or down) too many spaces
                        return False
                elif (moved_piece_old.j == moved_piece_new.j + 1 or moved_piece_old.j == moved_piece_new.j - 1) and moved_piece_new.i == moved_piece_old.i + 1:
                    # Moved diagonally to capture something
                    for piece in new_board.white_pieces:
                        if (piece.i == moved_piece_new.i and piece.j == moved_piece_new.j) or (piece.value == PAWN and piece.en_passantable and piece.i == moved_piece_new.i-1 and piece.j == moved_piece_new.j):
                            return True

                    # No capturable piece on this spot
                    return False
                # Moved sideways illegally
                return False

        elif moved_piece_old.value == BISHOP:
            # CHECK IF LEGAL BISHOP MOVE
            # Check if it was moved in a straight diagonal line
            if not (abs(moved_piece_old.i-moved_piece_new.i) == abs(moved_piece_old.j-moved_piece_new.j)):
                return False

            # Check if there were no positions occupied by other pieces between old and new position
            if moved_piece_old.i < moved_piece_new.i and moved_piece_old.j < moved_piece_new.j:
                # Went to bottom right
                for n in range(1, moved_piece_new.i-moved_piece_old.i):
                    if self.get_piece(moved_piece_old.i+n, moved_piece_old.j+n) is not None:
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
                for n in range(1, moved_piece_new.i - moved_piece_old.i):
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
                for n in range(1, moved_piece_new.j-moved_piece_old.j):
                    if self.get_piece(moved_piece_old.i, moved_piece_old.j + n) is not None:
                        return False
                return True
            elif moved_piece_old.j > moved_piece_new.j:
                # Went to left
                for n in range(1, moved_piece_old.j-moved_piece_new.j):
                    if self.get_piece(moved_piece_old.i, moved_piece_old.j - n) is not None:
                        return False
                return True
            elif moved_piece_old.i < moved_piece_new.i:
                for n in range(1, moved_piece_new.i - moved_piece_old.i):
                    if self.get_piece(moved_piece_old.i+n, moved_piece_old.j) is not None:
                        return False
                return True
            else:
                # Went to top
                for n in range(1, moved_piece_old.i - moved_piece_new.i):
                    if self.get_piece(moved_piece_old.i-n, moved_piece_old.j) is not None:
                        return False
                return True

        elif moved_piece_old.value == KNIGHT:
            # CHECK IF LEGAL KNIGHT MOVE
            return (abs(moved_piece_old.i-moved_piece_new.i) == 2 and abs(moved_piece_old.j-moved_piece_new.j) == 1) or\
                   (abs(moved_piece_old.i-moved_piece_new.i) == 1 and abs(moved_piece_old.j-moved_piece_new.j) == 2)

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
                    for n in range(1, moved_piece_new.i - moved_piece_old.i):
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
            return abs(moved_piece_old.i-moved_piece_new.i) <= 1 and abs(moved_piece_old.j-moved_piece_new.j) <= 1
        # NO LEGAL VALUE
        return False

    def generate_all_moves(self, colour):
        """
A function that returns ALL possible gamestates after colour makes a move
        :param colour: WHITE or BLACK
        :return: list[Gamestate]
        """
        output = []
        if colour == WHITE:
            for piece in self.white_pieces:
                for new_possible_piece in piece.generate_possible_moves():
                    new_gs = Gamestate([wp for wp in self.white_pieces if wp != piece] + [new_possible_piece],
                                       self.black_pieces.copy(), self.move + 1)
                    output.append(new_gs)
        elif colour == BLACK:
            for piece in self.black_pieces:
                for new_possible_piece in piece.generate_possible_moves():
                    new_gs = Gamestate(self.white_pieces.copy(),
                                       [bp for bp in self.black_pieces if bp != piece] + [new_possible_piece],
                                       self.move + 1)
                    output.append(new_gs)
        return output

    def update(self, target_gamestate: 'Gamestate'):
        """
Updates this gamestate to make the move to 'transform to target_gamestate', while incrementing move counter, removing captured elements and
restoring en-passantable values for pawns of colour that just made move
        :param target_gamestate: desired gamestate
        """
        if not self.is_legal(target_gamestate):
            raise Exception
        moved_piece_old = None
        moved_piece_new = None
        for piece in self.white_pieces:
            if piece not in target_gamestate.white_pieces:
                moved_piece_old = piece
        for piece in self.black_pieces:
            if piece not in target_gamestate.black_pieces:
                moved_piece_old = piece

        for piece in target_gamestate.white_pieces:
            if piece not in self.white_pieces:
                moved_piece_new = piece
        for piece in target_gamestate.black_pieces:
            if piece not in self.black_pieces:
                moved_piece_new = piece
        if moved_piece_new.colour == BLACK:
            self.black_pieces = [piece for piece in self.black_pieces if piece != moved_piece_old] + [moved_piece_new]
            # Remove white piece if it's captured
            self.white_pieces = [piece for piece in self.white_pieces if
                                 piece.i != moved_piece_new.i or piece.j != moved_piece_new.j]
            for piece in self.white_pieces[:]:
                if piece.value == PAWN:
                    # CHECK IF IT GOT EN-PASSANTED
                    if piece.en_passantable and moved_piece_new.value == PAWN and moved_piece_new.i == piece.i+1 and moved_piece_new.j == piece.j:
                        self.white_pieces.remove(piece)
                    else:
                        piece.en_passantable = False
        else:
            self.white_pieces = [piece for piece in self.white_pieces if piece != moved_piece_old] + [moved_piece_new]
            # Remove black piece if it's captured
            self.black_pieces = [piece for piece in self.black_pieces if
                                 piece.i != moved_piece_new.i or piece.j != moved_piece_new.j]
            for piece in self.black_pieces[:]:
                if piece.value == PAWN:
                    # CHECK IF IT GOT EN-PASSANTED
                    if piece.en_passantable and moved_piece_new.value == PAWN and moved_piece_new.i == piece.i-1 and moved_piece_new.j == piece.j:
                        self.black_pieces.remove(piece)
                    else:
                        piece.en_passantable = False
        self.move += 1

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
