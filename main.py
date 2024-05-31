import base64
import io
import json
import math
import os
import random
import shutil
from typing import List

import discord
import openai
from PIL import Image
from discord import option, Color
from dotenv import load_dotenv

from GameList import GameList
from HeroList import HeroList
from Pick import Pick
from WigglePoll import WigglePoll
from services.warhammer import Warhammer
from services.warhammer.models.faction import WHFaction
from services.warhammer.models.search_params import SearchParams
from services.warhammer.models.unit import WHUnit
from services.warhammer.views.TestView import TestView
from services.warhammer.views.UnitView import UnitView
from util.utils import send_in_chunks

load_dotenv()
bot = discord.Bot(debug_guilds=[os.getenv('DEFAULT_GUILD')])
if os.getenv("OPENAI_API_KEY"):
    openai.api_key = os.getenv("OPENAI_API_KEY")

env = {
    "DEV": {
        "timeout": 10,
        "io_emoji": "<:io:1021872443788370072>",
        "pudge": "<:pudge:1021872278360825906>",
        "hacky_one_click": True,
    },
    "PROD": {
        "timeout": 300,
        "hacky_one_click": False,
    }
}

hero_list = HeroList(os.getenv('DOTA_TOKEN'))
pudge = None
io_moji = None
activation_owner = None
wiggle_poll = WigglePoll()
wh_data = Warhammer.get_wh_data()

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

    for s in bot.guilds:
        for x in s.channels:
            if x.name == "bot":
                with open("message.txt", mode="r") as messagefile:
                    await bot.get_channel(x.id).send(messagefile.readline())

def bill_and_ben_are_on_the_same_team(matchup: List[Pick]):
    team1_names = set([x.user.display_name.lower() for x in matchup[:3]])
    team2_names = set([x.user.display_name.lower() for x in matchup[3:]])
    return {"chu", "mrc48b"}.issubset(team1_names) or {"chu", "mrc48b"}.issubset(team2_names)

def pick_heroes(user_list):
    matchup, team1, team2 = build_picks(user_list)
    while bill_and_ben_are_on_the_same_team(matchup):
        matchup, team1, team2 = build_picks(user_list)
    return matchup, team1, team2

def build_picks(user_list):
    chosen, team1, team2 = hero_list.choose()
    matchup = []
    for pick in chosen:
        if user_list and len(user_list) > 0:
            user_pick = random.choice(user_list)
            user_list.remove(user_pick)
            matchup.append(Pick(pick, user_pick))
        else:
            matchup.append(Pick(pick, "Unassigned"))
    return matchup, team1, team2

def extra_fun_names(hero_picks: List[Pick]):
    swipswappin = 0
    for h in hero_picks:
        if h.hero.localized_name == 'Bloodseeker':
            enemy_idx = random.randint(0,2) # It's inclusive
            if swipswappin < 3:
                enemy_idx += 3
            hero_picks[enemy_idx].hero.hilarious_display_name = 'Bloodhaver'

        if h.hero.localized_name == 'Silencer':
            if random.randint(0, 9) < 5:
                for j in hero_picks:
                    j.user_display_name = 'Silencer'
                    j.hero.hilarious_display_name = 'Silencer'
        swipswappin += 1

    return hero_picks

def collage(hero_picks: List[Pick]):
    hero_imgs = [Image.open(x.hero.image_path) for x in hero_picks]
    versus = Image.open("imagecache/versus.png")
    cols = 2
    rows = 3
    single_height = max(x.height for x in hero_imgs)
    single_width = max(x.width for x in hero_imgs)
    divider = 35
    out = Image.new('RGB', (single_width * cols + divider, single_height * rows), color=(47, 49, 54, 0))
    i = 0
    x = 0
    y = 0

    hero_picks = extra_fun_names(hero_picks)

    for col in range(cols):
        for row in range(rows):
            out.paste(hero_picks[i].hero.image_with_name(hero_picks[i].user_display_name), (x, y))
            i += 1
            y += single_height
        x += single_width + divider
        y = 0
    w, h = versus.size
    W, H = out.size
    out.paste(versus, (int((W - w) / 2), int((H - h) / 2)), versus)
    out.save("processed/Collage.jpg")


class MyView(discord.ui.View):
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        self.children = []
        global wiggle_poll
        display_embed = discord.Embed(title=f"Don't do a hit!",
                                      color=0x900000)
        wiggle_poll.end()
        await self.message.edit(embed=display_embed, view=self)

    async def update_embed(self):
        global wiggle_poll
        if wiggle_poll.ready():
            self.timeout = None
            for child in self.children:
                child.disabled = True
            self.children = {}
            chosen, team1, team2 = pick_heroes(list(wiggle_poll.users))
            collage(chosen)
            display_embed = wiggle_poll.build_embed()
            display_embed.add_field(name=team1 if team1 else "Radiant Team",
                                    value=f"{chosen[0].user.mention} ({chosen[0].hero.localized_name})\n"
                                          f"{chosen[1].user.mention} ({chosen[1].hero.localized_name})\n"
                                          f"{chosen[2].user.mention} ({chosen[2].hero.localized_name})",
                                    inline=True)
            display_embed.add_field(name=team2 if team2 else "Dire Team",
                                    value=f"{chosen[3].user.mention} ({chosen[3].hero.localized_name})\n"
                                          f"{chosen[4].user.mention} ({chosen[4].hero.localized_name})\n"
                                          f"{chosen[5].user.mention} ({chosen[5].hero.localized_name})",
                                    inline=True)
            display_embed.set_image(url="attachment://image.jpg")
            await self.message.edit(embed=display_embed, view=self,
                                    file=discord.File("processed/Collage.jpg", filename="image.jpg"))
            wiggle_poll.end()
            shutil.rmtree("processed/")
        else:
            await self.message.edit(embed=wiggle_poll.build_embed(), view=self)

    @discord.ui.button(label="", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        global wiggle_poll
        wiggle_poll.user_reacted(interaction.user)

        if wiggle_poll.invalid():
            self.timeout = None
            for child in self.children:
                child.disabled = True
            self.children = {}
            new_message = f"Too many presses. \n{wiggle_poll.display_user_str()}"
            await self.message.edit(content=new_message, view=self)

        elif wiggle_poll.ready():
            await self.update_embed()

        else:
            await self.message.edit(embed=wiggle_poll.build_embed(), view=self)
            await interaction.response.defer()

    @discord.ui.button(label="", row=0, style=discord.ButtonStyle.danger)
    async def second_button_callback(self, button, interaction):
        global wiggle_poll
        if not wiggle_poll.owner == activation_owner:
            await interaction.response.send_message(f"{interaction.user.display_name} broke the law!")
        else:
            for child in self.children:
                child.disabled = True
            self.children = []
            user = interaction.user.display_name
            display_embed = discord.Embed(title=f"{user} put a stop to it.",
                                          color=0xC00000)
            wiggle_poll.end()
            await self.message.edit(embed=display_embed, view=self)

    @staticmethod
    def get_test_name(usermember):
        user = usermember.display_name
        test_names = [f"{user}", f"{user} 2", f"{user} squawk squawk", f"{user} hooooooooooooooooooooooo", f"{user[:2]}",
                      f"{user} I'm a little fat boy", f"{user}5", f"{user} get it",
                      f"{user} {user[::-1]}", f"{user} B{user[1:]}", f"{user} sfddfsd", ]
        usermember.display_name = random.choice(test_names)
        return usermember

    @discord.ui.button(label="TEST One user", row=0, style=discord.ButtonStyle.secondary)
    async def secret_last_button_callback(self, button, interaction):
        global wiggle_poll
        user = interaction.user

        if os.getenv('ENV') == 'DEV' and get_env_attribute('hacky_one_click'):
            wiggle_poll.user_reacted(user, True)
            await self.update_embed()

        await interaction.response.defer()

    @discord.ui.button(label="TEST manyuser", row=0, style=discord.ButtonStyle.secondary)
    async def secret_more_button_callback(self, button, interaction):
        global wiggle_poll
        user = interaction.user

        if os.getenv('ENV') == 'DEV' and get_env_attribute('hacky_one_click'):
            while not wiggle_poll.ready():
                wiggle_poll.user_reacted(user, True)
            await self.update_embed()

        await interaction.response.defer()


@bot.slash_command(name="wiggle", description="Let's get ready to WIGGLE!")
async def wiggle(ctx):
    global wiggle_poll
    if not wiggle_poll.active:
        wiggle_poll.start(ctx.user)
        view = MyView(timeout=get_env_attribute('timeout'))
        view.children[0].emoji = io_moji
        view.children[1].emoji = pudge
        if not (os.getenv('ENV') == 'DEV' and get_env_attribute('hacky_one_click')):
            view.children = [x for x in view.children if "TEST" not in x.label]

        await ctx.respond(embed=wiggle_poll.build_embed(), view=view)
        global activation_owner
        activation_owner = ctx.user
    else:
        await ctx.respond("Too slow", ephemeral=True)


@bot.slash_command(name="again", description="Another round!")
async def again(ctx):
    global wiggle_poll
    if not wiggle_poll.previous_success:
        await ctx.respond("Can't do a hit if there was no prior hit!")
    else:
        wiggle_poll.rerun()

        chosen, team1, team2 = pick_heroes(list(wiggle_poll.previous_success))
        collage(chosen)
        display_embed = wiggle_poll.build_embed()
        display_embed.add_field(name=team1 if team1 else "Radiant Team",
                                value=f"{chosen[0].user.mention} ({chosen[0].hero.localized_name})\n"
                                      f"{chosen[1].user.mention} ({chosen[1].hero.localized_name})\n"
                                      f"{chosen[2].user.mention} ({chosen[2].hero.localized_name})",
                                inline=True)
        display_embed.add_field(name=team2 if team2 else "Dire Team",
                                value=f"{chosen[3].user.mention} ({chosen[3].hero.localized_name})\n"
                                      f"{chosen[4].user.mention} ({chosen[4].hero.localized_name})\n"
                                      f"{chosen[5].user.mention} ({chosen[5].hero.localized_name})",
                                inline=True)
        display_embed.set_image(url="attachment://image.jpg")
        await ctx.response.send_message(embed=display_embed, file=discord.File("processed/Collage.jpg", filename="image.jpg"))
        wiggle_poll.end()
        shutil.rmtree("processed/")


@bot.slash_command(name="debug", description="Info")
@option("hero", description="Hero Name", required=False)
async def slash_debug(ctx, hero: str):
    await ctx.defer()
    hero_map = {x.localized_name.lower(): x for x in hero_list.hero_list}
    hero = hero.lower() if hero else None
    if hero and hero in hero_map:
        h = hero_map[hero]
        cols = math.ceil(math.sqrt(len(h.name_list) * .7))
        rows = math.ceil(len(h.name_list) / cols)
        single_height = h.image.height
        single_width = h.image.width
        out = Image.new('RGB', (single_width * cols, single_height * rows), color=(47, 49, 54, 0))
        x = 0
        y = 0
        for n in h.name_list:
            h.hilarious_display_name = n
            out.paste(h.image_with_name(h.localized_name), (x * single_width, y * single_height))
            y += 1
            if y == rows:
                x += 1
                y = 0
        out.save("processed/Collage.jpg")
        await ctx.followup.send("```" +
            json.dumps({
                'name': hero_map[hero].name,
                'name_list': hero_map[hero].name_list,
                'image_path': hero_map[hero].image_path
            }) + "```",
                                file=discord.File("processed/Collage.jpg", filename="image.jpg"))
    else:
        await ctx.followup.send((hero if hero else "") + json.dumps(sorted(hero_map.keys())))

@bot.slash_command(name="bigcollage", description="All the pictures")
async def big_collage(ctx):
    await ctx.defer()
    hero_imgs = [Image.open(x.image_path) for x in hero_list.hero_list]
    cols = math.ceil(math.sqrt(len(hero_list.hero_list)*.7))
    rows = math.ceil(len(hero_list.hero_list) / cols)
    single_height = max(x.height for x in hero_imgs)
    single_width = max(x.width for x in hero_imgs)
    out = Image.new('RGB', (single_width * cols, single_height * rows), color=(47, 49, 54, 0))
    x = 0
    y = 0
    hero_list.hero_list.sort(key=lambda hs: hs.localized_name)
    for h in hero_list.hero_list:
        h.get_display_name()
        out.paste(h.image_with_name(h.localized_name), (x*single_width, y*single_height))
        y += 1
        if y == rows:
            x += 1
            y = 0
    out.save("processed/Collage.jpg")
    await ctx.followup.send(file=discord.File("processed/Collage.jpg", filename="image.jpg"))
    shutil.rmtree("processed/")


@bot.slash_command(name="random", description="I need a hero")
async def get_one(ctx):
    name = ctx.user.display_name
    random.choice(hero_list.hero_list).image_with_name(name)
    await ctx.response.send_message("",
                                    file=discord.File(f"processed/{name}.png"))


@bot.slash_command(name="refresh", description="Data gone stale?")
async def refresh(ctx):
    await ctx.defer()
    global wiggle_poll
    wiggle_poll = WigglePoll()
    dota_toekn = os.getenv("DOTA_TOKEN")
    if dota_toekn and dota_toekn != "":
        await ctx.followup.send("Doing a refresh")
        hero_list.refresh(dota_toekn)
        await ctx.followup.send("Refresh did")

    else:
        await ctx.followup.send("Can't refresh without a token")


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

@bot.slash_command(name="aitext", description="Write a story")
@option("prompt", description="Prompt?")
@option("randomness", description="0-10", required=False)
@option("max_length", description="how long?", required=False)
async def open_api_generate(ctx, prompt:str, randomness: int, max_length:int):
    await ctx.defer()
    try:
        prompt = prompt or "Story about a butterfly princess"
        randomness = sorted([1, randomness or 7, 10])[1]/10
        max_length = sorted([1, max_length or 250, 2000])[1]

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=randomness,
            max_tokens=max_length
        )
        await ctx.followup.send(">" + prompt + "\n" + response['choices'][0]['text'])
    except Exception as e:
        await ctx.followup.send(f"> {prompt}\nError: {e}")

def decode_img(msg):
    msg = base64.b64decode(msg)
    buf = io.BytesIO(msg)
    img = Image.open(buf)
    return img


@bot.slash_command(name="aiimage", description="Make image")
@option("prompt", description="What to make?")
@option("count", description="Generatead count, 1-10", required=False)
async def open_api_generate(ctx, prompt:str, count: int):
    await ctx.defer()
    prompt = prompt or "butterfly princess"
    try:
        count = sorted([1, count or 1, 10])[1]
        image_resp = openai.Image.create(prompt=prompt, n=count, response_format='b64_json')
        # https://beta.openai.com/docs/guides/images
        # print(image_resp['data'][0])
        images = []
        for i in image_resp['data']:
            images.append(decode_img(i['b64_json']))

        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count/cols)
        out = Image.new('RGB', (images[0].width * cols, images[0].height * rows), color=(47, 49, 54, 0))
        x = 0
        y = 0
        for i in images:
            out.paste(i, (x * i.width, y * i.height))
            x += 1
            if x == cols:
                y += 1
                x = 0
        if count > 4:
            out = out.resize((int(out.width*.5), int(out.height*.5)))
        out.save("images.png")
        await ctx.followup.send(f"> {prompt}", file=discord.File("images.png", filename="images.png"))
    except Exception as e:
        await ctx.followup.send(f"> {prompt}\nError: {e}")


def simple_format(field):
    if type(field) is list:
        if type(field[0]) is str:
            return ", ".join(field)
        return "\n".join(simple_format(x) for x in field)
    elif type(field) is map:
        if len(field.keys()) == 1:
            return simple_format(field[field.keys()[0]])
        return json.dumps(field).strip("\"")
    else:
        return json.dumps(field).strip("\"")


warhammer = bot.create_group("warhammer", "Command=War Hammer=Hammer")


@bot.slash_command(name="faction", description="Get faction info")
@option("faction", description="Faction Name", autocomplete=discord.utils.basic_autocomplete(wh_data.get_all_faction_names()))
async def find_faction(ctx, faction: str):
    err, names, faction = wh_data.get_faction(faction)

    if err and type(err) is str:
        color = Color.dark_blue()
        e = discord.Embed(title="Not Found", color=color, description=err)
        await ctx.respond(embed=e, ephemeral=True)
    elif names:
        color = Color.red()
        e = discord.Embed(title="Not Found", color=color, description=names)
        await ctx.respond(embed=e, ephemeral=True)
    elif faction and type(faction) is WHFaction:
        t = f"**{faction.name}**:" + ", ".join(sorted(faction.unit_names))
        await send_in_chunks(ctx, t, e=True)


@bot.slash_command(name="datacard", description="Find a datacard")
@option("unitname", description="Unit Name")
@option("faction", description="Faction Name", required=False)
async def datacard(ctx, unitname:str, faction:str):
    err, unit = wh_data.find(unitname, faction)

    if err and type(err) is str:
        color = Color.red()
        e = discord.Embed(title="Nope", color=color)
        e.add_field(name="Error",
                    value=err,
                    inline=True)
        await ctx.respond(embed=e)
    elif unit and type(unit) is WHUnit:
        e = discord.Embed(title=unit.get_display_name(), color=unit.get_color())
        unit.formatted_stats(e)
        await ctx.respond(embed=e, view=UnitView(unit), ephemeral=True)


@bot.slash_command(name="search", description="Search datacards for stats")
@option("f", description="Faction Name", required=False)
@option("t", description="Toughness", required=False)
@option("w", description="Wounds", required=False)
@option("sv", description="Save", required=False)
@option("m", description="Movement", required=False)
@option("inv", description="Invuln", required=False)
@option("fnp", description="Feel no pain", required=False)
@option("a", description="Attacks", required=False)
@option("ws", description="Weapon Skill (BS and melee)", required=False)
@option("s", description="Strength", required=False)
@option("d", description="Damage", required=False)
@option("ap", description="Armor Pierce", required=False)
@option("pts", description="Points", required=False)
async def search(ctx, f: str, t: str, w: str, sv: str, m: str, inv: str, fnp: str, a: str, ws: str, s: str, d: str, ap: str, pts: str):
    sp = SearchParams(
        {
            "faction": f,
            "toughness": t,
            "wounds": w,
            "save": sv,
            "movement": m,
            "invuln": inv,
            "feelnopain": fnp,
            "attacks": a,
            "weaponskill": ws,
            "strength": s,
            "damage": d,
            "ap": ap,
            "points": pts,
        }
    )
    if sp.empty():
        await ctx.respond("`t:>3,<8 w:=10 sv:<=3`\n`f:fish t:4`\n`f:csm t:>10 w:min`", ephemeral=True)
    else:
        # await ctx.defer()
        x = wh_data.search(sp)
        if len(x) != 0:
            print("\n".join([y.name + ": " + y.unformatted_stats() for y in x]))
        if len(x) == 0:
            await ctx.respond("No results", ephemeral=True)
        elif len(x) == 1:
            unit = x[0]
            e = discord.Embed(title=unit.get_display_name(), color=unit.get_color())
            unit.formatted_stats(e)
            await ctx.respond(embed=e, view=UnitView(unit))
        elif len(x) <= 20:
            await ctx.respond("Choose", view=TestView(x))
        else:
            out = [u.get_display_name() for u in x]
            await ctx.respond(", ".join(out)[:1999])

if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))
