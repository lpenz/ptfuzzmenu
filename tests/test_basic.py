"""ptfuzzmenu basic tests"""

# type: ignore

import unittest

import ptfuzzmenu


class TestView(unittest.TestCase):
    def test_version(self):
        ptfuzzmenu.version()
