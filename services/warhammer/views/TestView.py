import discord

from services.warhammer import Warhammer
from services.warhammer.models.unit import WHUnit
from services.warhammer.views.UnitView import UnitView
from util.utils import simple_format, send_in_chunks

wh_data = Warhammer.get_wh_data()


class UnitSelect(discord.ui.Select):
    def __init__(self, units: list[WHUnit]):

        options = [
            discord.SelectOption(label=x.get_display_name(), description=x.unformatted_stats()) for x in units
        ]
        super().__init__(placeholder="Choose your destiny", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        err, unit = wh_data.find(self.values[0], None)

        if unit and type(unit) is WHUnit:
            e = discord.Embed(title=unit.get_display_name(), color=unit.get_color())
            unit.formatted_stats(e)
            await interaction.response.send_message(embed=e, view=UnitView(unit), ephemeral=True)
        else:
            await interaction.response.send_message("Error", ephemeral=True)


class TestView(discord.ui.View):

    def __init__(self, units: list[WHUnit], disable_forward_button=False):
        self.unit = units
        self.disable_forward_button = disable_forward_button
        super().__init__(timeout=None)
        self.add_item(UnitSelect(units))
