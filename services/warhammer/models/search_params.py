from services.warhammer.models.search_item import SearchItem
from services.warhammer.models.unit import WHUnit
from util.utils import get_or_default


class SearchParams:

    def __init__(self, params):
        self.faction = get_or_default(params, 'faction')
        t = get_or_default(params, 'toughness')
        w = get_or_default(params, 'wounds')
        s = get_or_default(params, 'save')
        self.filters = [
           SearchItem("t", t) if t else None,
           SearchItem("sv", s) if s else None,
           SearchItem("w", w) if w else None,
        ]

    def apply(self, unit: WHUnit):
        match = True
        for f in self.filters:
            if f:
                match &= f.apply(unit)
        return match


