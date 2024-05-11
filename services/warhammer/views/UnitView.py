import discord

from services.warhammer import Warhammer
from util.utils import simple_format, send_in_chunks

wh_data = Warhammer.Warhammer()

class UnitView(discord.ui.View):

    async def respond_with(self, interaction, display, propname):
        options = self.parent.data['options']
        unitname = next((x['value'] for x in options if x['name'] == 'unitname'), None)
        faction = next((x['value'] for x in options if x['name'] == 'faction'), None)
        err, unit, color = wh_data.find(unitname, faction)
        val = getattr(unit, propname)
        t = simple_format(val)
        if len(t) > 2000:
            await send_in_chunks(interaction, t)
        else:
            e2 = discord.Embed(title=display, color=color, description=t)
            await interaction.respond(embed=e2)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="🔫")
    async def gun_button_callback(self, button, interaction):
        await self.respond_with(interaction, "Ranged", "rangedWeapons")

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="🗿")
    async def ability_button_callback(self, button, interaction):
        await self.respond_with(interaction, "Abilities", "abilities")

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def melee_button_callback(self, button, interaction):
        await self.respond_with(interaction, "Melee", "meleeWeapons")

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="☁️")
    async def fluff_button_callback(self, button, interaction):
        await self.respond_with(interaction, "Fluff", "fluff")

