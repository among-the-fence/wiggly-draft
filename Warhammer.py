import os
import json

dataroot = "data/datasources/10th/json/"

faction_nickname_map = {
    "aeldari": ["elves", "eldar"],
    "adeptasororitas": ["mommy"],
    "votann": ["dwarves"],
    "worldeaters": ["we"],
}


def find(unitname, faction_name):
    out = ""
    if unitname:
        unitname = unitname.lower()
    if faction_name:
        faction_name = faction_name.lower().replace(" ", "")
    for y,x in faction_nickname_map.items():
        if faction_name in x:
            faction_name = y
    try:
        if not faction_name:
            if not unitname:
                return "Either faction or unit name required"
            for f in os.listdir(dataroot):
                print(f)
                out += f
                faction_name = f.split('.')[0]
                faction = faction_as_map(faction_name)
                for k,v in faction.items():
                    if unitname in k or k in unitname:
                        return v
        else:
            # Faction and no unit
            return ", ".join(faction_as_map(faction_name).keys())
    except Exception as e:
        out += "Welp" + str(e)
    return out


def get_faction(name):
    lname = name.lower()
    with open(dataroot + lname + ".json", "r") as file:
        return json.load(file)


def faction_as_map(name):
    all_info = get_faction(name)
    datasheets = all_info['datasheets']
    datasheetmap = {}
    for d in datasheets:
        datasheetmap[d['name'].lower()] = d
    return datasheetmap