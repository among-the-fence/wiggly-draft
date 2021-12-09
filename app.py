import configparser
import json
from os.path import exists
import discord
import os
from dotenv import load_dotenv
import logging
import requests


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
    if not exists("heroData"):
        heros = requests.get(f"https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key={tokens['dota']}&language=en-US").content
        open("heroData", 'w').write(json.dumps(str(heros), indent=2))


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!wiggle'):
        await message.channel.send('Do the wiggle!')

        embedVar=discord.Embed(
            title="Let's Get Ready to Street Dota!",
            color=0xaf0101)
        embedVar.add_field(name="Radiant Heroes", value="{hero1}\n{hero2}\n{hero3}", inline=True)
        embedVar.add_field(name="Dire Heroes", value="{hero4}\n{hero5}\n{hero6}", inline=True)
        embedVar.set_footer(text="Game started by: {}".format(message.author))
        await message.channel.send(embed=embedVar)


get_hero_info()
client.run(bot_token)
