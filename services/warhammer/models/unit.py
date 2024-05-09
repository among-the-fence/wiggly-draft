import os
import json


def extract_and_clear(jsondata, key, default=None):
    jsonfield = default
    if key in jsondata:
        jsonfield = jsondata[key]
        del jsondata[key]
    return jsonfield


class WHUnit:

    def __init__(self, jsonunit):
        self._raw_json = jsonunit
        self.name = extract_and_clear(jsonunit, "name")
        self.stats = extract_and_clear(jsonunit, "stats")
        self.abilities = extract_and_clear(jsonunit, "abilities")
        self.composition = extract_and_clear(jsonunit, "composition")
        self.rangedWeapons = extract_and_clear(jsonunit, "rangedWeapons")
        self.meleeWeapons = extract_and_clear(jsonunit, "meleeWeapons")
        self.keywords = extract_and_clear(jsonunit, "keywords")
        self.fluff = extract_and_clear(jsonunit, "fluff")
        self.loadout = extract_and_clear(jsonunit, "loadout")
        self.wargear = extract_and_clear(jsonunit, "wargear")
        self.points = extract_and_clear(jsonunit, "points")
        self.transport = extract_and_clear(jsonunit, "transport")
        self.leader = extract_and_clear(jsonunit, "leader")
        self.leads = extract_and_clear(jsonunit, "leads")
        self.leadBy = extract_and_clear(jsonunit, "leadBy")
        self.imperialArmour = extract_and_clear(jsonunit, "imperialArmour")
        self.factions = extract_and_clear(jsonunit, "factions")
        self.faction_id = extract_and_clear(jsonunit, "faction_id")
        self.id = extract_and_clear(jsonunit, "id")
        self.legends = extract_and_clear(jsonunit, "legends", False)


if __name__ == "__main__":
    with open("../../../data/datasources/10th/json/aeldari.json", "r") as file:
        x = json.load(file)
        WHUnit(x["datasheets"][10])

