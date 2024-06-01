import os

from services.warhammer.models.generated.Catalogue import parse
from services.warhammer.models.unit import WHUnit

dataroot = "data/"
XML_DATA_PREFIX = "wh40k-10e/"

if __name__ == "__main__":
    xml_units = {}
    for f in os.listdir(dataroot + XML_DATA_PREFIX):
        if ".cat" in f:
            data = parse(dataroot + XML_DATA_PREFIX + f, silence=True)
            if data.sharedSelectionEntries:
                for x in data.sharedSelectionEntries.selectionEntry:
                    if x.type_ in ["unit", "model"]:
                        xml_units[x.name] = WHUnit(x, {"factions": ["a"]}, "a")



