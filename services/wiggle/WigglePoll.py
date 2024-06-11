import discord


class WigglePoll:
    colors = [
        0x000000,
        0x005000,
        0x009000,
        0x00A000,
        0x00B000,
        0x00D000,
        0x00F000,
        0xD00000]

    def __init__(self):
        self.users = []
        self.previous_success = []
        self.owner = None
        self.active = False

    def start(self, init_user):
        self.users.append(init_user)
        self.owner = init_user
        self.active = True

    def end(self):
        self.users = []
        self.owner = None
        self.active = False

    def user_reacted(self, user, allow_weird_shit=False):
        if user in self.users and not allow_weird_shit:
            self.users.remove(user)
        else:
            self.users.append(user)

    def display_user_str(self):
        return ", ".join([x.mention for x in self.users])

    def rerun(self):
        self.users = self.previous_success

    def build_embed(self):
        display_embed = discord.Embed(title="Commence the wigglin`",
                                      color=self.embed_color())
        if self.ready():
            self.previous_success = self.users
        else:
            display_embed.description = f"Who is in?\n{self.display_user_str()}"
        return display_embed

    def invalid(self):
        return len(self.users) > 6

    def ready(self):
        return len(self.users) == 6

    def embed_color(self):
        return WigglePoll.colors[len(self.users)]
