import unittest

from services.warhammer.models.search_item import SearchItem
from services.warhammer.models.unit import WHUnit


class TestSeachItem(unittest.TestCase):
    def test_split(self):
        s = SearchItem("t", ">5")
        unit = WHUnit({"stats": [{"t": "6"}], "factions": ["A"]})
        s.apply(unit)


if __name__ == '__main__':
    unittest.main()