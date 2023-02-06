import unittest

import main
from models.HeroList import HeroList
from models import Pick


class testUser:
    def __init__(self, name):
        self.display_name = name

class MyTestCase(unittest.TestCase):
    def test_something(self):
        heros = HeroList()
        hero_map = {}
        for h in heros.hero_list:
            h.preload_image()
            hero_map[h.localized_name] = h
        picks = [
            Pick(hero_map["Tidehunter"], testUser("test")),
            Pick(hero_map["Skywrath Mage"], testUser("SOOOOO COOOYL GOGOLD")),
            Pick(hero_map["Outworld Destroyer"], testUser("test")),
            Pick(hero_map["Death Prophet"], testUser("scooty dooty")),
            Pick(hero_map["Dark Willow"], testUser("a b c d e f g h i j k l m n o p")),
            Pick(hero_map["Shadow Fiend"], testUser("jljsfdaljfds jlahsdfhj lkajsdfhl asdlkfjh aslkdjfh lkjashdfiah rfiouh wefoih END")),
        ]
        for p in picks:
            p.hero.hilarious_display_name = p.hero.get_display_name()
        print(picks[0].hero.hilarious_display_name)
        main.collage(picks)

if __name__ == '__main__':
    unittest.main()
