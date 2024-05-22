import os
import json
import re

from util.name_matcher import normalize_name
from util.utils import extract_and_clear, remove_empty_fields

fnp_reg = re.compile("Feel No Pain \d\+")
save_reg = re.compile("(\d)+")
class WHUnit:

    def __init__(self, jsonunit):
        self._raw_json = jsonunit
        self.name = extract_and_clear(jsonunit, "name")
        self.normalized_name = normalize_name(self.name)
        self.abilities = remove_empty_fields(extract_and_clear(jsonunit, "abilities"))
        self.stats = extract_and_clear(jsonunit, "stats")
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

    def __str__(self):
        return self._raw_json

    def formatted_stats(self, parent):
        out = ""
        ordered_props = [
            {"key": "m", "display": "M"},
            {"key": "t", "display": "T"},
            {"key": "sv", "display": "SV"},

            {"key": "feelnopain", "display": "FNP"},
            {"key": "w", "display": "W"},
            {"key": "oc", "display": "OC"},
            {"key": "ld", "display": "Ld"}]

        for s in self.stats:
            for p in ordered_props:
                if p['key'] in s:
                    out += f"{p['display']}:**{s[p['key']]}** "

            if self.abilities and 'invul' in self.abilities and 'value' in self.abilities['invul']:
                out += f"Inv: **{self.abilities['invul']['value']}** "
            if self.abilities and 'core' in self.abilities:
                fnp_list = list(filter(fnp_reg.match, self.abilities["core"]))
                if fnp_list and len(fnp_list) > 0:
                    out += f"FNP: **{','.join(fnp_list).replace('Feel No Pain ', '')}** "
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

    @staticmethod
    def extract_numeric(property, stats):
        out = []
        for s in stats:
            matches = save_reg.search(s[property])
            out.append(matches.group())
        return out

    def get_prop(self, propname):
        if propname == "t":
            return [int(p["t"]) for p in self.stats]
        elif propname == "w":
            return [int(p["w"]) for p in self.stats]
        elif propname == "sv":
            return [int(p["sv"].replace("+", "")) for p in self.stats]
        elif propname == "m":
            try:
                return [int(p["m"].replace("\"", "").replace("+", "").replace("-", "")) for p in self.stats]
            except:
                return [0]
        return None


if __name__ == "__main__":
    with open("../../../data/datasources/10th/json/aeldari.json", "r") as file:
        x = json.load(file)
        WHUnit(x["datasheets"][10])

