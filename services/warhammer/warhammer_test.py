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
        self.assertEqual(33, len(out))
        out = w.get_matching_factions("necrons")
        self.assertEqual(list(out.keys()), ["necrons"])
        out = w.get_matching_factions("demons")
        self.assertEqual(list(out.keys()), ["chaos daemons"])
        out = w.get_matching_factions("angels,angles")
        self.assertEqual(list(out.keys()), ['blood angels', 'dark angels'])
        out = w.get_matching_factions("!=angels,!=we")
        print(",".join([x if x else ' ' for x in out.keys()]))

    def test_operator_order(self):
        w = Warhammer(data_path)
        sp = SearchParams({"points": "<45,>=20"})
        out = w.search(sp)

        sp2 = SearchParams({"points": ">=20,<45"})
        out2 = w.search(sp2)
        print(",".join([x if x else ' ' for x in out.keys()]))

    def test_search_spaces(self):
        w = Warhammer(data_path)
        sp = SearchParams({"points": "<45, >=20"})
        self.assertTrue(0 < len(w.search(sp)))

        sp = SearchParams({"keywords": "assault , heavy"})
        self.assertTrue(0 < len(w.search(sp)))


if __name__ == '__main__':
    unittest.main()