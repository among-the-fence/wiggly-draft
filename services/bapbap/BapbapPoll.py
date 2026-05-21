import discord


class BapbapPoll:
    colors = [
        0x000000,
        0x1A0050,
        0x330090,
        0x5500C0,
        0x7700E0,
        0x9900FF,
        0xBB00FF,
        0xDD00FF,
        0xFF00FF,
    ]

    def __init__(self):
        self.users = []
        self.bans = {}
        self.owner = None
        self.active = False

    def start(self, init_user):
        self.owner = init_user
        self.active = True

    def end(self):
        self.users = []
        self.bans = {}
        self.owner = None
        self.active = False

    def user_reacted(self, user):
        if user in self.users:
            self.users.remove(user)
        else:
            self.users.append(user)

    def set_bans(self, user_id, heroes):
        self.bans[user_id] = heroes

    def get_bans(self, user_id):
        return self.bans.get(user_id, [])

    def ready(self):
        return len(self.users) >= 2

    def display_user_str(self):
        return "\n".join([x.mention for x in self.users]) if self.users else "_nobody yet_"

    def build_embed(self):
        embed = discord.Embed(
            title="BAPBAP — Who's playing?",
            description=f"Sign up below!\n\n{self.display_user_str()}",
            color=self.embed_color(),
        )
        embed.set_footer(text=f"{len(self.users)} player(s) signed up • Host can press Let's Go! when ready")
        return embed

    def embed_color(self):
        idx = min(len(self.users), len(BapbapPoll.colors) - 1)
        return BapbapPoll.colors[idx]
