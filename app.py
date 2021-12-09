import configparser
import json
from os.path import exists
import discord
import os
from dotenv import load_dotenv
import logging
import requests
import random
from PIL import Image


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()

config = configparser.ConfigParser()
config.read("tokens")
tokens = config['DEFAULT']
bot_token = tokens['discord'] if 'discord' in tokens and tokens['discord'] else os.environ.get("BOT_TOKEN")
dota_token = tokens['dota'] if 'dota' in tokens and tokens['dota'] else os.environ.get("DOTA_TOKEN")

client = discord.Client()


def get_hero_info():
    if not exists("heroData.json"):
        heroes = json.loads(requests.get(f"https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key={dota_token}&language=en-US").content)
        open("heroData.json", 'w').write(json.dumps(heroes['result']))


def get_hero_img(hero_data):
    img_name = hero_data['name'].replace('npc_dota_hero_', '') + "_lg.png"
    save_location = f"imagecache/{img_name}"
    if exists(save_location):
        print("Found")
    else:
        with open(save_location, 'wb') as handle:
            response = requests.get("http://cdn.dota2.com/apps/dota2/images/heroes/" + img_name, stream=True)
            if not response.ok:
                print(response)
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
    return save_location


def collage(image_paths):
    hero_imgs = [Image.open(x) for x in image_paths]
    cols = 2
    rows = 3
    single_height = hero_imgs[0].height
    single_width = hero_imgs[0].width
    out = Image.new('RGB', (single_width*cols+5, single_height*rows))
    i = 0
    x = 0
    y = 0
    for col in range(cols):
        for row in range(rows):
            print(i, x, y)
            out.paste(hero_imgs[i], (x, y))
            i += 1
            y += single_height
        x += single_width+5
        y = 0
    out.save("Collage.jpg")


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!wiggle'):
        if exists("heroData.json"):
            heroesjson = json.loads(open("heroData.json", 'r').read())
            heroes = heroesjson['heroes']
        else:
            heroes = [{'localized_name': "hero1"},
                      {'localized_name': "hero2"},
                      {'localized_name': "hero3"},
                      {'localized_name': "hero4"},
                      {'localized_name': "hero5"},
                      {'localized_name': "hero6"},
                      ]
        chosen = []
        images = []
        for i in range(0,6):
            pick = random.choice(heroes)
            chosen.append(pick)
            images.append(get_hero_img(pick))
        collage(images)
        embedVar=discord.Embed(
            title="Let's Get Ready to Street Dota!",
            color=0xaf0101)
        file = discord.File("Collage.jpg", filename="image.jpg")
        embedVar.set_image(url="attachment://image.jpg")
        embedVar.add_field(name="Radiant Heroes", value=f"{chosen[0]['localized_name']}\n{chosen[1]['localized_name']}\n{chosen[2]['localized_name']}", inline=True)
        embedVar.add_field(name="Dire Heroes", value=f"{chosen[3]['localized_name']}\n{chosen[4]['localized_name']}\n{chosen[5]['localized_name']}", inline=True)
        embedVar.set_footer(text="Game started by: {}".format(message.author))
        msg = await message.channel.send(file=file, embed=embedVar)
        await msg.add_reaction("<:morphGive:908107050163249272>")


get_hero_info()
client.run(bot_token)
