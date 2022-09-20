import json
import random
import discord
import os
from os.path import exists
import requests as requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()
bot = discord.Bot(debug_guilds=[os.getenv('DEFAULT_GUILD')])

bunches = {}

env = {
    "DEV": {
        "timeout": 10
    },
    "PROD": {
        "timeout": 300
    }
}


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

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
            pick['user'] = user_pick
            user_list.remove(user_pick)
        else:
            pick['user'] = "unassigned"
    return chosen


def get_hero_info():
    heroes = json.loads(requests.get(f"https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key={os.getenv('DOTA_TOKEN')}&language=en-US").content)
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
    myFont = ImageFont.truetype("fonts/Trajan Pro Bold.ttf", 15)
    for col in range(cols):
        for row in range(rows):
            print(i, x, y)
            out.paste(hero_imgs[i], (x, y))
            textual = ImageDraw.Draw(out)
            textual.text((x + 5, y + 5), hero_picks[col+row]['user'], fill=(255, 255, 255), font=myFont, stroke_width=2, stroke_fill=(0, 0, 0))
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

    @discord.ui.button(label="Do", row=0, style=discord.ButtonStyle.primary)
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


    @discord.ui.button(label="No", row=0, style=discord.ButtonStyle.danger)
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
async def hello(ctx):
    await ctx.respond("Who's in?", view=MyView(timeout=get_env_attribute('timeout')))


def get_env_attribute(attribute):
    return env.get(os.getenv('ENV'))[attribute]


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN')) # run the bot with the token