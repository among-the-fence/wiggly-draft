import json
import random
import discord
import os
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
            await interaction.response.send_message(f"{','.join(bunches[messageid])} pressed me!")
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