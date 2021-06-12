import unittest
import main

class TestSnake(unittest.TestCase):
    def test_length(self):
        snake = main.Snake(5)
        self.assertEqual(len(snake.parts), 8)
if __name__ == '__main__':
    unittest.main()