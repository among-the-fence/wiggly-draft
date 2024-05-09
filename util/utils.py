import re

normalize_regex = re.compile('[^a-z]')


def normalize_name(name):
    return normalize_regex.sub('', name.lower()) if name else None


def extract_and_clear(jsondata, key, default=None):
    jsonfield = default
    if key in jsondata:
        jsonfield = jsondata[key]
        del jsondata[key]
    return jsonfield
