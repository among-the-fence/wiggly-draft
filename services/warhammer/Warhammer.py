import json
import os

from thefuzz import fuzz

from services.warhammer.models.faction import WHFaction
from services.warhammer.models.search_params import SearchParams
from util.name_matcher import name_match_function, normalize_name

faction_nickname_map = {
    "astramilitarum": ["am", "ig", "guard", "imperial guard"],
    "adeptasororitas": ["mommy", "sororitas", "senoritas", "sisters", "sob"],
    "bloodangels": ["ba", "angels", "blood angles"],
    "darkangels": ["da", "angles", "dark angles"],
    "chaosknights": ["ck"],
    "chaosdeamons": ["daemons", "demons"],
    "chaosspacemarines": ["csm", "chaos marines"],
    "deathguard": ["dg"],
    "deathwatch": ["dw"],
    "drukhari": ["dark elves", "dark eldar"],
    "blacktemplars": ["bt"],
    "adeptacustodes": ["custodes"],
    "adeptamechanicus": ["admech"],
    "aeldari": ["elves", "eldar", "aeldar", "eldari", "aeldar", "legalos and friends"],
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
    def __init__(self, dataroot="data/datasources/10th/json/"):
        self.factions = {}
        self.faction_names = []
        for f in os.listdir(dataroot):
            with open(dataroot + f, "r") as file:
                wf = WHFaction(json.load(file))
                self.factions[wf.normalized_name] = wf
                if wf.name:
                    self.faction_names.append(wf.name)
        self.compiled_faction_names = []
        self.compiled_faction_names.extend(self.faction_names)
        for k,v in faction_nickname_map.items():
            self.compiled_faction_names.extend(v)

    def find(self, unitname, faction_name):
        factions = self.get_matching_factions(faction_name)

        unitname = normalize_name(unitname)
        closest_match_ratio = 0
        closest_match_unit = None
        if unitname:
            for i in factions:
                unit, match = self.factions[i].get_unit(unitname)
                # print(f"{unitname} {unit.name} {match}")
                if match >= 99:
                    return None, unit
                elif match > closest_match_ratio:
                    closest_match_unit = unit
                    closest_match_ratio = match
        elif faction_name:
            return None, self.factions[faction_name]
        else:
            return "WTF", None
        # print(f"{closest_match_unit.name} - {unitname} - {closest_match_color} {closest_match_ratio}")
        return None, closest_match_unit

    def search(self, params: SearchParams):
        factions = self.get_matching_factions(params.faction)
        units = []
        for k,i in factions.items():
            if i.units:
                for uk, u in i.units.items():
                    if params.apply(u):
                        units.append({"color": i.get_color(), "unit": u})
        return units

    def get_matching_factions(self, faction_name: str):
        if faction_name:
            invert = "!=" in faction_name
            faction_name = faction_name.replace("!=", "")
            faction_name = self.find_closest_faction_name(faction_name)
            if invert:
                out = {k: v for k, v in self.factions.items() if k != faction_name}
            else:
                out = {faction_name: self.factions[faction_name]}
            return out
        else:
            return self.factions

    def find_closest_faction_name(self, faction_name: str):
        faction_name = normalize_name(faction_name)

        closest_match_name = None
        closest_match_ratio = 30

        for i in self.faction_names:
            r = fuzz.token_sort_ratio(faction_name, i)
            if r > closest_match_ratio:
                closest_match_name = i
                closest_match_ratio = r
        for y, x in faction_nickname_map.items():
            for i in x:
                r = name_match_function(faction_name, i)
                if r > closest_match_ratio:
                    closest_match_name = y
                    closest_match_ratio = r
        for x in self.factions.keys():
            if x:
                if x.replace(" ", "") == closest_match_name:
                    closest_match_name = x
                    break
        print(f"{faction_name} {closest_match_name} {closest_match_ratio}")
        return closest_match_name.lower()

    def get_faction(self, faction_name):
        closest_match_name = self.find_closest_faction_name(faction_name)

        if closest_match_name:
            return None, None, self.factions[closest_match_name]
        else:
            return None, ", ".join(sorted(self.faction_names)), None

    def get_all_faction_names(self):
        return self.compiled_faction_names

warhammer_40k_data = Warhammer()


def get_wh_data():
    return warhammer_40k_data

