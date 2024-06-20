import re

from services.warhammer.models.unit import WHUnit

search_type_re = re.compile("(\\<|\\>|=|!)+")
number_re = re.compile("(\\d+)")


class SearchItem:
    def __init__(self, prop_name: str, item_str: str):
        self.__raw = f"{prop_name}:{item_str}"
        self.prop_name = prop_name
        self.min_filter = None
        self.max_filter = None
        self.search_type = None
        self.search_value = None
        self.search_function = None
        # print(self.__raw)
        if len(item_str) > 0:
            if "min" in item_str:
                self.min_filter = prop_name
            elif "max" in item_str:
                self.max_filter = prop_name
            elif "keywords" == prop_name:
                if "!=" in item_str:
                    item_str = item_str.replace("!=", "")
                    self.search_function = lambda unit: item_str not in unit.get_prop("keywords")
                else:
                    item_str = item_str.replace("=", "")
                    self.search_function = lambda unit: item_str in unit.get_prop("keywords")
            else:
                operator_search = search_type_re.search(item_str)

                if "d" in item_str:
                    self.search_value = item_str
                else:
                    search_result = number_re.search(item_str)
                    if search_result:
                        self.search_value = int(search_result.group())
                self.search_type = None
                if operator_search:
                    match operator_search.group():
                        case ">":
                            self.search_type = lambda x: x > self.search_value
                        case ">=":
                            self.search_type = lambda x: x >= self.search_value
                        case "<":
                            self.search_type = lambda x: x < self.search_value
                        case "<=":
                            self.search_type = lambda x: x <= self.search_value
                        case "!=":
                            self.search_type = lambda x: x != self.search_value
                        case _:
                            self.search_type = lambda x: x == self.search_value
                else:
                    self.search_type = lambda x: x == self.search_value

    def __str__(self):
        return self.__raw

    def apply(self, unit: WHUnit):
        match = True
        if self.search_function:
            match &= self.search_function(unit)
        if self.search_type:
            match &= any([type(self.search_value) is type(x) and self.search_type(x) for x in unit.get_prop(self.prop_name) or [False]])
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
            print(prop_name)
            flatten_values = SearchItem.flatten([x.get_prop(prop_name) for x in units])
            flatten_values = filter(lambda x: type(x) is int, flatten_values)

            extreme_value = max(flatten_values)
        if self.min_filter:
            prop_name = self.min_filter
            flatten_values = SearchItem.flatten([x.get_prop(prop_name) for x in units])
            extreme_value = min(flatten_values)
        out = []
        if prop_name:
            if type(extreme_value) is list:
                extreme_value = extreme_value[0]
            print(extreme_value)
            for u in units:
                got_prop = u.get_prop(prop_name)
                if got_prop and extreme_value in got_prop:
                    out.append(u)
        return out
