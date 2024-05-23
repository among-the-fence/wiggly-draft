import re

from thefuzz import fuzz

normalize_regex = re.compile('[^a-z ]')


def name_match_function(a, b):
    # print(f"{fuzz.token_sort_ratio(a, b)} {a} {b}")
    return fuzz.token_sort_ratio(a, b)


def normalize_name(name):
    out = normalize_regex.sub('', name.lower()) if name else None
    return out


def closest_match(name, compare_list):
    _original_name = name
    name = normalize_name(name)
    closest_match_name = None
    closest_match_ratio = -1
    for i in compare_list:
        unmodified_match_name = i
        i = normalize_name(i)

        current_r = name_match_function(i, name)
        if current_r > closest_match_ratio:
            closest_match_ratio = current_r
            closest_match_name = unmodified_match_name
    print(f"{_original_name} {closest_match_name} {closest_match_ratio}")
    return closest_match_name


if __name__ == "__main__":
    closest_match("Test", "Test")
    closest_match("Test", ["test"])
    closest_match("Mr Test", ["test"])
    closest_match("Mr Test", ["test"])
    closest_match("Test", ["best"])
    closest_match("Test", ["best"])
    closest_match("crisis suit enforcer commander", ["commander enforcer suit", "battlestuit enforcer"])
    print(normalize_name("Test test"))
