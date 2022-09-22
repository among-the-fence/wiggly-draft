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
from HeroList import HeroList, Hero
from Pick import Pick

load_dotenv()
bot = discord.Bot(debug_guilds=[os.getenv('DEFAULT_GUILD')])

bunches = {}

env = {
    "DEV": {
        "timeout": 10,
        "io_emoji": "<:io:1021872443788370072>",
        "pudge": "<:pudge:1021872278360825906>",
    },
    "PROD": {
        "timeout": 300,
        "io_emoji": "<:io:908114245806329886>",
        "pudge": "<:pudge:908107144254087169>",
    }
}

hero_list = HeroList(os.getenv('DOTA_TOKEN'))
pudge = None
io_moji = None


def get_env_attribute(attribute):
    return env.get(os.getenv('ENV'))[attribute]


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
    myFont = ImageFont.truetype("fonts/Trajan Pro Bold.ttf", 15)
    for col in range(cols):
        for row in range(rows):
            print(i, x, y)
            out.paste(hero_imgs[i], (x, y))
            textual = ImageDraw.Draw(out)
            textual.text((x + 5, y + 5), hero_picks[i].user, fill=(255, 255, 255), font=myFont, stroke_width=2, stroke_fill=(0, 0, 0))
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
        if os.getenv('ENV') == 'DEV':
            bunches[messageid].add(user + "1")
            bunches[messageid].add(user + "2")
            bunches[messageid].add(user + "3")
            bunches[messageid].add(user + "4")
            bunches[messageid].add(user + '5')

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
            chosen = pick_heroes(list(bunches[messageid]))
            collage(chosen)
            await interaction.response.send_message(f"{','.join(bunches[messageid])} pressed me!", file=discord.File('Collage.jpg'))
            bunches.clear()

        print("done")

    @discord.ui.button(label="No", row=0, emoji=get_env_attribute("pudge"), style=discord.ButtonStyle.danger)
    async def second_button_callback(self, button, interaction):
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
    print(io_moji)
    print(pudge)
    x = await ctx.respond("Who's in?", view=MyView(timeout=get_env_attribute('timeout')))
    print(x)


@bot.slash_command(name="refresh", description="Data gone stale?")
async def refresh(ctx):
    dota_toekn = os.getenv("DOTA_TOKEN")
    if dota_toekn and dota_toekn != "":
        hero_list.refresh(dota_toekn)
        await ctx.respond("Doing a refresh")
    else:
        await ctx.respond("Can't refresh without a token")


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))
