import unittest
import main

class TestHead(unittest.TestCase):
    def test_move(self):
        head = main.Head((255,255,255))
        head.move()
        self.assertEqual(head.rect.left, 360)
if __name__ == '__main__':
    unittest.main()
