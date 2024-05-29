import re

from services.warhammer.models.unit import WHUnit

search_type_re = re.compile("(\\<|\\>|=|!)+")
number_re = re.compile("(\d+)")


class SearchItem:
    def __init__(self, prop_name: str, item_str: str):
        self.__raw = f"{prop_name}{item_str}"
        self.prop_name = prop_name
        self.min_filter = None
        self.max_filter = None
        self.search_type = None
        self.search_value = None
        if len(item_str) > 0:
            if "min" in item_str:
                self.min_filter = prop_name
            elif "max" in item_str:
                self.max_filter = prop_name
            else:
                operator_search = search_type_re.search(item_str)

                va = int(number_re.search(item_str).group())
                self.search_type = None
                if operator_search:
                    match operator_search.group():
                        case ">":
                            self.search_type = lambda unit: any([type(x) is int and x > va for x in unit.get_prop(prop_name) or [False]])
                        case ">=":
                            self.search_type = lambda unit: any([type(x) is int and x >= va for x in unit.get_prop(prop_name) or [False]])
                        case "<":
                            self.search_type = lambda unit: any([type(x) is int and x < va for x in unit.get_prop(prop_name) or [False]])
                        case "<=":
                            self.search_type = lambda unit: any([type(x) is int and x <= va for x in unit.get_prop(prop_name) or [False]])
                        case "!=":
                            self.search_type = lambda unit: any([type(x) is int and va != x for x in unit.get_prop(prop_name) or [False]])
                        case _:
                            self.search_type = lambda unit: any([type(x) is int and va == x for x in unit.get_prop(prop_name) or [False]])
                else:
                    self.search_type = lambda unit: any([type(x) is int and va == x for x in unit.get_prop(prop_name) or [False]])

    def __str__(self):
        return self.__raw

    def apply(self, unit: WHUnit):
        match = True
        if self.search_type:
            # print(f"{unit.stats} {unit.get_prop(self.prop_name)} {self.search_type(unit)}")
            match &= self.search_type(unit)
        return match

    @staticmethod
    def flatten(lst):
        # print(lst)
        out = []
        for i in lst:
            if i:
                out.extend(i)
        # print(out)
        return out

    def filter(self, units: list[WHUnit]):
        prop_name = None
        extreme_value = -1
        if self.max_filter:
            prop_name = self.max_filter
            flatten_values = SearchItem.flatten([x.get_prop(self.max_filter) for x in units])
            extreme_value = max(flatten_values)
        if self.min_filter:
            prop_name = self.min_filter
            flatten_values = SearchItem.flatten([x.get_prop(self.min_filter) for x in units])
            extreme_value = min(flatten_values)
        out = []
        if prop_name:
            if type(extreme_value) is list:
                extreme_value = extreme_value[0]
            print(extreme_value)
            for u in units:
                if extreme_value in u.get_prop(prop_name):
                    out.append(u)
        return out
