import json
import random
import re

from discord import Colour

from util.name_matcher import normalize_name
from util.utils import extract_and_clear, remove_empty_fields

fnp_reg = re.compile("Feel No Pain \d\+")
save_reg = re.compile("(\d)+")


class WHUnit:

    def __init__(self, jsonunit, colors):
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
        self.colors = colors
        self.the_rest = jsonunit

    def get_display_name(self):
        out = self.name
        if self.legends:
            out += " 🪦"
        return out

    def __str__(self):
        return self._raw_json

    def get_color(self):
        if type(self.colors) is list:
            out = random.choice(self.colors)
        elif type(self.colors) is Colour:
            out = self.colors
        else:
            out = Colour.random()
        return out

    @staticmethod
    def calculate_variable_stats(stat):
        s = stat.lower()
        if "d" in s:
            x = s.split("d")
            dice_count = 1
            if not x[0] == '':
                dice_count = int(x[0].strip())
            min_roll = dice_count
            mod_split = x[1].split("+")
            dice_size = int(mod_split[0].strip())
            max_roll = dice_count * dice_size
            if len(mod_split) > 1:
                modifier = int(mod_split[1].strip())
                min_roll += modifier
                max_roll += modifier
            return [min_roll, max_roll]
        elif s == "n/a":
            return [0]
        if stat:
            return [int(stat.replace("+", "").replace("-", ""))]
        return []

    def formatted_stats(self, parent):
        out = ""
        ordered_props = [
            {"key": "m", "display": "M"},
            {"key": "t", "display": "T"},
            {"key": "sv", "display": "SV"},
            {"key": "invul", "display": "INV"},
            {"key": "feelnopain", "display": "FNP"},
            {"key": "w", "display": "W"},
            {"key": "oc", "display": "OC"},
            {"key": "ld", "display": "Ld"}]

        for s in self.stats:
            for p in ordered_props:
                if p['key'] in s:
                    out += f"{p['display']}:**{s[p['key']]}** "
                else:
                    if p['key'] == "invul":
                        if self.abilities and 'invul' in self.abilities and 'value' in self.abilities['invul']:
                            out += f"Inv:**{self.abilities['invul']['value']}** "
                    elif p['key'] == "feelnopain":
                        if self.abilities and 'core' in self.abilities:
                            fnp_list = list(filter(fnp_reg.match, self.abilities["core"]))
                            if fnp_list and len(fnp_list) > 0:
                                out += f"FNP:**{','.join(fnp_list).replace('Feel No Pain ', '')}** "
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

    def unformatted_stats(self):
        out = ""
        ordered_props = [
            {"key": "m", "display": "M"},
            {"key": "t", "display": "T"},
            {"key": "sv", "display": "SV"},
            {"key": "invul", "display": "INV"},
            {"key": "feelnopain", "display": "FNP"},
            {"key": "w", "display": "W"},
            {"key": "oc", "display": "OC"},
            {"key": "ld", "display": "Ld"}]

        for s in self.stats:
            for p in ordered_props:
                if p['key'] in s:
                    out += f"{p['display']}:{s[p['key']]}"
                else:
                    if p['key'] == "invul":
                        if self.abilities and 'invul' in self.abilities and 'value' in self.abilities['invul']:
                            out += f"/{self.abilities['invul']['value']}++"
                    elif p['key'] == "feelnopain":
                        if self.abilities and 'core' in self.abilities:
                            fnp_list = list(filter(fnp_reg.match, self.abilities["core"]))
                            if fnp_list and len(fnp_list) > 0:
                                out += f"/{','.join(fnp_list).replace('Feel No Pain ', '')}+++"
        return out

    @staticmethod
    def extract_numeric(property, stats):
        out = []
        for s in stats:
            matches = save_reg.search(s[property])
            out.append(matches.group())
        return out

    def trycastint(self, val):
        try:
            return int(val)
        except:
            return None

    def extract_profile_values(self, value):
        out = []
        for ranged in self.rangedWeapons:
            if 'profiles' in ranged:
                for bp in ranged['profiles']:
                    if value in bp:
                        out.extend(WHUnit.calculate_variable_stats(bp[value]))
        for melee in self.meleeWeapons:
            if 'profiles' in melee:
                for m in melee['profiles']:
                    if value in m:
                        out.extend(WHUnit.calculate_variable_stats(m[value]))
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
        elif propname == "feelnopain":
            if self.abilities and 'core' in self.abilities:
                fnp_list = list(filter(fnp_reg.match, self.abilities["core"]))
                if fnp_list and len(fnp_list) > 0:
                    matches = [int(save_reg.search(fnpentry).group()) for fnpentry in fnp_list]
                    return matches
        elif propname == "invuln":
            if self.abilities and 'invul' in self.abilities and 'value' in self.abilities['invul']:
                out = []
                for aiv in self.abilities['invul']['value']:
                    matches = save_reg.search(aiv)
                    if matches:
                        out.append(int(matches.group()))
                return out
        elif propname == "attacks":
            return self.extract_profile_values("attacks")
        elif propname == "weaponskill":
            return self.extract_profile_values("skill")
        elif propname == "strength":
            return self.extract_profile_values("strength")
        elif propname == "damage":
            return self.extract_profile_values("damage")
        elif propname == "ap":
            return self.extract_profile_values("ap")
        elif propname == "points":
            if self.points:
                return [self.trycastint(p['cost']) for p in self.points]
        return None


if __name__ == "__main__":
    with open("../../../data/datasources/10th/json/aeldari.json", "r") as file:
        x = json.load(file)
        WHUnit(x["datasheets"][10])

