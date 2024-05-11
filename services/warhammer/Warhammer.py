import os
import json
from services.warhammer.models.faction import WHFaction
from util.utils import normalize_name

dataroot = "data/datasources/10th/json/"

faction_nickname_map = {
    "aeldari": ["elves", "eldar"],
    "adeptasororitas": ["mommy"],
    "votann": ["dwarves"],
    "worldeaters": ["we"],
}


class Warhammer:
    def __init__(self):
        self.factions = {}
        self.faction_names = []
        for f in os.listdir(dataroot):
            with open(dataroot + f, "r") as file:
                wf = WHFaction(json.load(file))
                self.factions[wf.normalized_name] = wf
                self.faction_names.append(wf.name)
        print(self.faction_names)

    def find(self, unitname, faction_name):
        faction_name = normalize_name(faction_name)
        for y, x in faction_nickname_map.items():
            if faction_name in x:
                faction_name = y
        unitname = normalize_name(unitname)
        closest_match_ratio = 0
        closest_match_unit = None
        cloest_match_color = None
        if faction_name and unitname:
            return None, self.factions[faction_name].get_unit(unitname), self.factions[faction_name].get_color()
        elif unitname:
            for i in self.factions.keys():
                unit, color, match = self.factions[i].get_unit(unitname)
                if match >= .99:
                    return None, unit, color
                elif match > closest_match_ratio:
                    closest_match_unit = unit
                    closest_match_ratio = match
                    cloest_match_color = color
        elif faction_name:
            return None, self.factions[faction_name].unit_names, self.factions[faction_name].get_color()
        else:
            return "WTF", None, None
        print(f"{closest_match_unit.name} - {unitname} - {cloest_match_color} {closest_match_ratio}")
        return None, closest_match_unit, cloest_match_color

    def get_faction(self, faction_name):
        faction_name = normalize_name(faction_name)
        for y, x in faction_nickname_map.items():
            if faction_name in x:
                faction_name = y
        if faction_name in self.factions:
            return None, None, self.factions[faction_name]
        else:
            return None, self.factions.keys(), None
