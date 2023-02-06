import shutil
import random
from typing import List

import discord
from PIL import Image

from models.HeroList import HeroList
from models.Pick import Pick
from services.Configuration import Configuration
from services.WigglePoll import WigglePoll

wiggle_poll = WigglePoll()
hero_list = HeroList(Configuration.get_config('DOTA_TOKEN'))



def bill_and_ben_are_on_the_same_team(matchup: List[Pick]):
    team1_names = set([x.user.display_name.lower() for x in matchup[:3]])
    team2_names = set([x.user.display_name.lower() for x in matchup[3:]])
    return {"chu", "mrc48b"}.issubset(team1_names) or {"chu", "mrc48b"}.issubset(team2_names)

def pick_heroes(user_list):
    matchup = build_picks(user_list)
    while bill_and_ben_are_on_the_same_team(matchup):
        matchup = build_picks(user_list)
    return matchup

def build_picks(user_list):
    chosen = hero_list.choose()
    matchup = []
    for pick in chosen:
        if user_list and len(user_list) > 0:
            user_pick = random.choice(user_list)
            user_list.remove(user_pick)
            matchup.append(Pick(pick, user_pick))
        else:
            matchup.append(Pick(pick, "Unassigned"))
    return matchup


def collage(hero_picks: List[Pick]):
    hero_imgs = [x.hero.image for x in hero_picks]
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

    for h in hero_picks:
        if h.hero.localized_name == 'Silencer':
            if random.randint(0, 9) < 5:
                for j in hero_picks:
                    j.user_display_name = 'Silencer'
                    j.hero.hilarious_display_name = 'Silencer'

    for col in range(cols):
        for row in range(rows):
            print(i, x, y)
            out.paste(hero_picks[i].hero.image_with_name(hero_picks[i].user_display_name), (x, y))
            i += 1
            y += single_height
        x += single_width + divider
        y = 0
    w, h = versus.size
    W, H = out.size
    out.paste(versus, (int((W - w) / 2), int((H - h) / 2)), versus)
    out.save("processed/Collage.jpg")


class WiggleView(discord.ui.View):
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
            chosen = pick_heroes(list(wiggle_poll.users))
            collage(chosen)
            display_embed = wiggle_poll.build_embed()
            display_embed.add_field(name="Radiant Team",
                                    value=f"{chosen[0].user.mention} ({chosen[0].hero.localized_name})\n"
                                          f"{chosen[1].user.mention} ({chosen[1].hero.localized_name})\n"
                                          f"{chosen[2].user.mention} ({chosen[2].hero.localized_name})",
                                    inline=True)
            display_embed.add_field(name="Dire Team",
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
        if not wiggle_poll.is_owner_user(interaction.user):
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

        if Configuration.get_config('hacky_one_click'):
            wiggle_poll.user_reacted(user, True)
            await self.update_embed()

        await interaction.response.defer()

    @discord.ui.button(label="TEST manyuser", row=0, style=discord.ButtonStyle.secondary)
    async def secret_more_button_callback(self, button, interaction):
        global wiggle_poll
        user = interaction.user

        if Configuration.get_config('hacky_one_click'):
            while not wiggle_poll.ready():
                wiggle_poll.user_reacted(user, True)
            await self.update_embed()

        await interaction.response.defer()
