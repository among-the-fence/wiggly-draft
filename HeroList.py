import json
from os.path import exists
import random

from PIL import Image, ImageDraw, ImageFont
import requests


class HeroList:
    def __init__(self, dota_token: str = None):
        if exists("heroData.json"):
            heroesjson = json.loads(open("heroData.json", 'r').read())
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
        self.hero_list = []
        self.list_to_objects(heroes)

    @staticmethod
    def fetch(dota_token):
        raw_content = requests.get(
                f"https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key={dota_token}&language=en-US").content
        print(raw_content)
        heroesjson = json.loads(raw_content)
        open("heroData.json", 'w').write(json.dumps(heroesjson['result']))
        for h in heroesjson['result']['heroes']:
            print(h)
        return heroesjson['heroes']

    def refresh(self, dota_token):
        self.list_to_objects(self.fetch(dota_token))

    def list_to_objects(self, heroes):
        for h in heroes:
            i = Hero(h)
            i.preload_image()
            self.hero_list.append(i)

    def choose(self):
        return random.sample(self.hero_list, 6)


class Hero:
    def __init__(self, hero_json):
        self.name = hero_json['name']
        self.id = hero_json['id']
        self.localized_name = Hero.rename(hero_json["localized_name"])
        self._raw_json = hero_json
        self.image = None

    @staticmethod
    def rename(name):
        return "Weird Dog" if name == 'Lifestealer' else name

    def preload_image(self):
        img_name = self.name.replace('npc_dota_hero_', '') + "_lg.png"
        save_location = f"imagecache/heroes/{img_name}"
        if not exists(save_location):
            with open(save_location, 'wb') as handle:
                response = requests.get("http://cdn.dota2.com/apps/dota2/images/heroes/" + img_name, stream=True)
                if not response.ok:
                    print(response)
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
            portrait = Image.open(save_location)
            W, H = portrait.size
            padding = 6
            draw = ImageDraw.Draw(portrait)
            myFont = ImageFont.truetype("fonts/Trajan Pro Bold.ttf", 15)
            draw.text((padding, H - 20), self.localized_name, fill=(255, 255, 255), font=myFont, stroke_width=2, stroke_fill=(0, 0, 0))
            portrait.save(save_location)
        self.image = Image.open(save_location)
        return save_location

