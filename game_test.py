import unittest
from copy import deepcopy

from game import Game, Color, Board, Pos, Player

# class GameTest(unittest.TestCase):
#     def setUp(self):
#         self.game = Game()
#     def test_move(self):
#         return self.assertEqual(2+2, 4)


class BoardTest(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.wp = Player(color=Color.WHITE)
        self.combo_board = Board()

    def test_valid_move(self):
        pos1 = Pos(6, 1)
        pos2 = Pos(5, 2)
        self.board.move(self.wp, pos1, pos2)

    def test_positions(self):
        self.assertEqual(self.board[Pos(-1, 2)], Color.WALL)
        self.assertEqual(self.board[Pos(11, 2)], Color.WALL)
        self.board[Pos(1, 2)]

    def test_invalid_move_leap(self):
        pos1 = Pos(8, 9)
        pos2 = Pos(4, 5)
        with self.assertRaises(Board.BadMove):
            self.board.move(self.wp, pos1, pos2)

    def test_invalid_move_overlap(self):
        pos1 = Pos(9, 8)
        pos2 = Pos(8, 9)
        with self.assertRaises(Board.BadMove):
            self.board.move(self.wp, pos1, pos2)

    def test_beating(self):
        self.board[Pos(5, 8)] = Color.BLACK
        pos = Pos(6, 9)
        target = Pos(4, 7)
        self.board.move(self.wp, pos, target)
        self.assertEqual(self.board[Pos(5, 8)], Color.EMPTY)
        self.assertEqual(self.board[pos], Color.EMPTY)
        self.assertEqual(self.board[target], Color.WHITE)

    def test_beating_edge(self):
        self.board[Pos(4, 1)] = Color.WHITE
        pos = Pos(6, 3)
        target = Pos(5, 4)
        print()
        print(self.board)
        print()
        self.board.move(self.wp, pos, target)
        self.assertEqual(self.board[target], Color.WHITE)
        self.assertEqual(self.board[pos], Color.EMPTY)

    def test_combo(self):
        self.board[Pos(5, 8)] = Color.BLACK
        pos = Pos(6, 9)
        target = Pos(4, 7)
        self.board.move(self.wp, pos, target)
        self.assertEqual(self.board[Pos(5, 8)], Color.EMPTY)
        self.assertEqual(self.board[pos], Color.EMPTY)
        self.assertEqual(self.board[target], Color.WHITE)

    def test_bad_combo(self):
        self.board[Pos(5, 8)] = Color.BLACK
        pos = Pos(6, 1)
        target = Pos(5, 2)
        print(self.board)
        with self.assertRaises(Board.BadMove):
            self.board.move(self.wp, pos, target)


if __name__ == '__main__':
    unittest.main()
