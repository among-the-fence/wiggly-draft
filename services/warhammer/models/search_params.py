from services.warhammer.models.search_item import SearchItem
from services.warhammer.models.unit import WHUnit
from util.utils import get_or_default
import string

keyword_abbreviation_map = {
    "devestating wounds": ["dw", "dev wounds"],
    "deadly demise": ["dd"],
    "lethal hits": ["lh", "lethal"],
    "sustained hits": ["sh", "sustain", "sustained", "sus"],
    "re-roll": ["rr", "reroll", "re roll"],
}


class SearchParams:

    def parse_search_parameter(self, key, item):
        if key == "keywords":
            if item:
                for x in item.lower().split(","):
                    x = x.strip()
                    added = False
                    for k, v in keyword_abbreviation_map.items():
                        if x in v:
                            self.filters.append(SearchItem("keywords", k))
                            self.loose_filters.extend([SearchItem("keywordextended", x) for x in k.split(" ")])
                            added = True
                            break
                    if not added:
                        self.filters.append(SearchItem("keywords", x))
                        self.loose_filters.extend([SearchItem("keywordextended", x) for x in x.translate(str.maketrans('', '', string.punctuation)).split(" ")])
        else:
            self.filters.extend([SearchItem(key, x.replace(" ", "").strip()) for x in item.split(",")]) if item else None

    def __init__(self, params):
        self.faction = get_or_default(params, 'faction')
        self.filters = []
        self.loose_filters = []
        self.parse_search_parameter("t", get_or_default(params, 'toughness'))
        self.parse_search_parameter("sv", get_or_default(params, 'save'))
        self.parse_search_parameter("w", get_or_default(params, 'wounds'))
        self.parse_search_parameter("m", get_or_default(params, 'movement'))
        self.parse_search_parameter("invuln", get_or_default(params, 'invuln'))
        self.parse_search_parameter("feelnopain", get_or_default(params, 'feelnopain'))
        self.parse_search_parameter("attacks", get_or_default(params, 'attacks'))
        self.parse_search_parameter("weaponskill", get_or_default(params, 'weaponskill'))
        self.parse_search_parameter("strength", get_or_default(params, 'strength'))
        self.parse_search_parameter("damage", get_or_default(params, 'damage'))
        self.parse_search_parameter("ap", get_or_default(params, 'ap'))
        self.parse_search_parameter("points", get_or_default(params, 'points'))
        self.parse_search_parameter("keywords", get_or_default(params, 'keywords'))
        self.parse_search_parameter("oc", get_or_default(params, 'oc'))

    def __str__(self):
        out = f"f:{self.faction}" if self.faction else None
        return ", ".join([str(x) for x in [out] + self.filters + self.loose_filters if x])

    def empty(self):
        return len(self.filters) == 0 and self.faction is None and len(self.loose_filters) == 0

    def apply(self, unit: WHUnit):
        match = True
        for f in self.filters:
            if f and match:
                match &= f.apply(unit)
        return match

    def apply_loose(self, unit: WHUnit):
        match = True
        for f in self.filters:
            if f and match and f.prop_name != "keywords":
                match &= f.apply(unit)
        for f in self.loose_filters:
            if f and match:
                match &= f.apply(unit)
        return match

    def filter(self, unit_list: list[WHUnit]):
        if unit_list:
            for f in self.filters:
                if f and (f.min_filter or f.max_filter):
                    unit_list = f.filter(unit_list)
        return unit_list
