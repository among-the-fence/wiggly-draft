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
        await interaction.response.send_message("You pressed me!")

    @discord.ui.button(label="NO", row=0, style=discord.ButtonStyle.danger)
    async def second_button_callback(self, button, interaction):
        for child in self.children:
            child.disabled = True
        self.children = []
        await self.message.edit(content="Don't do a hit!", view=self)

@bot.slash_command(name="wiggle", description="Make it")
async def hello(ctx):
    await ctx.respond("Hey!", view=MyView(timeout=get_env_attribute('timeout')))


def get_env_attribute(attribute):
    return env.get(os.getenv('ENV'))[attribute]


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN')) # run the bot with the token