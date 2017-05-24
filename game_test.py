import unittest
from copy import deepcopy

from game import Game, Color, Board, Pos

# class GameTest(unittest.TestCase):
#     def setUp(self):
#         self.game = Game()
#     def test_move(self):
#         return self.assertEqual(2+2, 4)


class BoardTest(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_valid_move(self):
        pos1 = Pos(1, 6)
        pos2 = Pos(2, 5)
        self.board.move(pos1, pos2)

    def test_positions(self):
        with self.assertRaises(Board.BadPosition):
            self.board[Pos(-1, 2)]
        with self.assertRaises(Board.BadPosition):
            self.board[Pos(11, 2)]
        self.board[Pos(1, 2)]
        

    def test_invalid_move_leap(self):
        pos1 = Pos(8, 9)
        pos2 = Pos(4, 5)
        with self.assertRaises(Board.BadMove):
            self.board.move(pos1, pos2)

    def test_invalid_move_overlap(self):
        pos1 = Pos(8, 9)
        pos2 = Pos(9, 8)
        with self.assertRaises(Board.BadMove):
            self.board.move(pos1, pos2)

    def test_beating(self):
        self.board.board[5][8] = Color.BLACK
        pos = Pos(9, 6)
        target = Pos(7, 4)
        print(self.board)
        self.board.move(pos, target)
        self.assertEqual(Pos(8, 5), Color.EMPTY)
        self.assertEqual(pos, Color.EMPTY)
        self.assertEqual(target, Color.WHITE)

if __name__ == '__main__':
    unittest.main()
