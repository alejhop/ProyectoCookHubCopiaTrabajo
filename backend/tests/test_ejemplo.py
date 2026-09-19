import unittest


class TestEjemplo(unittest.TestCase):

    def setUp(self):
        self.x = 10

    def tearDown(self):
        self.x = 0

    def test_is_1(self):
        self.assertEqual(self.x, 10)
