import unittest

from services.warhammer.models.unit import WHUnit


class TestUnit(unittest.TestCase):
    def test_parse_variable_stat(self):
        print(WHUnit.calculate_variable_stats("1"))
        print(WHUnit.calculate_variable_stats("N/A"))
        print(WHUnit.calculate_variable_stats("2+"))
        print(WHUnit.calculate_variable_stats("D6"))
        print(WHUnit.calculate_variable_stats("2D6"))
        print(WHUnit.calculate_variable_stats("D3"))
        print(WHUnit.calculate_variable_stats("D3 + 2"))
        print(WHUnit.calculate_variable_stats("2D6 + 1"))
        print(WHUnit.calculate_variable_stats("6D6+1"))


if __name__ == '__main__':
    unittest.main()