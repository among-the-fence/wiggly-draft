import unittest

from services.warhammer.Warhammer import Warhammer
from services.warhammer.models.search_item import SearchItem


class TestSeachItem(unittest.TestCase):
    def test_search_item(self):
        warhammer_data = Warhammer("../../../data/")
        err, unit = warhammer_data.find("Avatar of Khaine", "Elf")
        self.assertTrue(SearchItem("t", ">5").apply(unit))
        self.assertTrue(SearchItem("attacks", "<50").apply(unit))
        self.assertTrue(SearchItem("sv", "<3").apply(unit))
        self.assertTrue(SearchItem("sv", "<=3").apply(unit))
        self.assertTrue(SearchItem("sv", "<=2").apply(unit))
        self.assertTrue(SearchItem("sv", ">=2").apply(unit))
        self.assertTrue(SearchItem("sv", ">1").apply(unit))
        self.assertTrue(SearchItem("sv", ">=1").apply(unit))
        self.assertTrue(SearchItem("sv", "2").apply(unit))
        self.assertTrue(SearchItem("sv", "=2").apply(unit))
        self.assertTrue(SearchItem("invuln", "<=5").apply(unit))
        self.assertTrue(SearchItem("m", ">5").apply(unit))
        self.assertTrue(SearchItem("w", "14").apply(unit))
        self.assertTrue(SearchItem("points", ">100").apply(unit))
        self.assertTrue(SearchItem("damage", "d6+2").apply(unit))


if __name__ == '__main__':
    unittest.main()
