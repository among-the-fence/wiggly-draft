import json
import random
from typing import List

import discord
import os
from os.path import exists
import requests as requests
from PIL import Image, ImageDraw, ImageFont
from discord import PartialEmoji, Emoji
from dotenv import load_dotenv

from GameList import GameList
from HeroList import HeroList, Hero
from Pick import Pick

load_dotenv()
bot = discord.Bot(debug_guilds=[os.getenv('DEFAULT_GUILD')])

bunches = {}
latest_users = None

env = {
    "DEV": {
        "timeout": 10,
        "io_emoji": "<:io:1021872443788370072>",
        "pudge": "<:pudge:1021872278360825906>",
        "hacky_one_click": True,
    },
    "PROD": {
        "timeout": 300,
        "io_emoji": "<:io:908114245806329886>",
        "pudge": "<:pudge:908107144254087169>",
        "hacky_one_click": False,
    }
}

hero_list = HeroList(os.getenv('DOTA_TOKEN'))
pudge = None
io_moji = None
activation_owner = None


def get_env_attribute(attribute):
    e = os.getenv('ENV')
    e = e if e else 'PROD'
    return env.get(e)[attribute]


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    emoji_list = list(bot.guilds[0].emojis)
    global io_moji
    io_moji_list = [x for x in emoji_list if x.name == "io"]
    io_moji = io_moji_list[0] if len(io_moji_list) >= 1 else None
    global pudge
    pudge_moji_list = [x for x in emoji_list if x.name == "pudge"]
    pudge = pudge_moji_list[0] if len(pudge_moji_list) >= 1 else None

    print(pudge)
    print(io_moji)


def pick_heroes(user_list):
    chosen = hero_list.choose()
    matchup = []
    for pick in chosen:
        if user_list and len(user_list) > 0:
            user_pick = random.choice(user_list)
            user_list.remove(user_pick)
            matchup.append(Pick(pick, user_pick))
        else:
            matchup.append(Pick(pick, "unassinged"))
    return matchup


def collage(hero_picks: List[Pick]):
    hero_imgs = [x.hero.image for x in hero_picks]
    versus = Image.open("imagecache/versus.png")
    cols = 2
    rows = 3
    single_height = max(x.height for x in hero_imgs)
    single_width = max(x.width for x in hero_imgs)
    divider = 35
    out = Image.new('RGB', (single_width*cols+divider, single_height*rows),color=(47,49,54,0))
    i = 0
    x = 0
    y = 0
    for col in range(cols):
        for row in range(rows):
            print(i, x, y)
            out.paste(hero_picks[i].hero.image_with_name(hero_picks[i].user), (x, y))
            i += 1
            y += single_height
        x += single_width+divider
        y = 0
    w, h = versus.size
    W, H = out.size
    out.paste(versus,(int((W-w)/2),int((H-h)/2)), versus)
    out.save("Collage.jpg")


class MyView(discord.ui.View):
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        self.children = []
        await self.message.edit(content="Don't do a hit!", view=self)

    @discord.ui.button(label="Do", row=0, emoji=get_env_attribute("io_emoji"), style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        messageid = self.message.id
        if messageid not in bunches:
            bunches[messageid] = set(())
        user = interaction.user.display_name
        if os.getenv('ENV') == 'DEV' and get_env_attribute('hacky_one_click'):
            bunches[messageid].add(user + "1")
            bunches[messageid].add(user + "2")
            bunches[messageid].add(user + "3")
            bunches[messageid].add(user + "4")
            bunches[messageid].add(user + '5')

        if user in bunches[messageid]:
            bunches[messageid].remove(user)
        else:
            bunches[messageid].add(user)
        new_message = "Who's in?\n" + ', '.join(bunches[messageid])

        if len(bunches[messageid]) >= 6:
            self.timeout = None
            for child in self.children:
                child.disabled = True
            self.children = {}
            if len(bunches[messageid]) > 6:
                new_message = "Too many presses. \n" + ', '.join(bunches[messageid])
        await self.message.edit(content=new_message, view=self)

        if len(bunches[messageid]) == 6:
            global latest_users
            latest_users = bunches[messageid]
            chosen = pick_heroes(list(bunches[messageid]))
            collage(chosen)
            await interaction.response.send_message(f"{','.join(bunches[messageid])} pressed me!", file=discord.File('Collage.jpg'))
            bunches.clear()
        else:
            await interaction.response.defer()

    @discord.ui.button(label="No", row=0, emoji=get_env_attribute("pudge"), style=discord.ButtonStyle.danger)
    async def second_button_callback(self, button, interaction):
        global activation_owner
        if not interaction.user == activation_owner:
            await interaction.response.send_message(f"{interaction.user.display_name} broke the law!")
        else:
            for child in self.children:
                child.disabled = True
            self.children = []
            messageid = self.message.id
            if messageid in bunches:
                bunches[messageid] = None
            user = interaction.user.display_name
            await self.message.edit(content=f"{user} put a stop to it.", view=self)


@bot.slash_command(name="wiggle", description="Time for street DOTA")
async def wiggle(ctx):
    x = await ctx.respond("Who's in?", view=MyView(timeout=get_env_attribute('timeout')))
    global activation_owner
    activation_owner = ctx.user


@bot.slash_command(name="again", description="Time for street DOTA AGAIN")
async def wiggle(ctx):
    global latest_users
    if not latest_users:
        await ctx.respond("No last match data to use")
    else:
        chosen = pick_heroes(list(latest_users))
        collage(chosen)
        await ctx.response.send_message(f"{','.join(latest_users)} again!",
                                                file=discord.File('Collage.jpg'))


@bot.slash_command(name="random", description="I need a hero")
async def get_one(ctx):
    name = ctx.user.display_name
    random.choice(hero_list.hero_list).image_with_name(name)
    await ctx.response.send_message("",
                                    file=discord.File(name + ".png"))


@bot.slash_command(name="refresh", description="Data gone stale?")
async def refresh(ctx):
    dota_toekn = os.getenv("DOTA_TOKEN")
    if dota_toekn and dota_toekn != "":
        hero_list.refresh(dota_toekn)
        await ctx.respond("Doing a refresh")
    else:
        await ctx.respond("Can't refresh without a token")


@bot.slash_command(name="game", description="Can't pick a game")
async def refresh(ctx):
    await ctx.respond(GameList().get_all())


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))
