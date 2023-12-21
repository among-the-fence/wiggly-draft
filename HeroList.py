import json
import os
from os.path import exists
import random
from typing import Dict

from PIL import Image, ImageDraw, ImageFont
import requests


class HeroList:
    def __init__(self, dota_token: str = None):
        if exists("heroData.json"):
            with open("heroData.json", 'r') as herodatafile:
                heroesjson = json.loads(herodatafile.read())
                self._raw = heroesjson
                heroes = heroesjson['heroes']
        elif dota_token:
            heroes = self.fetch(dota_token)
        else:
            print("super fail fallback hero list")
            heroes = [{'localized_name': "hero1", 'id': 1, 'name': 'hero1'},
                      {'localized_name': "hero2", 'id': 2, 'name': 'hero2'},
                      {'localized_name': "hero3", 'id': 3, 'name': 'hero3'},
                      {'localized_name': "hero4", 'id': 4, 'name': 'hero4'},
                      {'localized_name': "hero5", 'id': 5, 'name': 'hero5'},
                      {'localized_name': "hero6", 'id': 6, 'name': 'hero6'},
                      ]

        if exists("namemap.json"):
            with open("namemap.json", "r") as namemapfile:
                name_map = json.loads(namemapfile.read())
        else:
            name_map = {"Lifestealer": "Weird Dog"}
        self.hero_list = []
        self.list_to_objects(heroes, name_map)

    def fetch(self, dota_token):
        raw_content = requests.get(
                f"https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key={dota_token}&language=en-US").content
        self._raw = raw_content
        heroesjson = json.loads(raw_content)
        open("heroData.json", 'w').write(json.dumps(heroesjson['result']))
        for h in heroesjson['result']['heroes']:
            print(h)
        return heroesjson['result']['heroes']

    def refresh(self, dota_token):
        if exists("namemap.json"):
            with open("namemap.json", "r") as namemapfile:
                name_map = json.loads(namemapfile.read())
        else:
            name_map = {"Lifestealer": "Weird Dog"}
        self.list_to_objects(self.fetch(dota_token), name_map)

    def list_to_objects(self, heroes, name_map: Dict[str, str]):
        self.hero_list.clear()
        for h in heroes:
            i = Hero(h, name_map)
            i.preload_image()
            self.hero_list.append(i)

    def fix_tean_name(self, name: str):
        if not name == name.lower():
            return name
        else:
            return f"Team {name.capitalize()}"

    def build_silly_teams(self):
        with open("funheroinfo.json", "r") as file:
            team_shit = json.loads(file.read())
            possible_teams = {}
            for h in team_shit:
                fun_info = team_shit[h]
                if 'descriptors' in fun_info:
                    for d in fun_info['descriptors']:
                        if d not in possible_teams:
                            possible_teams[d] = []
                        possible_teams[d].append(h)
            possible_teams = {t: possible_teams[t] for t in possible_teams if len(possible_teams[t]) > 2}
            teams = random.sample(possible_teams.keys(), 2)
            t1 = random.sample(possible_teams[teams[0]], 3)
            t2 = random.sample(possible_teams[teams[1]], 3)

            # Ensure no dupes across teams
            while any(t in t1 for t in t2):
                teams = random.sample(possible_teams.keys(), 2)
                t1 = random.sample(possible_teams[teams[0]], 3)
                t2 = random.sample(possible_teams[teams[1]], 3)
        t1.extend(t2)
        return t1, teams[0], teams[1]

    def choose(self):
        sampled = []
        if random.randint(0, 20) < 5:
            names, team1, team2 = self.build_silly_teams()
            hero_list_map = {h.localized_name: h for h in self.hero_list}
            sampled = [hero_list_map[n] for n in names]
            for h in sampled:
                h.hilarious_display_name = h.get_display_name()
            print(", ".join(n.hilarious_display_name for n in sampled), team1, team2)
            return sampled, team1, team2
        sampled.extend(random.sample(self.hero_list, 6))
        for h in sampled:
            h.hilarious_display_name = h.get_display_name()
        return sampled, None, None

def safe_make_dir(full_directory):
    split_dirs = full_directory.split("/")
    to_make = ""
    for d in split_dirs:
        to_make = to_make + d + "/"
        if not (os.path.exists(to_make) and os.path.isdir(to_make)):
            os.mkdir(to_make)


class Hero:
    def __init__(self, hero_json, name_map):
        safe_make_dir("imagecache/heroes")
        self.name = hero_json['name']
        self.id = hero_json['id']
        self.localized_name = hero_json["localized_name"]
        self.name_list = self.build_name_list(name_map)
        self._raw_json = hero_json
        self.img_name = self.name.replace('npc_dota_hero_', '') + "_lg.png"
        self.image_path = f"imagecache/heroes/{self.img_name}"
        self.hilarious_display_name = None

    def build_name_list(self, name_map):
        if self.localized_name in name_map:
            names = name_map[self.localized_name]
            if isinstance(names, str):
                names = [names, self.localized_name]
            else:
                names.append(self.localized_name)
        else:
            names = [self.localized_name]
        return names

    def get_display_name(self):
        if isinstance(self.name_list, str):
            naem = self.name_list
        elif type(self.name_list) is list:
            naem = random.choice(self.name_list)
        else:
            naem = self.localized_name
        self.hilarious_display_name = naem
        return naem

    @staticmethod
    def rename(name, name_map=None):
        outname = name_map[name] if name_map and name in name_map else name
        return outname

    @staticmethod
    def break_text(text, font, max_width, max_height = 99999999999):
        chunks = []
        split = text.split()
        if len(split) == 1:
            return split
        current_chunk = split[0]
        split = split[1:]
        prev_iteration = ""
        bbox = font.getbbox(current_chunk)
        # use bbox[3] to approximate height and shortcircuit really long strings. They'll never be shown anyway
        while len(split) > 0 and bbox[3]*(len(chunks)-3) < max_height:
            while (bbox[2] * 1.05 + current_chunk.count(' ') * 3) < max_width  and len(split) > 0:
                current_chunk = current_chunk.lstrip() + " " + split[0]
                split = split[1:]
                bbox = font.getbbox(current_chunk)
                prev_iteration = current_chunk
            chunks.append(prev_iteration)
            if prev_iteration != current_chunk:
                split.insert(0, current_chunk.split(" ")[-1])
            prev_iteration = ""
            current_chunk = ""
            bbox = (0,0,0,bbox[3])
        return chunks

    @staticmethod
    def scale_font(box_max_width, text, starting_size, box_max_height=99999999):
        font = ImageFont.truetype("fonts/Trajan Pro Bold.ttf", starting_size)
        bbox = font.getbbox(text)
        original_text = text
        font_size = starting_size
        chunk_text = [text]
        while bbox[2] > box_max_width and font_size > 10:
            font_size = font_size - 1
            font = ImageFont.truetype("fonts/Trajan Pro Bold.ttf", font_size)
            chunk_text = Hero.break_text(original_text, font, box_max_width, box_max_height)
            text = "\n".join(chunk_text)
            bbox = font.getbbox(text)
        return font, chunk_text, bbox[3]

    def preload_image(self):
        if not exists(self.image_path):
            with open(self.image_path, 'wb') as handle:
                response = requests.get("http://cdn.dota2.com/apps/dota2/images/heroes/" + self.img_name, stream=True)
                if not response.ok:
                    print(response)
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
        return self.image_path

    def name_or_default(self):
        print(self.localized_name + " " + self.hilarious_display_name)
        return self.hilarious_display_name if self.hilarious_display_name else self.localized_name

    def image_with_name(self, name):
        portrait = Image.open(self.image_path)
        out = Image.new('RGB', (portrait.width, portrait.height), color=(255, 255, 255, 0))
        out.paste(portrait, (0, 0))
        width, height = out.size
        padding = 5
        textual = ImageDraw.Draw(out)
        font, player_name_chunks, top_name_box_height = Hero.scale_font(width - 10, name, 25)
        textual.text((padding, padding), player_name_chunks[0], fill=(255, 255, 255), font=font, stroke_width=4, stroke_fill=(0, 0, 0))
        font, text, box_height = Hero.scale_font(width - 10, self.name_or_default(), 20, height-top_name_box_height)
        # print(f"{hero_name_text}  {top_name_box_height}")
        print(f"h:{height}  bh:{box_height} t:{text}")
        start_y = height - (box_height * 1.3 * min(len(text), 6))
        for t in text:
            textual.text((padding, start_y), t, fill=(255, 255, 255), font=font, stroke_width=3, stroke_fill=(0, 0, 0))
            start_y = start_y + box_height * 1.3
        if not (os.path.exists("processed") and os.path.isdir("processed")):
            os.mkdir("processed")
        out.save("processed/" + name + ".png")
        return out

if __name__ == "__main__":
    skywrathJson = json.loads('{"name": "npc_dota_hero_skywrath_mage", "id": 101, "localized_name": "Skywrath Mage"}')
    name_map = json.loads(open("namemap.json", "r").read())
    skywrath = Hero(skywrathJson, name_map)
    skywrath.preload_image()
    skywrath.hilarious_display_name = skywrath.name_list[1]

    skywrath.image_with_name(skywrathJson["localized_name"])

    Hero.break_text("From the Ghastly Eyrie I can see to the ends of the world, and from this vantage point I declare with utter certainty that this one is in the bag!",
                    ImageFont.truetype("fonts/Trajan Pro Bold.ttf", 12),
                    187)