import unittest

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
        pos1 = Pos(9, 9)
        pos2 = Pos(8,8)
        self.board.move(pos1, pos2)

    def test_positions(self):
        with self.assertRaises(Board.BadPosition):
            self.board[Pos(-1, 2)]
        with self.assertRaises(Board.BadPosition):
            self.board[Pos(11, 2)]
        self.board[Pos(1, 2)]
        

    def test_invalid_move_leap(self):
        pos1 = Pos(9, 9)
        pos2 = Pos(0,1)
        with self.assertRaises(Board.BadMove):
            self.board.move(pos1, pos2)

    def test_invalid_move_overlap(self):
        pos1 = Pos(9, 9)
        pos2 = Pos(8, 8)
        with self.assertRaises(Board.BadMove):
            self.board.move(pos1, pos2)
        



if __name__ == '__main__':
    unittest.main()
