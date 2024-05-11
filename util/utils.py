import json
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


def simple_format(field):
    if type(field) is list:
        if type(field[0]) is str:
            return ", ".join(field)
        return "\n".join(simple_format(x) for x in field)
    elif type(field) is map:
        if len(field.keys()) == 1:
            return simple_format(field[field.keys()[0]])
        return json.dumps(field).strip("\"")
    else:
        return json.dumps(field).strip("\"")


async def send_in_chunks(ctx, t, size=2000, e=False):
    chunk_count = (len(t) // size) + 1
    chunk_size = len(t) // chunk_count
    print(f"chunking message {chunk_size} {chunk_count}")
    for i in range(0, len(t), chunk_size):
        await ctx.response.send_message(t[i: i + chunk_size], ephemeral=e)

