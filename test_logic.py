
import unittest
from logic import add

class TestLogic(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 2), 4)
        print("\n✅ Validation Successful: Logic is sound.")

if __name__ == '__main__':
    unittest.main()
