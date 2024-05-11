import copy

import discord

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

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="🔫")
    async def gun_button_callback(self, button, interaction):
        err, unit, color = self.get_unit()
        e = discord.Embed(title="Ranged", color=color)
        prop_order = [
            {"key": "range", "display": "Ra"},
            {"key": "attacks", "display": "At"},
            {"key": "skill", "display": "Sk"},
            {"key": "strength", "display": "St"},
            {"key": "ap", "display": "AP"},
            {"key": "damage", "display": "D"},
            {"key": "keywords", "display": "K"}
        ]
        for x in unit.rangedWeapons:
            for p in x["profiles"]:
                pn = p["name"]
                extract_and_clear(p, "name")
                out = ""
                for x in prop_order:
                    if x["key"] in p:
                        out += f"{x['display']}:**{p[x['key']]}** "

                e.add_field(name=pn, value=out, inline=False)
        await interaction.respond(embed=e)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def melee_button_callback(self, button, interaction):

        err, unit, color = self.get_unit()
        e = discord.Embed(title="Melee", color=color)
        prop_order = [
            {"key": "range", "display": "Ra"},
            {"key": "attacks", "display": "At"},
            {"key": "skill", "display": "Sk"},
            {"key": "strength", "display": "St"},
            {"key": "ap", "display": "AP"},
            {"key": "damage", "display": "D"},
            {"key": "keywords", "display": "K"}
        ]
        for x in unit.meleeWeapons:
            for p in x["profiles"]:
                pn = p["name"]
                extract_and_clear(p, "name")
                out = ""
                for x in prop_order:
                    if x["key"] in p:
                        out += f"{x['display']}:**{p[x['key']]}** "

                e.add_field(name=pn, value=out, inline=False)
        await interaction.respond(embed=e)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="🗿")
    async def ability_button_callback(self, button, interaction):
        await self.respond_with(interaction, "Abilities", "abilities")



    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="☁️")
    async def fluff_button_callback(self, button, interaction):
        await self.respond_with(interaction, "Fluff", "fluff")

