import discord
from Configuration import get_config
from models.PollResponse import PollResponse


class WigglePoll:
    colors = [
        0x000000,
        0x005000,
        0x009000,
        0x00A000,
        0x00B000,
        0x00D000,
        0x00F000]

    def __init__(self):
        self.users = []
        self.previous_success = []
        self.owner = None
        self.active = False

    def start(self, context):
        init_user = context.user
        self.users.append(init_user)
        self.owner = init_user

    def register_button(self, button_name, context):
        user = context.user
        if button_name == "register":
            if user in self.users:
                self.users.remove(user)
            else:
                self.users.append(user)
        elif button_name == "cancel":
            if user == self.owner:
                self.active = False
                self.users = []
                return PollResponse(color=0xAF0000, text=f"{user} put a stop to it")
            else:
                return PollResponse(ephemeral=True, text="Stop right there, criminal scum!")
        elif button_name == "hacky_one_click":
            while len(self.users) < 6:
                self.users.append(user)
        elif button_name == "hacky_trick_button":
            self.users.append(user)
        else:
            return PollResponse(color=0xAF0000, text="the hell was that")

        self.build_poll_response()

    def again(self):
        self.users = self.previous_success
        self.build_poll_response()

    def build_poll_response(self):
        return PollResponse(text=", ".join(self.users))

    def display_user_str(self):
        return ", ".join([x.mention for x in self.users])


    def build_embed(self):
        display_embed = discord.Embed(title="Commence the wigglin`",
                                      color=self.embed_color())
        if self.ready():
            self.previous_success = self.users
        else:
            display_embed.description = f"Who is in?\n{self.display_user_str()}"
        return display_embed


    def embed_color(self):
        return WigglePoll.colors[len(self.users)]
