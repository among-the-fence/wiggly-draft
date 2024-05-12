import copy

import discord
from discord import Color

from services.warhammer import Warhammer
from util.utils import simple_format, send_in_chunks, extract_and_clear

wh_data = Warhammer.Warhammer()

class UnitView(discord.ui.View):

    def get_unit(self):
        options = self.parent.data['options']
        unitname = next((x['value'] for x in options if x['name'] == 'unitname'), None)
        faction = next((x['value'] for x in options if x['name'] == 'faction'), None)
        x,y,z = wh_data.find(unitname, faction)
        return x, copy.deepcopy(y), z

    async def respond_with(self, interaction, display, propname):
        err, unit, color = self.get_unit()
        val = getattr(unit, propname)
        t = simple_format(val)
        if len(t) > 2000:
            await send_in_chunks(interaction, t)
        else:
            e2 = discord.Embed(title=display, color=color, description=t)
            await interaction.respond(embed=e2)

    async def handle_error(self, interaction, e):
        e2 = discord.Embed(title="Error", description=f"{type(e)}  {e}")
        await interaction.respond(embed=e2, ephemeral=True)

    async def send_weapon_profiles(self, interaction, name, display_name, prop_order):
        try:
            err, unit, color = self.get_unit()
            e = discord.Embed(title=display_name, color=color)

            val = getattr(unit, name)
            if val:
                for x in val:
                    for p in x["profiles"]:
                        pn = p["name"]
                        extract_and_clear(p, "name")
                        out = ""
                        for x in prop_order:
                            if x["key"] in p:
                                if x["key"] == "keywords":
                                    if len(p[x['key']]) > 0:
                                        out += f"{x['display']}:**{', '.join(p[x['key']])}** "
                                else:
                                    out += f"{x['display']}:**{p[x['key']]}** "

                        e.add_field(name=pn, value=out, inline=False)
            await interaction.respond(embed=e)
        except Exception as e:
            await self.handle_error(interaction, e)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="🔫")
    async def gun_button_callback(self, button, interaction):
        prop_order = [
            {"key": "range", "display": "Ra"},
            {"key": "attacks", "display": "At"},
            {"key": "skill", "display": "BS"},
            {"key": "strength", "display": "St"},
            {"key": "ap", "display": "AP"},
            {"key": "damage", "display": "D"},
            {"key": "keywords", "display": "K"}
        ]
        await self.send_weapon_profiles(interaction,"rangedWeapons", "Ranged", prop_order)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def melee_button_callback(self, button, interaction):
        prop_order = [
            {"key": "range", "display": "Ra"},
            {"key": "attacks", "display": "At"},
            {"key": "skill", "display": "WS"},
            {"key": "strength", "display": "St"},
            {"key": "ap", "display": "AP"},
            {"key": "damage", "display": "D"},
            {"key": "keywords", "display": "K"}
        ]
        await self.send_weapon_profiles(interaction,"meleeWeapons", "Melee", prop_order)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="🗿")
    async def ability_button_callback(self, button, interaction):
        try:
            await self.respond_with(interaction, "Abilities", "abilities")
        except Exception as e:
            await self.handle_error(interaction, e)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="☁️")
    async def fluff_button_callback(self, button, interaction):
        try:
            await self.respond_with(interaction, "Fluff", "fluff")
        except Exception as e:
            await self.handle_error(interaction, e)

