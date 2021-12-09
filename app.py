import configparser
import json
from os.path import exists
import discord
import os
from dotenv import load_dotenv
import logging
import requests
import random


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
    img_name = hero_data['name'].replace('npc_dota_hero_', '') + "_sb.png"
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
        for i in range(0,6):
            pick = random.choice(heroes)
            chosen.append(pick)
            get_hero_img(pick)
        embedVar=discord.Embed(
            title="Let's Get Ready to Street Dota!",
            color=0xaf0101)
        # embedVar.set_image(url=img_url)
        embedVar.add_field(name="Radiant Heroes", value=f"{chosen[0]['localized_name']}\n{chosen[1]['localized_name']}\n{chosen[2]['localized_name']}", inline=True)
        embedVar.add_field(name="Dire Heroes", value=f"{chosen[3]['localized_name']}\n{chosen[4]['localized_name']}\n{chosen[5]['localized_name']}", inline=True)
        embedVar.set_footer(text="Game started by: {}".format(message.author))
        msg = await message.channel.send(embed=embedVar)
        await msg.add_reaction("<:morphGive:908107050163249272>")


get_hero_info()
client.run(bot_token)
