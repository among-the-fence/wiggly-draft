import os
import json
from util.utils import normalize_name, extract_and_clear



class WHUnit:

    def __init__(self, jsonunit):
        self._raw_json = jsonunit
        self.name = extract_and_clear(jsonunit, "name")
        self.normalized_name = normalize_name(self.name)
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
        self.factions = ", ".join(extract_and_clear(jsonunit, "factions"))
        self.faction_id = extract_and_clear(jsonunit, "faction_id")
        self.id = extract_and_clear(jsonunit, "id")
        self.legends = extract_and_clear(jsonunit, "legends", False)
        self.the_rest = jsonunit

    def formatted_stats(self, parent):
        out = ""
        ordered_props = [
            {"key": "m", "display": "M"},
            {"key": "t", "display": "T"},
            {"key": "sv", "display": "SV"},
            {"key": "w", "display": "W"},
            {"key": "oc", "display": "OC"},
            {"key": "ld", "display": "M"}]

        for s in self.stats:
            for p in ordered_props:
                out += f"{p['display']}:**{s[p['key']]}** "
            if len(self.stats) > 1:
                parent.add_field(name=s["name"],
                             value=out,
                             inline=False)
                out = ""
            else:
                parent.description = out

    def formatted_cost(self):
        out = []
        for p in self.points:
            out.append(f"**{p['models']}** models: **{p['cost']}** points")
        return "\n".join(out)



if __name__ == "__main__":
    with open("../../../data/datasources/10th/json/aeldari.json", "r") as file:
        x = json.load(file)
        WHUnit(x["datasheets"][10])

