from services.warhammer.models.search_item import SearchItem
from services.warhammer.models.unit import WHUnit
from util.utils import get_or_default


class SearchParams:

    def __init__(self, params):
        self.faction = get_or_default(params, 'faction')
        t = get_or_default(params, 'toughness')
        w = get_or_default(params, 'wounds')
        s = get_or_default(params, 'save')
        m = get_or_default(params, 'movement')
        inv = get_or_default(params, 'invuln')
        fnp = get_or_default(params, 'feelnopain')
        self.filters = []
        self.filters.extend([SearchItem("t", x) for x in t.split(",")]) if t else None
        self.filters.extend([SearchItem("sv", x) for x in s.split(",")]) if s else None
        self.filters.extend([SearchItem("w", x) for x in w.split(",")]) if w else None
        self.filters.extend([SearchItem("m", x) for x in m.split(",")]) if m else None
        self.filters.extend([SearchItem("invuln", x) for x in inv.split(",")]) if inv else None
        self.filters.extend([SearchItem("feelnopain", x) for x in fnp.split(",")]) if fnp else None

    def empty(self):
        return len(self.filters) == 0 and self.faction == None

    def apply(self, unit: WHUnit):
        match = True
        for f in self.filters:
            if f:
                match &= f.apply(unit)
        return match


