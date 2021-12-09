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

client = discord.Client()


def get_hero_info():
    if not exists("heroData.json") and 'dota' in tokens and tokens['dota']:
        heroes = json.loads(requests.get(f"https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key={tokens['dota']}&language=en-US").content)
        open("heroData.json", 'w').write(json.dumps(heroes['result']))


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!wiggle'):
        await message.channel.send('Do the wiggle!')

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
        for i in range(0,):
            pick = random.choice(heroes)
            chosen.append(pick['localized_name'])
            heroes.remove(pick)
        embedVar=discord.Embed(
            title="Let's Get Ready to Street Dota!",
            color=0xaf0101)
        embedVar.add_field(name="Radiant Heroes", value=f"{chosen[0]}\n{chosen[1]}\n{chosen[2]}", inline=True)
        embedVar.add_field(name="Dire Heroes", value=f"{chosen[3]}\n{chosen[4]}\n{chosen[5]}", inline=True)
        embedVar.set_footer(text="Game started by: {}".format(message.author))
        await message.channel.send(embed=embedVar)


get_hero_info()
client.run(bot_token)
