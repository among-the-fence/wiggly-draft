import discord


class UnitView(discord.ui.View):

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="🔫")
    async def gun_button_callback(self, button, interaction):
        await interaction.response.send_message("You clicked the button!")
