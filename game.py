import enum
from copy import deepcopy
from itertools import cycle
from string import ascii_uppercase
from collections import namedtuple
from time import time


from ab import minimax


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
    WALL = 3  # position out of bounds

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
        self.moves = []
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
        x, y = key
        if x < 0 or y < 0:
            return Color.WALL
        try:
            return self.board[x][y]
        except IndexError:
            return Color.WALL

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
        opposing = opposing_color(player.type)
        dt = (target - source).abs()
        piece_color, target_color = self[source], self[target]

        # check if move is diagonal
        if abs(dt.x) != abs(dt.y):
            raise BadMoveException(source, target)
        if dt.x > 2:
            raise BadMoveException(source, target, "Jumping too far")
        if dt.x == 2:  # move variant: beating opponent's piece
            middle_pos = (source+target)/2
            middle = self[middle_pos]
            if middle != opposing:
                raise BadMoveException(source, target, "Attack failed - %s %s" % (str(middle_pos), str(middle)))
        # check if colors are right
        if piece_color == Color.EMPTY:  # todo: check if right piece is being moved
            raise BadMoveException(source, target, 'source empty')
        if target_color != Color.EMPTY:
            raise BadMoveException(source, target, 'target not empty')

        # check if move is in right direction
        is_combo = source is self.last_moved_piece  # combo is when we beat with the same piece multiple times
        if not is_combo:
            to_white_edge = target.x > source.x  # move is downwards
            valid_black = to_white_edge and piece_color == Color.BLACK
            valid_white = not to_white_edge and piece_color == Color.WHITE
            if not (valid_black or valid_white):
                raise BadMoveException(source, target, "Jumping in wrong direction (%s)" % str(piece_color))

    def is_moving(self, pos1, pos2):
        return abs(pos2.x-pos1.x) == 1

    def is_jumping(self, pos1, pos2):
        return abs(pos2.x-pos1.x) == 2

    def neighbours_of(self, pos, color):  # left and right one
        dx = -1 if color == Color.WHITE else 1
        if not (1 <= pos.x + dx < 9):
            return []
        dt1, dt2 = Pos(dx, -1), Pos(dx, 1)
        neighbours = []
        neighbor = pos + dt1
        if neighbor.y >= 1 and self[neighbor + dt1] == Color.EMPTY:
            neighbours.append(neighbor)

        neighbor = pos + dt2
        if neighbor.y < 9 and self[neighbor + dt2] == Color.EMPTY:
            neighbours.append(neighbor)
        return neighbours

    def _is_beat_possible(self, player, pos):
        # 2 conditions must be met: neighboring piece is of opposite color and next to that
        # piece is a free cell, so jump is possible
        curr_color = self[pos]
        opponent_color = Color.WHITE if curr_color == Color.BLACK else Color.BLACK
        # check if neighbour is of opposite color
        return any(self[p] == opponent_color for p in self.neighbours_of(pos, curr_color))

    def _get_pieces(self, color):
        for x, row in enumerate(self.board):
            for y, c in enumerate(row):
                if c == color:
                    yield(Pos(x, y))

    def move(self, player, source, target):
        self.validate_move(player, source, target)

        if self.is_moving(source, target):
            # if is moving, check if beating is also possible. Moving is then disallowed.
            # other pieces of that player, that are not currently moved piece
            my_other_pieces = iter(p for p in self._get_pieces(player.type) if p != source)
            for other_piece in my_other_pieces:
                if self._is_beat_possible(player, other_piece):
                    raise BadMoveException(source, target, 'Cant move; beating is possible (%s)' % str(other_piece))
            self[source], self[target] = Color.EMPTY, player.type

        elif self.is_jumping(source, target):
            middle_pos = (source + target) / 2
            opponent = self[middle_pos]
            if opponent == player.type:  # trying to jump over own piece
                raise BadMoveException(source, target, 'Jumping over the same piece (%s to %s over %s)' % (source, target, middle_pos))
            self[source], self[middle_pos], self[target] = Color.EMPTY, Color.EMPTY, player.type
        self.last_moved_piece = target
        self.moves.append((player, source, target))

LET_TO_NUM = {l: n for n, l in enumerate(ascii_uppercase[:10])}
NUM_TO_LET = {n: l for l, n in enumerate(LET_TO_NUM.items())}


class Game:
    def __init__(self):
        self.W, self.B = Player(Color.WHITE), Player(Color.BLACK)
        self.players = cycle([self.W, self.B])
        self.board = Board()
        self.current_player = self.W

    def draw_board(self):
        print(str(self.board))

    def copy(self):
        return deepcopy(self)

    def evaluate_for(self, player):
        score = 0.0
        color = player.type
        opponent = opposing_color(color)
        BEATABLE_WEIGHT = 0.2

        for x, row in enumerate(self.board.board):
            for y, cell in enumerate(row):
                pos = Pos(x, y)
                is_beatable = self.is_beatable(pos, cell)
                weight = BEATABLE_WEIGHT if is_beatable else 1  # if not beatable, weight = 1 (neutral)

                if cell == color:
                    score += 1 * weight
                elif cell == opponent:
                    score -= 1 * weight
        return score

    def is_beatable(self, pos, color):
        dx = 1 if color == Color.WHITE else -1
        opposing = opposing_color(color)
        return self.board[Pos(pos.x + dx, pos.y - 1)] == opposing or self.board[Pos(pos.x + dx, pos.y + 1)] == opposing


    def _raw_move_to_pos(self, raw_move):
        (x, y), *moves = raw_move.split(' ')
        return Pos(int(x), int(y)), [Pos(int(x), int(y)) for x, y in moves]

    def make_raw_move(self, raw_move: str):
        source, targets = self._raw_move_to_pos(raw_move)
        for target in targets:
            self.board.move(self.current_player, source, target)
            source = target

    def make_move(self, source, target):
        self.board.move(self.current_player, source, target)

    def end_turn(self):
        self.current_player = self.B if self.current_player == self.W else self.W

    def is_terminating(self):
        whites = False
        blacks = False
        for row in self.board.board:
            for cell in row:
                blacks = blacks or cell == Color.BLACK
                whites = whites or cell == Color.WHITE
                if whites and blacks:
                    return False
        return True

    def ai_turn(self, depth=3):
        t = time()
        node = Node(self, None,  None)
        score = float('-inf')
        winning_variant = None
        for child in node.children():
            new_score = minimax(child, depth)
            if new_score > score:
                winning_variant = child
        print('new solution found in', time() - t, 's')
        self.board = winning_variant.game.board
        self.end_turn()


def opposing_color(color):
    if color == Color.WHITE:
        return Color.BLACK
    return Color.WHITE


class Node(object):
    directions = [Pos(1,1), Pos(-1,1), Pos(1,-1), Pos(-1,-1) ]
    directions += [d*2 for d in directions]

    def __init__(self, game: Game, source, target):
        self.game = game
        self.source = source
        self.target = target

    def value(self):
        return self.game.evaluate_for(self.game.B)

    def is_terminating(self):
        return self.game.is_terminating()

    def possible_moves(self, piece):
        return iter(d + piece for d in self.directions)

    def children(self):
        # children are about next turn, so this turn must end now
        self.game.end_turn()
        # next player's color
        color = self.game.current_player.type
        # for every piece of that color
        for piece in self.game.board._get_pieces(color):
            # yield nodes with all possible move variants
            for node in self.yield_moves_for(self.game, piece):
                yield node

    def yield_moves_for(self, game: Game, piece: Pos):
        for possible_target in self.possible_moves(piece):
            game_copy = game.copy()
            try:
                game_copy.make_move(piece, possible_target)
                yield Node(game_copy, piece, possible_target)
                # try to make combo
                self.yield_moves_for(game_copy, possible_target)

            except (BadMoveException, BadPositionException):
                pass

if __name__ == '__main__':
    g = Game()
    while not g.is_terminating():
        g.draw_board()
        while True:
            try:
                move = input('your move:')
                g.make_raw_move(move)
                break
            except Exception as e:
                print(e)

        g.ai_turn()
