import os
import random
from typing import List, Optional

import discord
from PIL import Image
from discord import option
from dotenv import load_dotenv

from GameList import GameList
from HeroList import HeroList
from Pick import Pick
from WigglePoll import WigglePoll

load_dotenv()
bot = discord.Bot(debug_guilds=[os.getenv('DEFAULT_GUILD')])


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
wiggle_poll = WigglePoll()


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
        global wiggle_poll
        wiggle_poll.end()
        await self.message.edit(content="Don't do a hit!", view=self)

    @discord.ui.button(label="Do", row=0, emoji=get_env_attribute("io_emoji"), style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        global wiggle_poll
        user = interaction.user.display_name

        if os.getenv('ENV') == 'DEV' and get_env_attribute('hacky_one_click'):
            wiggle_poll.user_reacted(user_name=f"{user}2")
            wiggle_poll.user_reacted(user_name=f"{user} squawk squawk")
            wiggle_poll.user_reacted(user_name=f"{user} hooooooooooooooooooooooo")
            wiggle_poll.user_reacted(user_name=f"{user} I'm a little fat boy")
            wiggle_poll.user_reacted(user_name=f"{user}5")

        await self.message.edit(embed=wiggle_poll.build_embed(), view=self)

        if wiggle_poll.invalid():
            self.timeout = None
            for child in self.children:
                child.disabled = True
            self.children = {}
            new_message = f"Too many presses. \n{wiggle_poll.display_user_str()}"
            await self.message.edit(content=new_message, view=self)

        if wiggle_poll.ready():
            self.timeout = None
            for child in self.children:
                child.disabled = True
            self.children = {}
            chosen = pick_heroes(list(wiggle_poll.users))
            collage(chosen)
            embedVar = wiggle_poll.build_embed()
            embedVar.set_image(url="attachment://image.jpg")
            await self.message.edit(embed=embedVar, view=self, file=discord.File("Collage.jpg", filename="image.jpg"))
            wiggle_poll.end()
        else:
            await interaction.response.defer()

    @discord.ui.button(label="No", row=0, emoji=get_env_attribute("pudge"), style=discord.ButtonStyle.danger)
    async def second_button_callback(self, button, interaction):
        global wiggle_poll
        if not wiggle_poll.owner == activation_owner:
            await interaction.response.send_message(f"{interaction.user.display_name} broke the law!")
        else:
            for child in self.children:
                child.disabled = True
            self.children = []
            user = interaction.user.display_name
            await self.message.edit(content=f"{user} put a stop to it.", view=self)


@bot.slash_command(name="wiggle", description="Time for street DOTA")
async def wiggle(ctx):
    global wiggle_poll
    if not wiggle_poll.active:
        wiggle_poll.start(ctx.user)
        await ctx.respond(embed=wiggle_poll.build_embed(), view=MyView(timeout=get_env_attribute('timeout')))
        global activation_owner
        activation_owner = ctx.user
    else:
        await ctx.respond("Too slow", ephemeral=True)


@bot.slash_command(name="again", description="Time for street DOTA AGAIN")
async def again(ctx):
    global wiggle_poll
    if not wiggle_poll.previous_success:
        await ctx.respond("No last match data to use")
    else:
        wiggle_poll.rerun()

        chosen = pick_heroes(list(wiggle_poll.previous_success))
        collage(chosen)
        embedVar = wiggle_poll.build_embed()
        embedVar.set_image(url="attachment://image.jpg")
        await ctx.response.send_message(embed=embedVar, file=discord.File("Collage.jpg", filename="image.jpg"))
        wiggle_poll.end()

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
@option("player_count", description="How many people?", required=False)
async def random_game(ctx, player_count: int):
    if not player_count:
        await ctx.respond(GameList().get_all())
    elif player_count == 1:
        await ctx.respond("Whatever you want")
    elif 1 < player_count <= 10:
        await ctx.respond(f"{player_count}: {GameList().get_rand(player_count)}")
    else:
        await ctx.respond("very funny.\n" + GameList().get_all())


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))
