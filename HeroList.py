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
            heroesjson = json.loads(open("heroData.json", 'r').read())
            self._raw = heroesjson
            heroes = heroesjson['heroes']
        elif dota_token:
            heroes = self.fetch(dota_token)
        else:
            heroes = [{'localized_name': "hero1", 'id': 1, 'name': 'hero1'},
                      {'localized_name': "hero2", 'id': 2, 'name': 'hero2'},
                      {'localized_name': "hero3", 'id': 3, 'name': 'hero3'},
                      {'localized_name': "hero4", 'id': 4, 'name': 'hero4'},
                      {'localized_name': "hero5", 'id': 5, 'name': 'hero5'},
                      {'localized_name': "hero6", 'id': 6, 'name': 'hero6'},
                      ]

        if exists("namemap.json"):
            name_map = json.loads(open("namemap.json", "r").read())
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
            name_map = json.loads(open("namemap.json", "r").read())
        else:
            name_map = {"Lifestealer": "Weird Dog"}
        self.list_to_objects(self.fetch(dota_token), name_map)

    def list_to_objects(self, heroes, name_map: Dict[str, str]):
        self.hero_list.clear()
        for h in heroes:
            i = Hero(h, name_map)
            i.preload_image()
            self.hero_list.append(i)

    def choose(self):
        return random.sample(self.hero_list, 6)


class Hero:
    def __init__(self, hero_json, name_map):
        self.name = hero_json['name']
        self.id = hero_json['id']
        self.localized_name = hero_json["localized_name"]
        if self.localized_name in name_map:
            self.name_list = name_map[self.localized_name]
        else:
            self.name_list = self.localized_name
        self._raw_json = hero_json
        self.img_name = self.name.replace('npc_dota_hero_', '') + "_lg.png"
        self.image_path = f"imagecache/heroes/{self.img_name}"
        self.image = None

    def get_display_name(self):
        if isinstance(self.name_list, str):
            return self.name_list
        elif type(self.name_list) is list:
            return random.choice(self.name_list)
        else:
            return self.localized_name
    @staticmethod
    def rename(name, name_map=None):
        outname = name_map[name] if name_map and name in name_map else name
        return outname

    @staticmethod
    def scale_font(size, text, starting_size):
        font = ImageFont.truetype("fonts/Trajan Pro Bold.ttf", starting_size)
        while font.getsize(text)[0] > size > 10:
            starting_size = starting_size - 1
            font = ImageFont.truetype("fonts/Trajan Pro Bold.ttf", starting_size)
        return font

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
        portrait = Image.open(self.image_path)
        self.image = portrait
        return self.image_path

    def image_with_name(self, name):
        out = Image.new('RGB', (self.image.width, self.image.height), color=(255, 255, 255, 0))
        out.paste(self.image, (0, 0))
        width, height = out.size
        padding = 6
        textual = ImageDraw.Draw(out)
        hilarious_hero_display_name = self.get_display_name()
        font = Hero.scale_font(width - 10, hilarious_hero_display_name, 20)
        textual.text((padding, height - 20), hilarious_hero_display_name, fill=(255, 255, 255), font=font, stroke_width=3, stroke_fill=(0, 0, 0))
        font = Hero.scale_font(width - 10, name, 25)
        textual.text((5, 5), name, fill=(255, 255, 255), font=font, stroke_width=4, stroke_fill=(0, 0, 0))
        if not (os.path.exists("processed") and os.path.isdir("processed")):
            os.mkdir("processed")
        out.save("processed/" + name + ".png")
        return out
