import configparser
import json
from os.path import exists
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import requests
import random
from PIL import Image, ImageDraw, ImageFont
import asyncio


def get_env_or_default(cfg, name, env_name):
    return cfg[name] if name in cfg and cfg[name] else os.environ.get(env_name)


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()

config = configparser.ConfigParser()
config.read("config")
env_config = config['DEFAULT']
bot_token = get_env_or_default(env_config, 'discord', "BOT_TOKEN")
dota_token = get_env_or_default(env_config, 'dota', "DOTA_TOKEN")
max_players = int(env_config['player_count'])
listen_timeout = int(env_config['timeout'])
command_prefix = str(get_env_or_default(env_config, 'prefix', "BOT_PREFIX"))


bot = commands.Bot(command_prefix=command_prefix)


def pick_heroes(user_list):
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
    chosen = random.sample(heroes, 6)
    for pick in chosen:
        if pick['localized_name'] == "Lifestealer":
            pick['localized_name'] = "Weird Dog"
        pick['image'] = get_hero_img(pick)
        if user_list and len(user_list) > 0:
            user_pick = random.choice(user_list)
            pick['user'] = user_pick.mention
            user_list.remove(user_pick)
        else:
            pick['user'] = "unassigned"
    return chosen


def get_hero_info():
    heroes = json.loads(requests.get(f"https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key={dota_token}&language=en-US").content)
    open("heroData.json", 'w').write(json.dumps(heroes['result']))
    for h in heroes['result']['heroes']:
        print(h)
        get_hero_img(h)


def get_hero_img(hero_data):
    img_name = hero_data['name'].replace('npc_dota_hero_', '') + "_lg.png"
    save_location = f"imagecache/heroes/{img_name}"
    hero_name = hero_data['localized_name']
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
    draw.text((padding,H-20), hero_name, fill=(255,255,255), font = myFont, stroke_width=2, stroke_fill=(0,0,0))
    portrait.save(save_location)
    return save_location


def collage(hero_picks):
    hero_imgs = [Image.open(x['image']) for x in hero_picks]
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
            out.paste(hero_imgs[i], (x, y))
            i += 1
            y += single_height
        x += single_width+divider
        y = 0
    w, h = versus.size
    W, H = out.size
    out.paste(versus,(int((W-w)/2),int((H-h)/2)), versus)
    out.save("Collage.jpg")


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Wiggly Woods 3v3"))


@bot.command()
async def wiggle(ctx):
    currentPlayers = 0
    slotString = f"Current Signups: {currentPlayers}/{max_players}\n"
    embedVar=discord.Embed(
        title="Let's Get Ready to Street Dota!", description="Click the <:io:908114245806329886> to signup!",
        color=0xaf0101)
    embedVar.set_footer(text="Game started by: {}".format(ctx.author))
    embedVar.add_field(name='Signed up: ', value=slotString, inline=False)
    msg = await ctx.channel.send(embed=embedVar)
    user_list = []
    await msg.add_reaction("<:io:908114245806329886>")
    await msg.add_reaction("<:pudge:908107144254087169>")
    while True:
        users = ""
        try:
            reaction, user= await bot.wait_for("reaction_add", timeout=listen_timeout)
            if str(reaction) == "<:io:908114245806329886>":
                msg = await ctx.channel.fetch_message(msg.id)
                for reactions in msg.reactions:
                    if str(reactions) == "<:io:908114245806329886>":
                        user_list = [user async for user in reactions.users() if user != bot.user]
                        for user in user_list:
                            users = users + user.mention + "\n"
                            currentPlayers = len(user_list)
            slotString = f"Current Signups: {currentPlayers}/{max_players}\n"
            new_embed = discord.Embed(
                title="Let's Get Ready to Street Dota!", description="Click the <:io:908114245806329886> to signup!",
                color=0xaf0101)
            new_embed.set_footer(text="Game started by: {}".format(ctx.author))
            new_embed.add_field(name='Signed up:', value= slotString + users, inline=False)

            await msg.edit(embed=new_embed)

            if len(user_list) == max_players:
                chosen = pick_heroes(user_list)
                collage(chosen)
                embedVar=discord.Embed(
                    title="FIGHT!",
                    color=0x0faff4)
                file = discord.File("Collage.jpg", filename="image.jpg")
                embedVar.set_image(url="attachment://image.jpg")
                embedVar.add_field(name="Radiant Players", value=f"{chosen[0]['user']}\n{chosen[1]['user']}\n{chosen[2]['user']}", inline=True)
                embedVar.add_field(name="Dire Players", value=f"{chosen[3]['user']}\n{chosen[4]['user']} \n{chosen[5]['user']}", inline=True)
                embedVar.set_footer(text="Game started by: {}".format(ctx.author))
                await ctx.channel.send(file=file, embed=embedVar)
                break

        except asyncio.TimeoutError:
            break_embed = discord.Embed(
                title="Don't do a hit!", description="The draft was aborted due to timeout.",
                color=0x000000)
            await msg.edit(embed = break_embed)
            break


# @bot.command()
# async def random(ctx,arg=6):
#     chosen = pick_heroes(arg)
#     collage(chosen)
#     embedVar=discord.Embed(
#         title="FIGHT!",
#         color=0x0faff4)
#     file = discord.File("Collage.jpg", filename="image.jpg")
#     embedVar.set_image(url="attachment://image.jpg")
#     embedVar.set_footer(text="Generated started by: {}".format(ctx.author))
#     await ctx.channel.send(file=file, embed=embedVar)


if __name__ == "__main__":

    if not exists("heroData.json") or not bot_token:
        get_hero_info()
    if not bot_token:
        print("No discord token provided")
    else:
        bot.run(bot_token)
