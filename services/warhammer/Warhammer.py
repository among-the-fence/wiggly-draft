import json
import os
import re
import string

from thefuzz import fuzz

from services.warhammer.models.faction import WHFaction
from services.warhammer.models.generated.Catalogue import parse
from services.warhammer.models.search_params import SearchParams
from util.name_matcher import name_match_function, normalize_name
from collections import Counter

# adeptus titanicus,,black templar,,basic,emperors children,, ,agents of the imperium,
# ,,,space marines  leviathan,,

faction_nickname_map = {
    "astra militarum": ["am", "ig", "guard", "imperial guard"],
    "adepta sororitas": ["mommy", "sororitas", "senoritas", "sisters", "sob"],
    "blood angels": ["ba", "angels", "blood angles"],
    "dark angels": ["da", "angles", "dark angles"],
    "chaos knights": ["ck"],
    "chaos deamons": ["daemons", "demons"],
    "chaos space marines": ["csm", "chaos marines"],
    "death guard": ["dg"],
    "death watch": ["dw"],
    "drukhari": ["dark elves", "dark eldar"],
    "black templars": ["bt"],
    "adepta custodes": ["custodes"],
    "adepta mechanicus": ["admech"],
    "aeldari": ["elves", "eldar", "aeldar", "eldari", "aeldar", "legalos and friends"],
    "grey knights": ["gk"],
    "genestealer cults": ["gsc", "genestealer", "genestealers"],
    "imperial agents": ["ia"],
    "imperial knights": ["ik"],
    "space marines": ["sm", "marines"],
    "space wolves": ["wolves", "sw"],
    "votann": ["dwarves", "votan", "votann", "lov"],
    "world eaters": ["we", "eaters"],
    "orks": ["orcs", "ork", "orc"],
    "tyranids": ["nids", "bugs"],
    "tau empire": ["tau", "fish"],
    "thousand sons": ["tsons", "ksons", "1ksons", "dustyboiz", "dustyboys"],
    "necrons": ["necrons", "crons", "zombies"]
}

JSON_DATA_PREFIX = "datasources/10th/json/"
XML_DATA_PREFIX = "wh40k-10e/"

tab_remover_reg = re.compile("\s\s+")

class Warhammer:
    def __init__(self, dataroot="data/"):
        self.factions = {}
        self.faction_names = []
        xml_units = {}
        for f in os.listdir(dataroot + XML_DATA_PREFIX):
            if ".cat" in f:
                data = parse(dataroot + XML_DATA_PREFIX + f, silence=True)
                if data.sharedSelectionEntries:
                    for x in data.sharedSelectionEntries.selectionEntry:
                        if x.type_ in ["unit", "model"]:
                            xml_units[x.name] = x
        counts = Counter([])
        # for f in os.listdir(dataroot + JSON_DATA_PREFIX):
        #     with (open(dataroot + JSON_DATA_PREFIX + f, "r") as file):
        #         content = file.read().lower()
        #         words = tab_remover_reg.sub(" ",
        #           content.translate(str.maketrans('', '', string.punctuation))).split(" ")
        #         counts = counts + Counter(words)
        # print("\',\'".join([x[0] for x in counts.most_common(100)]))
        for f in os.listdir(dataroot + JSON_DATA_PREFIX):
            with open(dataroot + JSON_DATA_PREFIX + f, "r") as file:
                wf = WHFaction(json.load(file), xml_units)
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
        for k, i in factions.items():
            if i.units:
                for uk, u in i.units.items():
                    if params.apply(u):
                        units.append(u)
        units = params.filter(units)
        return list(set(units))

    def get_matching_factions(self, search_names_concatenated: str):
        if search_names_concatenated:
            matches = {}
            for faction_name in search_names_concatenated.split(","):
                if faction_name:
                    invert = "!=" in faction_name
                    faction_name = faction_name.replace("!=", "").strip()
                    faction_name = self.find_closest_faction_name(faction_name)
                    if invert:
                        matches.update({k: v for k, v in self.factions.items() if k != faction_name})
                    else:
                        matches.update({faction_name: self.factions[faction_name]})
            return matches
        else:
            return self.factions

    def find_closest_faction_name(self, faction_name: str):
        faction_name = normalize_name(faction_name)

        closest_match_name = None
        closest_match_ratio = 30

        for y, x in faction_nickname_map.items():
            for i in x:
                if i == faction_name:
                    faction_name = y
                    break

        for i in self.faction_names:
            r = fuzz.token_sort_ratio(faction_name, i)
            if r > closest_match_ratio:
                closest_match_name = i
                closest_match_ratio = r
        closest_match_ratio = 0
        for x in self.factions.keys():
            if x:
                r = name_match_function(faction_name, x)
                if r > closest_match_ratio:
                    closest_match_ratio = r
                    closest_match_name = x

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



