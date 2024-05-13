import copy

import discord
from discord import Color

from services.warhammer import Warhammer
from util.utils import simple_format, send_in_chunks, extract_and_clear

wh_data = Warhammer.get_wh_data()


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
            e = discord.Embed(title=unit.name, color=color, description=t)
            unit.formatted_stats(e)
            e.add_field(name=display, value=t, inline=False)
            await interaction.edit(embed=e)

    async def handle_error(self, interaction, e):
        e2 = discord.Embed(title="Error", description=f"{type(e)}  {e}")
        await interaction.respond(embed=e2, ephemeral=True)

    async def send_weapon_profiles(self, interaction, name, display_name, prop_order):
        try:
            err, unit, color = self.get_unit()
            e = discord.Embed(title=unit.name, description=display_name, color=color)
            unit.formatted_stats(e)

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
            await interaction.edit(embed=e)
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
            err, unit, color = self.get_unit()
            e = discord.Embed(title=unit.name, color=color, description="Abilities")

            e.add_field(name="Core",
                        value=simple_format(unit.abilities['core']),
                        inline=True)
            e.add_field(name="Faction",
                        value=simple_format(unit.abilities['faction']),
                        inline=True)
            if 'invul' in unit.abilities and 'value' in unit.abilities['invul']:
                e.add_field(name="Invuln",
                            value=unit.abilities['invul']['value'],
                            inline=True)
            if 'wargear' in unit.abilities:
                out = []
                for x in unit.abilities['wargear']:
                    out.append(f"**{x['name']}**: {x['description']}")
                e.add_field(name="Wargear",
                        value="\n".join(out),
                        inline=True)
            e.add_field(name="Other",
                        value=simple_format(unit.abilities['other']),
                        inline=True)
            unit.formatted_stats(e)
            await interaction.edit(embed=e)
        except Exception as e:
            await self.handle_error(interaction, e)


    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="🧀")
    async def composition_button_callback(self, button, interaction):
        try:
            err, unit, color = self.get_unit()
            t = simple_format(unit.fluff)
            if len(t) > 2000:
                await send_in_chunks(interaction, t)
            else:
                e = discord.Embed(title=unit.name, color=color, description=t)
                unit.formatted_stats(e)
                e.add_field(name="Points",
                            value=unit.formatted_cost(),
                            inline=False)
                e.add_field(name="Keywords",
                            value=simple_format(unit.keywords),
                            inline=False)
                e.add_field(name="Factions",
                            value=simple_format(unit.factions),
                            inline=True)
                e.add_field(name=chr(173), value=chr(173), inline=True)  # Line break
                e.add_field(name="Composition",
                            value=simple_format(unit.composition),
                            inline=True)
                if unit.leader:
                    e.add_field(name="Leader",
                                value=simple_format(unit.leader),
                                inline=False)
                if unit.leads:
                    if "extra" in unit.leads and unit.leads["extra"]:
                        e.add_field(name="Leads",
                                    value=simple_format(unit.leads["extra"]),
                                    inline=False)

                    if "units" in unit.leads and unit.leads["units"]:
                        e.add_field(name="Leads",
                                value=simple_format(unit.leads["units"]),
                                inline=False)
                if unit.wargear:
                    warout = simple_format(unit.wargear)
                    if warout and warout != "None":
                        e.add_field(name="Wargear",
                                    value=warout,
                                    inline=False)
                if unit.transport:
                    e.add_field(name="Transport",
                                value=simple_format(unit.transport),
                                inline=False)

                await interaction.edit(embed=e)
        except Exception as e:
            await self.handle_error(interaction, e)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="☁️")
    async def fluff_button_callback(self, button, interaction):
        try:
            err, unit, color = self.get_unit()
            t = simple_format(unit.fluff)
            if len(t) > 2000:
                await send_in_chunks(interaction, t)
            else:
                e = discord.Embed(title=unit.name, color=color, description=t)
                unit.formatted_stats(e)
                e.add_field(name="Fluff", value=t, inline=False)
                if unit.the_rest:
                    e.add_field(name="The Rest", value=simple_format(unit.the_rest), inline=False)
                await interaction.edit(embed=e)
        except Exception as e:
            await self.handle_error(interaction, e)

