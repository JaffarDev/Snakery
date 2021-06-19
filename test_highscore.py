import unittest
import main

class TestHighscore(unittest.TestCase):
    def test_write(self):
        game = main.Game()
        game.write_highscore(5)
        with open("storage/highscore.txt") as reader:
            data = reader.readline()
            self.assertEqual(data, "5")
if __name__ == '__main__':
    unittest.main()