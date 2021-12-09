import json
import unittest

from app import collage, pick_heroes


class MyTestCase(unittest.TestCase):
    def test_collage(self):
        collage([{"name": "npc_dota_hero_dragon_knight", "id": 49, "localized_name": "Dragon Knight", "image": "imagecache/dragon_knight_lg.png", "user": "u5"}, {"name": "npc_dota_hero_bristleback", "id": 99, "localized_name": "Bristleback", "image": "imagecache/bristleback_lg.png", "user": "u1"}, {"name": "npc_dota_hero_pangolier", "id": 120, "localized_name": "Pangolier", "image": "imagecache/pangolier_lg.png", "user": "u2"}, {"name": "npc_dota_hero_weaver", "id": 63, "localized_name": "Weaver", "image": "imagecache/weaver_lg.png", "user": "u6"}, {"name": "npc_dota_hero_enchantress", "id": 58, "localized_name": "Enchantress", "image": "imagecache/enchantress_lg.png", "user": "u4"}, {"name": "npc_dota_hero_juggernaut", "id": 8, "localized_name": "Juggernaut", "image": "imagecache/juggernaut_lg.png", "user": "u3"}]
                )

    def test_pick_heroes(self):
        pass
    print(json.dumps(pick_heroes(["u1", "u2", "u3", "u4", "u5", "u6"]), indent=2))


if __name__ == '__main__':
    unittest.main()
