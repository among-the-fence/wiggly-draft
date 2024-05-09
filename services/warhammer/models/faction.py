import os
import json

import discord

from services.warhammer.models.unit import WHUnit


class WHFaction:
    def __init__(self, json_faction):
        self.colors = [WHFaction.extract_color(json_faction["colours"][x]) for x in json_faction["colours"]]
        self.units = {u["name"]: WHUnit(u) for u in json_faction["datasheets"]}
        json_faction["datasheets"] = ""
        self.strategems = json_faction["stratagems"]
        json_faction["stratagems"] = ""

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

