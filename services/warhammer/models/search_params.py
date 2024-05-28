from services.warhammer.models.search_item import SearchItem
from services.warhammer.models.unit import WHUnit
from util.utils import get_or_default


class SearchParams:

    @staticmethod
    def parse_search_parameter(l, key, item):
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

    def empty(self):
        return len(self.filters) == 0 and self.faction is None

    def apply(self, unit: WHUnit):
        match = True
        for f in self.filters:
            if f:
                match &= f.apply(unit)
        return match


