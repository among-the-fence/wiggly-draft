from services.warhammer.models.search_item import SearchItem
from services.warhammer.models.unit import WHUnit
from util.utils import get_or_default


class SearchParams:

    def __init__(self, params):
        self.faction = get_or_default(params, 'faction')
        t = get_or_default(params, 'toughness')
        w = get_or_default(params, 'wounds')
        s = get_or_default(params, 'save')
        self.filters = []
        self.filters.extend([SearchItem("t", x) for x in t.split(",")]) if t else None
        self.filters.extend([SearchItem("sv", x) for x in s.split(",")]) if s else None
        self.filters.extend([SearchItem("w", x) for x in w.split(",")]) if w else None

    def apply(self, unit: WHUnit):
        match = True
        for f in self.filters:
            if f:
                match &= f.apply(unit)
        return match


