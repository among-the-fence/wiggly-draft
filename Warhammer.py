import os
import json

dataroot = "data/datasources/10th/json/"


def find(unitname, faction_name):
    out = ""
    if unitname:
        unitname = unitname.lower()
    if faction_name:
        faction_name = faction_name.lower().replace(" ", "")
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
                        v["fluff"] = ""
                        max_length = 1998 - len(k)
                        return k + " " + json.dumps(v)[:max_length]
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