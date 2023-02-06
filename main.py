import base64
import io
import math
import os
import random
import shutil
from typing import List
import openai

import discord
from PIL import Image
from discord import option

from models.GameList import GameList
from models.HeroList import HeroList
from services.Configuration import Configuration
from views.TeamBuildView import TeamBuildView
from views import WiggleView
from services.WigglePoll import WigglePoll


bot = discord.Bot(debug_guilds=[Configuration.get_config('DEFAULT_GUILD')])
if Configuration.get_config("OPENAI_API_KEY"):
    openai.api_key = Configuration.get_config("OPENAI_API_KEY")

pudge = None
io_moji = None


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


@bot.slash_command(name="wiggle", description="Let's get ready to WIGGLE!")
async def wiggle(ctx):
    wiggle_poll = WiggleView.wiggle_poll
    if not wiggle_poll.active:
        wiggle_poll.start(ctx.user)
        view = WiggleView.WiggleView(timeout=Configuration.get_config('timeout'))
        view.children[0].emoji = io_moji
        view.children[1].emoji = pudge
        if not (os.getenv('ENV') == 'DEV' and Configuration.get_config('hacky_one_click')):
            view.children = [x for x in view.children if "TEST" not in x.label]

        await ctx.respond(embed=wiggle_poll.build_embed(), view=view)
        global activation_owner
        activation_owner = ctx.user
    else:
        await ctx.respond("Too slow", ephemeral=True)


@bot.slash_command(name="team", description="Team up!")
async def wiggle(ctx):
    wiggle_poll = WiggleView.wiggle_poll
    if not wiggle_poll.active:
        wiggle_poll.start(ctx.user)
        view = TeamBuildView(timeout=Configuration.get_config('timeout'))
        view.children[0].emoji = io_moji
        view.children[1].emoji = pudge
        if not (os.getenv('ENV') == 'DEV' and Configuration.get_config('hacky_one_click')):
            view.children = [x for x in view.children if "TEST" not in x.label]

        await ctx.respond(embed=WiggleView.wiggle_poll.build_embed(), view=view)
        global activation_owner
        activation_owner = ctx.user
    else:
        await ctx.respond("Too slow", ephemeral=True)


@bot.slash_command(name="again", description="Another round!")
async def again(ctx):
    wiggle_poll = WiggleView.wiggle_poll
    if not wiggle_poll.previous_success:
        await ctx.respond("Can't do a hit if there was no prior hit!")
    else:
        WiggleView.wiggle_poll.rerun()

        chosen = WiggleView.pick_heroes(list(wiggle_poll.previous_success))
        WiggleView.collage(chosen)
        display_embed = wiggle_poll.build_embed()
        display_embed.add_field(name="Radiant Players",
                                value=f"{chosen[0].user.mention} ({chosen[0].hero.localized_name})\n"
                                      f"{chosen[1].user.mention} ({chosen[1].hero.localized_name})\n"
                                      f"{chosen[2].user.mention} ({chosen[2].hero.localized_name})",
                                inline=True)
        display_embed.add_field(name="Dire Players",
                                value=f"{chosen[3].user.mention} ({chosen[3].hero.localized_name})\n"
                                      f"{chosen[4].user.mention} ({chosen[4].hero.localized_name})\n"
                                      f"{chosen[5].user.mention} ({chosen[5].hero.localized_name})",
                                inline=True)
        display_embed.set_image(url="attachment://image.jpg")
        await ctx.response.send_message(embed=display_embed, file=discord.File("processed/Collage.jpg", filename="image.jpg"))
        wiggle_poll.end()
        shutil.rmtree("processed/")


@bot.slash_command(name="bigcollage", description="All the pictures")
async def big_collage(ctx):
    hero_list = HeroList(Configuration.get_config('DOTA_TOKEN'))
    hero_imgs = [x.image for x in hero_list.hero_list]
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
    await ctx.response.send_message(file=discord.File("processed/Collage.jpg", filename="image.jpg"))
    shutil.rmtree("processed/")


@bot.slash_command(name="random", description="I need a hero")
async def get_one(ctx):
    hero_list = HeroList(Configuration.get_config('DOTA_TOKEN'))

    name = ctx.user.display_name
    random.choice(hero_list.hero_list).image_with_name(name)
    await ctx.response.send_message("",
                                    file=discord.File(f"processed/{name}.png"))


@bot.slash_command(name="refresh", description="Data gone stale?")
async def refresh(ctx):
    # this doesn't work anymore, it needs to be hooked into the service
    hero_list = HeroList(Configuration.get_config('DOTA_TOKEN'))

    wiggle_poll = WiggleView.wiggle_poll
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


if __name__ == "__main__":
    bot.run(Configuration.get_config('TOKEN'))
