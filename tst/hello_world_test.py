import unittest

from hello_world import hello_world


class TestHelloWorld(unittest.TestCase):

    def test_prints_hello_world(self):
        result = hello_world()
        self.assertEqual('Hello World', result)
