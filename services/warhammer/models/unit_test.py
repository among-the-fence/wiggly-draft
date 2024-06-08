import unittest

from services.warhammer.Warhammer import Warhammer
from services.warhammer.models.search_params import SearchParams
from services.warhammer.models.unit import WHUnit


class TestUnit(unittest.TestCase):
    def test_parse_variable_stat(self):
        self.assertEqual([1], WHUnit.calculate_variable_stats("1"))
        self.assertEqual([0], WHUnit.calculate_variable_stats("N/A"))
        self.assertEqual([2], WHUnit.calculate_variable_stats("2+"))
        self.assertEqual([1, 6], WHUnit.calculate_variable_stats("D6"))
        self.assertEqual([2, 12], WHUnit.calculate_variable_stats("2D6"))
        self.assertEqual([1, 3], WHUnit.calculate_variable_stats("D3"))
        self.assertEqual([3, 5], WHUnit.calculate_variable_stats("D3 + 2"))
        self.assertEqual([3, 13], WHUnit.calculate_variable_stats("2D6 + 1"))
        self.assertEqual([7, 37], WHUnit.calculate_variable_stats("6D6+1"))

    def test_datacard(self):
        warhammer_data = Warhammer("../../../data/")
        err, unit = warhammer_data.find("Avatar of Khaine", "Elf")
        self.assertEqual('M:10" T:12 SV:2+/4++ M:14 OC:5 LD:6+', unit.unformatted_stats())

        err, unit = warhammer_data.find("Shard of the nightbringin", None)
        self.assertEqual('M:6" T:11 SV:4+/4++/5+++ M:12 OC:4 LD:6+', unit.unformatted_stats())

        err, unit = warhammer_data.find("Troupe", None)
        self.assertEqual('M:8" T:3 SV:6+/4++ M:1 OC:1 LD:6+', unit.unformatted_stats())

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
        units = warhammer_data.search(sp)
        print(set([u.factions for u in units]))


if __name__ == '__main__':
    unittest.main()
