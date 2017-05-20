import enum
from itertools import cycle
from string import ascii_uppercase
from collections import namedtuple


class Pos(namedtuple('P', ['x', 'y'])):
    @staticmethod
    def from_str(some_str: str):
        try:
            x, y = pos
            x, y = int(x), LET_TO_NUM[y]
        except:
            raise Board.BadPosition(some_str)
        return Pos(x, y)

    def abs(self):
        return Pos(abs(self.x), abs(self.y))

    def __sub__(self, other):
        return Pos(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return self - Pos(0, 0)


    def __add__(self, other):
        return Pos(self.x + other.x, self.y + other.y)



class Color(enum.Enum):
    WHITE = 0
    BLACK = 1
    EMPTY = 2

    def __str__(self):
        if self == Color.WHITE:
            return "O"
        if self == Color.BLACK:
            return "X"
        elif self == Color.EMPTY:
            return "-"


class Player:
    def __init__(self, color: Color):
        self.type = color
    
    def __str__(self):
        if self.type == Color.WHITE:
            return "White"
        elif self.type == Color.BLACK:
            return "Black"


class BadPositionException(Exception):
    def __init__(self, pos):
        self.value = pos
        self.msg = "Bad position (%s)" % repr(pos)


class BadMoveException(Exception):
    def __init__(self, pos1, pos2, msg=''):
        self.value = [pos1, pos2]
        reason = 'Reason: %s' % msg
        self.msg = "Bad move (from %s to %s). %s" % (str(pos1), str(pos2), msg and reason or '')


class Board:
    BadMove = BadMoveException
    BadPosition = BadPositionException

    def __init__(self):
        SIZE = 10
        self.board = [[Color.EMPTY]*SIZE for i in range(SIZE)]
        for row in range(SIZE):
            for col in range(SIZE):
                if row < 4 and (col+row) % 2 == 1:
                    self.board[row][col] = Color.BLACK
                if row >= SIZE - 4 and (col+row) % 2 == 1:
                    self.board[row][col] = Color.WHITE

    def _row_to_str(self, row):
        str_row = " ".join(str(p) for p in row)
        return str_row

    def __str__(self):
        board = ['%d|%s|' % (i, self._row_to_str(row)) for i, row in enumerate(self.board)]
        board = "\n".join(board)
        board += '\n  %s' % ' '.join(ascii_uppercase[:10])
        return board

    def __getitem__(self, key: Pos):
        self.validate_pos(key)
        x, y = key
        return self.board[x][y]

    def __setitem__(self, key: Pos, val: Color):
        self.validate_pos(key)
        x, y = key
        self.board[x][y] = val
    
    def validate_pos(self, pos: Pos):
        if 0 <= pos.x < 10 and 0 <= pos.y < 10:
            return
        raise self.BadPosition(pos)

    def validate_move(self, pos1, pos2):
        self.validate_pos(pos1)
        self.validate_pos(pos2)
        dt = pos2 - pos1
        if dt.abs() != Pos(1, 1):
            raise BadMoveException(pos1, pos2)
        v1, v2 = self[pos1], self[pos2]
        if v2 != Color.EMPTY:
            raise BadMoveException(pos1, pos2, 'target not empty')


    def move(self, pos1, pos2):
        self.validate_move(pos1, pos2)
        try:
            self[pos2], self[pos1] = self[pos1], Color.EMPTY
        except IndexError:
            raise

LET_TO_NUM = {l: n for n, l in enumerate(ascii_uppercase[:10])}
NUM_TO_LET = {n: l for l, n in enumerate(LET_TO_NUM.items())}

class Game:
    def __init__(self):
        self.W, self.B = Player(Color.WHITE), Player(Color.BLACK)
        self.players = cycle([self.W, self.B])
        self.board = Board()
        self.score = {self.W: 0, self.B: 0}

    def draw_board(self):
        print(str(self.board))

    def _raw_move_to_pos(self, raw_move):
        pos, *moves = raw_move.split(' ')
        return Pos(pos), [Pos(move) for move in moves]

    def make_move(self, raw_move: str):
        pos, *destination = self._raw_move_to_pos(raw_move)
        if self.board[pos] != self.current_player.type:
            print("You tried to move opponents' piece, try again")
            self.await_move()

    def loop(self):
        while True:
            self.draw_board()
            self.current_player = next(self.players)
            self.await_move()
# b = Board()
# Game().loop()