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
        self.users = set(())
        self.previous_success = set(())
        self.owner = None
        self.active = False

    def start(self, init_user):
        self.users.add(init_user.display_name)
        self.owner = init_user
        self.active = True

    def end(self):
        self.users = set(())
        self.owner = None
        self.active = False

    def user_reacted(self, user=None, user_name: str = None):
        if user:
            user_name = user.display_name
        if user_name in self.users:
            self.users.remove(user_name)
        else:
            self.users.add(user_name)

    def display_user_str(self):
        return ", ".join(self.users)

    def rerun(self):
        self.users = self.previous_success

    def build_embed(self):
        if self.ready():
            self.previous_success = self.users

        display_embed = discord.Embed(title="Commence the wigglin`",
                                      description=f"Who is in?\n{self.display_user_str()}",
                                      color=self.embed_color())
        return display_embed

    def invalid(self):
        return len(self.users) > 6

    def ready(self):
        return len(self.users) == 6

    def embed_color(self):
        return WigglePoll.colors[len(self.users)]
