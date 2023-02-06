import json
import random

import discord

from services.Configuration import Configuration
from views import WiggleView


class TeamBuildView(discord.ui.View):
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        self.children = []
        wiggle_poll = WiggleView.wiggle_poll
        display_embed = discord.Embed(title=f"Don't do a hit!",
                                      color=0x900000)
        wiggle_poll.end()
        await self.message.edit(embed=display_embed, view=self)

    @discord.ui.button(label="", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        wiggle_poll = WiggleView.wiggle_poll
        wiggle_poll.user_reacted(interaction.user)
        await interaction.response.defer()

        display_embed = discord.Embed(title="Commence the teamin`",
                                      color=0x00F000)
        display_embed.description = f"Who is in?\n{wiggle_poll.display_user_str()}"

        await self.message.edit(embed=display_embed, view=self)

    @discord.ui.button(label="", row=0, style=discord.ButtonStyle.danger)
    async def second_button_callback(self, button, interaction):
        wiggle_poll = WiggleView.wiggle_poll
        await interaction.response.defer()
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

    @discord.ui.button(label="done", row=0, style=discord.ButtonStyle.green)
    async def done_button_callback(self, button, interaction):
        wiggle_poll = WiggleView.wiggle_poll
        user = interaction.user
        await interaction.response.defer()

        team_size = int(len(wiggle_poll.users) / 2)
        team_name_list = json.loads(open("data/teamnames.json", 'r').read())
        teams = []
        users = wiggle_poll.users
        random.shuffle(users)
        i = 0
        for c in range(0,2):
            teams.append({'name': "", 'team': []})
            for t in range(0, team_size):
                teams[c]['team'].append(users[i])
                i = i + 1
            team_size = len(teams[c]['team'])
            team_size_name = "solo" if team_size == 1 else "duo" if team_size == 2 else "teams"
            teams[c]['name'] = random.choice(team_name_list[team_size_name])

        display_embed = discord.Embed(title="Commence the teamin`",
                                      color=0x00F000)
        for x in teams:
            names = [y.name for y in x['team']]
            display_embed.add_field(name=x['name'], value=f"{', '.join(names)}")

        wiggle_poll.end()
        await self.message.edit(embed=display_embed, view=self)

    @discord.ui.button(label="TEST One user", row=0, style=discord.ButtonStyle.secondary)
    async def secret_last_button_callback(self, button, interaction):
        wiggle_poll = WiggleView.wiggle_poll

        await interaction.response.defer()
        user = interaction.user
        if Configuration.get_config('hacky_one_click'):
            wiggle_poll.user_reacted(user, True)
            display_embed = discord.Embed(title="Commence the teamin`",
                                          color=0x00F000)
            display_embed.description = f"Who is in?\n{wiggle_poll.display_user_str()}"
            await self.message.edit(embed=display_embed, view=self)
        else:
            await interaction.response.defer()
