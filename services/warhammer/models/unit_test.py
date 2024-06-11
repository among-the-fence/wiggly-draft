import unittest

from services.warhammer.Warhammer import Warhammer
from services.warhammer.models.search_params import SearchParams
from services.warhammer.models.unit import WHUnit


class TestUnit(unittest.TestCase):
    def test_parse_variable_stat(self):
        self.assertEqual([1], WHUnit.calculate_variable_stats("1"))
        self.assertEqual([0], WHUnit.calculate_variable_stats("N/A"))
        self.assertEqual([2], WHUnit.calculate_variable_stats("2+"))
        self.assertEqual(["d6", 1, 2,3,4,5, 6], WHUnit.calculate_variable_stats("D6"))
        self.assertEqual(["2d6", 2,3,4,5,6,7,8,9,10,11, 12], WHUnit.calculate_variable_stats("2D6"))
        self.assertEqual(["d3", 1,2, 3], WHUnit.calculate_variable_stats("D3"))
        self.assertEqual(["d3+2", 3,4, 5], WHUnit.calculate_variable_stats("D3 + 2"))
        self.assertEqual(["2d6+1", 3,4,5,6,7,8,9,10,11,12, 13], WHUnit.calculate_variable_stats("2D6 + 1"))
        self.assertEqual(["6d6+1", 7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36, 37], WHUnit.calculate_variable_stats("6D6+1"))

    def test_datacard(self):
        warhammer_data = Warhammer("../../../data/")
        err, unit = warhammer_data.find("Avatar of Khaine", "Elf")
        self.assertEqual('M:10" T:12 SV:2+/4++ W:14 OC:5 LD:6+', unit.unformatted_stats())

        err, unit = warhammer_data.find("Shard of the nightbringin", None)
        self.assertEqual('M:6" T:11 SV:4+/4++/5+++ W:12 OC:4 LD:6+', unit.unformatted_stats())

        err, unit = warhammer_data.find("Troupe", None)
        self.assertEqual('M:8" T:3 SV:6+/4++ W:1 OC:1 LD:6+', unit.unformatted_stats())

    def test_search(self):
        warhammer_data = Warhammer("../../../data/")
        sp = SearchParams(
            {
                "faction": "!=Aeldari",
                "points": ">300",
                "toughness": ">=8,<=10",
                "wounds": ">10",

            }
        )
        self.runsearch(warhammer_data, sp)

        sp = SearchParams(
            {
                "points": ">45,<100"
            }
        )
        self.runsearch(warhammer_data, sp)

        sp = SearchParams(
            {
                "points": "<100,>45"
            }
        )
        self.runsearch(warhammer_data, sp)

    def test_search_keywords(self):
        warhammer_data = Warhammer("../../../data/")
        sp = SearchParams(
            {
                "faction": "orc",
                "keywords": "Deadly Demise,Torrent",
                "points": "<100"
            }
        )
        self.runsearch(warhammer_data, sp)

        sp = SearchParams(
            {
                "faction": "elf",
                "keywords": "lh"
            }
        )
        self.runsearch(warhammer_data, sp)

    @staticmethod
    def runsearch(data, sp):
        units = data.search(sp)
        print(set([u.name for u in units]))
        return units


if __name__ == '__main__':
    unittest.main()
