from services.warhammer.models.search_item import SearchItem
from services.warhammer.models.unit import WHUnit
from util.utils import get_or_default

keyword_abbreviation_map = {
    "devestating wounds": ["dw", "dev wounds"],
    "deadly demise": ["dd"],
    "lethal hits": ["lh", "lethal"],
    "sustained hits": ["sh", "sustain", "sustained", "sus"],
    "re-roll": ["rr", "reroll", "re roll"],
}


class SearchParams:
    @staticmethod
    def parse_search_parameter(l, key, item):
        if key == "keywords":
            if item:
                for x in item.lower().split(","):
                    added = False
                    for k, v in keyword_abbreviation_map.items():
                        if x in v:
                            l.append(SearchItem("keywords", k))
                            added = True
                            break
                    if not added:
                        l.append(SearchItem("keywords", x))
        else:
            l.extend([SearchItem(key, x) for x in item.split(",")]) if item else None

    def __init__(self, params):
        self.faction = get_or_default(params, 'faction')
        self.filters = []
        SearchParams.parse_search_parameter(self.filters, "t", get_or_default(params, 'toughness'))
        SearchParams.parse_search_parameter(self.filters, "sv", get_or_default(params, 'save'))
        SearchParams.parse_search_parameter(self.filters, "w", get_or_default(params, 'wounds'))
        SearchParams.parse_search_parameter(self.filters, "m", get_or_default(params, 'movement'))
        SearchParams.parse_search_parameter(self.filters, "invuln", get_or_default(params, 'invuln'))
        SearchParams.parse_search_parameter(self.filters, "feelnopain", get_or_default(params, 'feelnopain'))
        SearchParams.parse_search_parameter(self.filters, "attacks", get_or_default(params, 'attacks'))
        SearchParams.parse_search_parameter(self.filters, "weaponskill", get_or_default(params, 'weaponskill'))
        SearchParams.parse_search_parameter(self.filters, "strength", get_or_default(params, 'strength'))
        SearchParams.parse_search_parameter(self.filters, "damage", get_or_default(params, 'damage'))
        SearchParams.parse_search_parameter(self.filters, "ap", get_or_default(params, 'ap'))
        SearchParams.parse_search_parameter(self.filters, "points", get_or_default(params, 'points'))
        SearchParams.parse_search_parameter(self.filters, "keywords", get_or_default(params, 'keywords'))

    def empty(self):
        return len(self.filters) == 0 and self.faction is None

    def apply(self, unit: WHUnit):
        match = True
        for f in self.filters:
            if f:
                match &= f.apply(unit)
        return match

    def filter(self, unit_list: list[WHUnit]):
        for f in self.filters:
            if f and (f.min_filter or f.max_filter):
                unit_list = f.filter(unit_list)
        return unit_list
