import os
import json

dataroot = "data/datasources/10th/json/"

faction_nickname_map = {
    "aeldari": ["elves", "eldar"],
    "adeptasororitas": ["mommy"],
    "votann": ["dwarves"],
    "worldeaters": ["we"],
}


def normalize_name(name):
    x = name.lower().translate(",\'-ôûâ").replace(" ", "") if name else None
    # if not x == name:
    #     print(name + " " + x)
    return x


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
