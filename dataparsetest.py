import os

from services.warhammer.models.generated.Catalogue import parse

data_root = "data/wh40k-10e/"

if __name__ == "__main__":
    libs = {}
    for f in os.listdir(data_root):
        if ".cat" in f:
            # print(f)
            data = parse(data_root + f, silence=True)
            libs[f] = data
    for k, data in libs.items():
        print(k)
        if data.sharedSelectionEntries:
            for x in data.sharedSelectionEntries.selectionEntry:
                if x.type_ in ["unit", "model"]:
                    if x.costs:
                        print(f" - {x.name} {','.join([str(c.value) for c in x.costs.cost if x.costs])}")
                    else:
                        print(f" - {x.name} {x}")

