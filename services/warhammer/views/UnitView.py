import time

import discord

from services.warhammer.models.unit import WHUnit
from services.warhammer.wh_data import get_wh_data
from util.utils import simple_format, send_in_chunks, chunkatize
import urllib.parse
wh_data = get_wh_data()


class UnitView(discord.ui.View):

    def __init__(self, unit: WHUnit, disable_forward_button=False):
        self.created = time.time()
        self.updated = time.time()
        self.unit = unit
        self.disable_forward_button = disable_forward_button
        super().__init__(timeout=3600)
        if disable_forward_button:
            self.children.remove(self.children[-1])

        safeFaction = urllib.parse.quote(unit.factions)
        safeName = unit.name.replace(" ","%20")
        url = f'http://localhost:5173/wahasearch/{safeFaction}/{safeName}'
        # print(url)
        button = discord.ui.Button(label='w', style=discord.ButtonStyle.url, url=url)
        self.add_item(button)

    async def on_timeout(self):
        self.disable_all_items()
        now = time.time()
        print(f"Button Timeout: {self.created} {self.updated} {now} {now-self.updated} {now-self.created}", )
        if self.message:
            await self.message.edit(view=self)
        else:
            await self.parent.edit(view=self)

    def get_unit(self):
        return None, self.unit

    async def respond_with(self, interaction, display, propname):
        err, unit = self.get_unit()
        val = getattr(unit, propname)
        t = simple_format(val)
        if len(t) > 2000:
            await send_in_chunks(interaction, t)
        else:
            e = discord.Embed(title=unit.get_display_name(), color=unit.get_color(), description=t)
            unit.formatted_stats(e)
            e.add_field(name=display, value=t, inline=False)
            await interaction.edit(embed=e)

    async def handle_error(self, interaction, e):
        print(f"{type(e)}  {e}")
        e2 = discord.Embed(title="Error", description=f"{type(e)}  {e}")
        await interaction.respond(embed=e2, ephemeral=True)

    async def send_weapon_profiles(self, interaction, name, display_name, prop_order):
        try:
            err, unit = self.get_unit()
            e = discord.Embed(title=unit.get_display_name(), description=display_name, color=unit.get_color())
            unit.formatted_stats(e)

            val = getattr(unit, name)
            if val:
                for x in val:
                    for p in x["profiles"]:
                        out = ""
                        for x in prop_order:
                            if x["key"] in p:
                                if x["key"] == "keywords":
                                    if len(p[x['key']]) > 0:
                                        out += f"{x['display']}:**{', '.join(p[x['key']])}** "
                                else:
                                    out += f"{x['display']}:**{p[x['key']]}** "

                        e.add_field(name=p["name"], value=out, inline=False)
            await interaction.edit(embed=e, view=self)
        except Exception as e:
            await self.handle_error(interaction, e)

    @discord.ui.button(label="", custom_id="rangedbuttonid",style=discord.ButtonStyle.primary, emoji="🔫")
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
        self.updated = time.time()
        await self.send_weapon_profiles(interaction,"rangedWeapons", "Ranged", prop_order)

    @discord.ui.button(label="", custom_id="meleebuttonid", style=discord.ButtonStyle.primary, emoji="⚔️")
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
        self.updated = time.time()
        await self.send_weapon_profiles(interaction,"meleeWeapons", "Melee", prop_order)

    def add_field(self, e, title, text, inline):
        if len(text) < 1023:
            e.add_field(name=title, value=text, inline=inline)
        else:
            chunk_count = (len(text) // 1023) + 1
            chunk_size = len(text) // chunk_count
            print(f"chunking message {chunk_size} {chunk_count}")
            for i in range(0, len(text), chunk_size):
                e.add_field(name=title, value=text[i: i + chunk_size], inline=inline)

    @discord.ui.button(label="", custom_id="abilittybutton", style=discord.ButtonStyle.primary, emoji="🗿")
    async def ability_button_callback(self, button, interaction):
        try:
            err, unit = self.get_unit()
            e = discord.Embed(title=unit.get_display_name(), color=unit.get_color(), description="Abilities")
            unit.formatted_stats(e)

            if "core" in unit.abilities:
                self.add_field(e, "Core", simple_format(unit.abilities['core']), True)
            if "faction" in unit.abilities:
                self.add_field(e, "Faction", simple_format(unit.abilities['faction']), True)
            if 'invul' in unit.abilities and 'value' in unit.abilities['invul']:
                self.add_field(e, "Invuln", unit.abilities['invul']['value'], True)
            if 'wargear' in unit.abilities:
                out = []
                for x in unit.abilities['wargear']:
                    out.append(f"**{x['name']}**: {x['description']}")
                self.add_field(e, "Wargear", "\n".join(out), False)
            if 'other' in unit.abilities:
                for x in unit.abilities['other']:
                    if "name" in x and "description" in x:
                        self.add_field(e, f"{x['name']}", f"{x['description']}", True)
                    else:
                        self.add_field(e, "",f"{x['description']}", True)

            if "primarch" in unit.abilities:
                out = []
                for y in unit.abilities['primarch']:
                    current = []
                    for x in y['abilities']:
                        if "name" in x and "description" in x:
                            current.append(f"__{x['name']}__: {x['description']}")
                        else:
                            current.append(x)
                    out.append(f"**{y['name']}**: {' '.join(current)}")
                self.add_field(e, "Primarch", simple_format(out), False)
            self.updated = time.time()
            await interaction.edit(embed=e, view=self)
        except Exception as e:
            await self.handle_error(interaction, e)

    @discord.ui.button(label="", custom_id="buttoncomptbutton", style=discord.ButtonStyle.primary, emoji="🧀")
    async def composition_button_callback(self, button, interaction):
        try:
            err, unit = self.get_unit()
            t = simple_format(unit.fluff)
            if len(t) > 2000:
                await send_in_chunks(interaction, t)
            else:
                e = discord.Embed(title=unit.get_display_name(), color=unit.get_color(), description=t)
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
                if unit.leadBy:
                    e.add_field(name="Lead By",
                                value=simple_format(unit.leadBy),
                                inline=False)
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
                    if len(unit.wargear) > 0 and unit.wargear[0] != "None":
                        e.add_field(name="Wargear",
                                    value="\n".join(unit.wargear),
                                    inline=False)
                if unit.transport:
                    e.add_field(name="Transport",
                                value=simple_format(unit.transport),
                                inline=False)

                self.updated = time.time()
                await interaction.edit(embed=e, view=self)
        except Exception as e:
            await self.handle_error(interaction, e)

    @discord.ui.button(label="", custom_id="fluffbutton", style=discord.ButtonStyle.primary, emoji="☁️")
    async def fluff_button_callback(self, button, interaction):
        try:
            err, unit = self.get_unit()
            t = simple_format(unit.fluff)
            if len(t) > 2000:
                await send_in_chunks(interaction, t)
            else:
                e = discord.Embed(title=unit.get_display_name(), color=unit.get_color(), description=t)
                unit.formatted_stats(e)
                e.add_field(name="Fluff", value=t, inline=False)
                if unit.the_rest:
                    e.add_field(name="The Rest", value=simple_format(unit.the_rest), inline=False)

                self.updated = time.time()
                await interaction.edit(embed=e, view=self)
        except Exception as e:
            await self.handle_error(interaction, e)

    @discord.ui.button(label="", custom_id="debugbutton", style=discord.ButtonStyle.primary, emoji="🦠")
    async def debug_button_callback(self, button, interaction):
        try:
            err, unit = self.get_unit()
            e = discord.Embed(title=unit.get_display_name(), color=unit.get_color(), description="Abilities")
            unit.formatted_stats(e)
            k_c = chunkatize(simple_format(unit.compiled_keywords), 1023)
            for w in k_c:
                self.add_field(e, "Kwywords", w, False)
            k_c = chunkatize(simple_format(unit.super_keywords), 1023)
            for w in k_c:
                self.add_field(e, "Extended Keywords", w, False)
            self.updated = time.time()
            await interaction.edit(embed=e, view=self)
        except Exception as e:
            await self.handle_error(interaction, e)

    @discord.ui.button(label="", custom_id="forwardbutton", style=discord.ButtonStyle.primary, emoji="➡️")
    async def send_button_callback(self, button, interaction):
        try:
            button.disabled = True
            self.children.remove(button)
            await interaction.channel.send(view=self, embed=self.message.embeds[0])
            self.updated = time.time()
            await interaction.response.edit_message(view=self, embed=None)  # edit the message's view
        except Exception as e:
            await self.handle_error(interaction, e)

