import unittest

from services.warhammer.Warhammer import Warhammer
from services.warhammer.models.search_params import SearchParams


class TestSeachItem(unittest.TestCase):
    def test_split(self):
        w = Warhammer("../../data/datasources/10th/json/")
        out = w.search(SearchParams({"toughness": ">10"}))
        print(out)


if __name__ == '__main__':
    unittest.main()