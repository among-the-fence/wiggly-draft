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

        if faction_name and unitname:
            return None, self.factions[faction_name].get_unit(unitname), self.factions[faction_name].get_color()
        elif unitname:
            for i in self.factions.keys():
                unit, color = self.factions[i].get_unit(unitname)
                if unit:
                    return None, unit, color
        elif faction_name:
            return None, self.factions[faction_name].unit_names, self.factions[faction_name].get_color()
        else:
            return "WTF", None, None
        return "OH NO", None, None


def find(unitname, faction_name):
    out = ""
    unitname = normalize_name(unitname)
    faction_name = normalize_name(faction_name)
    for y,x in faction_nickname_map.items():
        if faction_name in x:
            faction_name = y
    try:
        if not faction_name:
            if not unitname:
                return "Either faction or unit name required", None
            for f in os.listdir(dataroot):
                out += f", {f}"
                faction_name = f.split('.')[0]
                found, color = check_faction_for_unit(faction_name, unitname)
                if found:
                    return found, color
        else:
            if unitname:
                found, color = check_faction_for_unit(faction_name, unitname)
                if found:
                    return found, color
                return f"{faction_name} {unitname} Not found"
            # Faction and no unit
            return ", ".join(faction_as_map(faction_name)[0].keys()), None

    except Exception as e:
        print(e)
        print(type(e))
        print(e)
        out += f"Welp {e}"
    return out, None


def check_faction_for_unit(normalized_faction_name, normalized_unit_name):
    faction, color = faction_as_map(normalized_faction_name)
    # This is slow
    for k, v in faction.items():
        if normalized_unit_name == k:
            return v, color
    for k, v in faction.items():
        if normalized_unit_name in k or k in normalized_unit_name:
            return v, color
    return None, None

def get_faction(name):
    lname = name.lower()
    with open(dataroot + lname + ".json", "r") as file:
        return json.load(file)


def faction_as_map(name):
    all_info = get_faction(name)
    datasheets = all_info['datasheets']
    datasheetmap = {}
    for d in datasheets:
        datasheetmap[normalize_name(d['name'])] = d

    return datasheetmap, all_info["colours"]['banner']
