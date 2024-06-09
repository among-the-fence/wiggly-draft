import unittest

from services.warhammer.Warhammer import Warhammer
from services.warhammer.models.search_params import SearchParams

data_path = "../../data/"


class TestSeachItem(unittest.TestCase):
    def test_split(self):
        w = Warhammer(data_path)
        out = w.search(SearchParams({"toughness": ">10"}))
        print(out)

    def test_name_search(self):
        w = Warhammer(data_path)
        out = w.get_matching_factions(None)
        print(",".join([x if x else ' ' for x in out.keys()]))
        out = w.get_matching_factions("necrons")
        print(",".join([x if x else ' ' for x in out.keys()]))
        out = w.get_matching_factions("demons")
        self.assertEqual(list(out.keys()), ["chaos daemons"])
        out = w.get_matching_factions("demons,we")
        print(",".join([x if x else ' ' for x in out.keys()]))


if __name__ == '__main__':
    unittest.main()