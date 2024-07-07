# PYGAME CONSTANTS
FPS = 3

# COLOURS
WHITE = 153, 204, 255
BLACK = 0, 0, 0
GREEN = 159, 255, 148
BEIGE = 249, 255, 222

# BOARD
WIDTH, HEIGHT = 720, 720
ROWS, COLUMNS = 8, 8
SQUAREWIDTH = WIDTH//COLUMNS

# PIECES
PAWN = 1
KNIGHT = 3
BISHOP = 4
ROOK = 5
QUEEN = 8
KING = 9

# BEGIN POSITIONS PIECES
"""
Board will look like this:
    (0,0) (0,1) (0,2) (0,3) (0,4) (0,5) (0,6) (0,7)
    (1,0) (1,1) (1,2) (1,3) (1,4) (1,5) (1,6) (1,7)
    (2,0) (2,1) (2,2) (2,3) (2,4) (2,5) (2,6) (2,7)
    (3,0) (3,1) (3,2) (3,3) (3,4) (3,5) (3,6) (3,7)
    (4,0) (4,1) (4,2) (4,3) (4,4) (4,5) (4,6) (4,7)
    (5,0) (5,1) (5,2) (5,3) (5,4) (5,5) (5,6) (5,7)
    (6,0) (6,1) (6,2) (6,3) (6,4) (6,5) (6,6) (6,7)
    (7,0) (7,1) (7,2) (7,3) (7,4) (7,5) (7,6) (7,7)
"""
BP_WLKNIGHT = (7, 1)
BP_WRKNIGHT = (7, 6)
BP_WLBISHOP = (7, 2)
BP_WRBISHOP = (7, 5)
BP_WLROOK = (7, 0)
BP_WRROOK = (7, 7)
BP_WQUEEN = (7, 3)
BP_WKING = (7, 4)

BP_BLKNIGHT = (0, 6)
BP_BRKNIGHT = (0, 1)
BP_BLBISHOP = (0, 5)
BP_BRBISHOP = (0, 2)
BP_BLROOK = (0, 7)
BP_BRROOK = (0, 0)
BP_BQUEEN = (0, 3)
BP_BKING = (0, 4)
