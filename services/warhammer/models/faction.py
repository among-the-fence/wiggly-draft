import os
import json

import discord

from services.warhammer.models.unit import WHUnit
from util.utils import extract_and_clear, normalize_name
import random


class WHFaction:
    def __init__(self, json_faction):

        self.colors = [WHFaction.extract_color(json_faction["colours"][x]) for x in json_faction["colours"]] if "colours" in json_faction else WHFaction.extract_color("#ffffff")
        extract_and_clear(json_faction, "colours")
        datasheets = {}
        unit_list = []
        if "datasheets" in json_faction:
            for u in json_faction["datasheets"]:
                converted = WHUnit(u)
                datasheets[converted.normalized_name] = converted
                unit_list.append(converted.name)
        self.units = datasheets
        self.unit_names = unit_list
        extract_and_clear(json_faction, "datasheets")
        self.strategems = extract_and_clear(json_faction, "stratagems")
        self.enhancements = extract_and_clear(json_faction, "enhancements")
        self.detachments = extract_and_clear(json_faction, "detachments")
        self.name = extract_and_clear(json_faction,"name")
        self.normalized_name = normalize_name(self.name)
        self.__the_rest = json_faction
        print(json.dumps(self.__the_rest))

    def get_unit(self, normalized_unitname):
        for k, v in self.units.items():
            if normalized_unitname in k or k in normalized_unitname:
                return v, self.get_color()
        return None, self.get_color()

    def get_color(self):
        return random.choice(self.colors)

    @staticmethod
    def extract_color(colorstr):
        if not colorstr:
            colorstr = "#ffffff"
        if "#" in colorstr:
            colorstr = colorstr.replace("#", "")
        return discord.Color(value=int(colorstr, 16))


if __name__ == "__main__":
    with open("../../../data/datasources/10th/json/aeldari.json", "r") as file:
        x = json.load(file)
        WHFaction(x)

