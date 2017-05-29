import enum
from itertools import cycle, chain
from string import ascii_uppercase
from collections import namedtuple


class Pos(namedtuple('P', ['x', 'y'])):
    @staticmethod
    def from_str(some_str: str):
        try:
            x, y = some_str
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

    def __mul__(self, other):
        if isinstance(other, Pos):
            return Pos(int(self.x * other.x), int(self.y * other.y))
        return Pos(int(self.x * other), int(self.y * other))
    
    def __truediv__(self, other):
        if isinstance(other, Pos):
            return Pos(int(self.x / other.x), int(self.y / other.y))
        return Pos(int(self.x / other), int(self.y / other))
    

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
        self.last_moved_piece = None
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
        board += '\n  %s' % ' '.join(str(i) for i in range(10))
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

    def validate_move(self, player, source, target):
        self.validate_pos(source)
        self.validate_pos(target)
        dt = (target - source).abs()
        piece_color, target_color = self[source], self[target]

        # check if move is diagonal
        if abs(dt.x) != abs(dt.y):
            raise BadMoveException(source, target)
        if dt.x > 2:
            raise BadMoveException(source, target, "Jumping too far")
        # check if colors are right
        if piece_color == Color.EMPTY:  # todo: check if right piece is being moved
            raise BadMoveException(source, target, 'source empty')
        if target_color != Color.EMPTY:
            raise BadMoveException(source, target, 'target not empty')

        # check if move is in right direction
        is_combo = source is self.last_moved_piece
        if not is_combo:
            to_white_edge = target.x - source.x > 0
            valid_black = to_white_edge and piece_color == Color.BLACK
            valid_white = not to_white_edge and piece_color == Color.WHITE
            if not (valid_black or valid_white):
                raise BadMoveException(source, target, "Jumping in wrong direction (%s)" % str(piece_color))

    def is_moving(self, pos1, pos2):
        return abs(pos2.x-pos1.x) == 1

    def neighbours_of(self, pos, color):  # left and right one
        x = pos.x + (-1 if color == Color.WHITE else 1)
        if  not (0 <= x < 10):
            return []
        neighbours = []
        y = pos.y - 1
        if y >= 0:
            neighbours.append(Pos(x, y))
        y = pos.y + 1
        if y < 10:
            neighbours.append(Pos(x, y))
        return neighbours

    def _is_beat_possible(self, player, pos):
        curr_color = self[pos]
        opponent_color = Color.WHITE if curr_color == Color.BLACK else Color.BLACK
        return any(self[p] == opponent_color for p in self.neighbours_of(pos, curr_color))

    def _get_pieces(self, color):
        for x, row in enumerate(self.board):
            for y, c in enumerate(row):
                if c == color:
                    yield(Pos(x, y))

    def is_jumping(self, pos1, pos2):
        return abs(pos2.x-pos1.x) == 2

    def move(self, player, source, target):
        self.validate_move(player, source, target)

        if self.is_moving(source, target):
            # if is moving, check if beating is also possible. Moving is then disallowed.
            for other_piece in (p for p in self._get_pieces(player.type) if p != source):
                if self._is_beat_possible(player, other_piece):
                    raise BadMoveException(source, target, 'Cant move; beating is possible (%s)' % str(other_piece))
            self[source], self[target] =  Color.EMPTY, player.type
        elif self.is_jumping(source, target):
            middle_pos = (source + target) / 2
            opponent = self[middle_pos]
            if opponent == player.type:  # trying to jump over own piece
                raise BadMoveException(source, target, 'Jumping over the same piece (%s to %s over %s)' % (source, target, middle_pos))
            self[source], self[middle_pos], self[target] =  Color.EMPTY, Color.EMPTY, player.type
        self.last_moved_piece = target

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
        pos, destination = self._raw_move_to_pos(raw_move)
        self.board.move(self.current_player, source, target)
        

    def end_turn(self):
        self.current_player = next(self.players)



def opposing_color(color):
    if color == Color.WHITE:
        return Color.BLACK
    return Color.WHITE


class Node(object):
    directions = [Pos(1,1), Pos(-1,1), Pos(1,-1), Pos(-1,-1) ]
    directions += [d*2 for d in directions]

    def __init__(self, game: Game):
        self.game = game

    def possible_moves(self, piece):
        return iter(d + piece for d in directions)

    def yield_moves_for(self, game: Game, piece: Pos):
        color = self.game.current_player.type
        for possible_target in self.possible_moves(piece):
            game_copy = self.game.copy()
            try:
                game_copy.make_move(piece, possible_target)
                yield Node(game_copy)
                # try to make combo
                self.yield_moves_for(game_copy, possible_target)

            except BadMoveException:
                pass

    def children(self):
        game.next_player()
        color = opposing_color(self.game.current_player.type)
        for piece in self.game.board._get_pieces(color):
            self.yield_moves(self.game, piece)
