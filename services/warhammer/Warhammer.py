import os
import json

from thefuzz import fuzz

from services.warhammer.models.faction import WHFaction
from util.utils import normalize_name

dataroot = "data/datasources/10th/json/"

faction_nickname_map = {
    "astramilitarum": ["am", "ig", "guard", "imperialguard"],
    "adeptasororitas": ["mommy", "sororitas", "senoritas", "sisters", "sob"],
    "bloodangels": ["ba", "angels", "bloodangles"],
    "darkangels": ["da", "angles", "darkangles"],
    "chaosknights": ["ck"],
    "chaosdeamons": ["daemons", "demons"],
    "chaosspacemarines": ["csm", "chaosmarines"],
    "deathguard": ["dg"],
    "deathwatch": ["dw"],
    "drukhari": ["darkelves", "darkeldar"],
    "blacktemplars": ["bt"],
    "adeptacustodes": ["custodes"],
    "adeptamechanicus": ["admech"],
    "aeldari": ["elves", "eldar", "aeldar", "eldari", "aeldar","legalosandfriends"],
    "greyknights": ["gk"],
    "genestealercults": ["gsc", "genestealer", "genestealers"],
    "imperialagents": ["ia"],
    "imperialknights": ["ik"],
    "spacemarines": ["sm", "marines"],
    "spacewolves": ["wolves", "sw"],
    "votann": ["dwarves", "votan", "votann", "lov"],
    "worldeaters": ["we", "eaters"],
    "orks": ["orcs", "ork", "orc"],
    "tyranids": ["nids", "bugs"],
    "tauempire": ["tau", "fish"],
    "thousandsons": ["tsons", "ksons", "1ksons", "dustyboiz", "dustyboys"],
    "necrons": ["necrons", "crons", "zombies"]
}


class Warhammer:
    def __init__(self):
        self.factions = {}
        self.faction_names = []
        for f in os.listdir(dataroot):
            with open(dataroot + f, "r") as file:
                wf = WHFaction(json.load(file))
                self.factions[wf.normalized_name] = wf
                if wf.name:
                    self.faction_names.append(wf.name)
        print(self.faction_names)

    def find(self, unitname, faction_name):
        if faction_name:
            faction_name = self.find_closest_faction_name(faction_name)

        unitname = normalize_name(unitname)
        closest_match_ratio = 0
        closest_match_unit = None
        closest_match_color = None
        if faction_name and unitname:
                unit, color, match = self.factions[faction_name].get_unit(unitname)
                if match >= .99:
                    return None, unit, color
                elif match > closest_match_ratio:
                    closest_match_unit = unit
                    closest_match_ratio = match
                    closest_match_color = color
        elif unitname:
            for i in self.factions.keys():
                unit, color, match = self.factions[i].get_unit(unitname)
                if match >= .99:
                    return None, unit, color
                elif match > closest_match_ratio:
                    closest_match_unit = unit
                    closest_match_ratio = match
                    closest_match_color = color
        elif faction_name:
            return None, self.factions[faction_name].unit_names, self.factions[faction_name].get_color()
        else:
            return "WTF", None, None
        print(f"{closest_match_unit.name} - {unitname} - {closest_match_color} {closest_match_ratio}")
        return None, closest_match_unit, closest_match_color

    def find_closest_faction_name(self, faction_name):
        faction_name = normalize_name(faction_name)

        closest_match_name = None
        closest_match_ratio = 50

        for i in self.faction_names:
            r = fuzz.token_sort_ratio(faction_name, i)
            if r > closest_match_ratio:
                closest_match_name = i
                closest_match_ratio = r
        for y, x in faction_nickname_map.items():
            for i in x:
                r = fuzz.token_sort_ratio(faction_name, i)
                if r > closest_match_ratio:
                    closest_match_name = y
                    closest_match_ratio = r
        print(f"{faction_name} {closest_match_name} {closest_match_ratio}")
        return closest_match_name

    def get_faction(self, faction_name):
        closest_match_name = self.find_closest_faction_name(faction_name)

        if closest_match_name:
            return None, None, self.factions[closest_match_name]
        else:
            return None, ", ".join(sorted(self.faction_names)), None


warhammer_40k_data = Warhammer()


def get_wh_data():
    return warhammer_40k_data

