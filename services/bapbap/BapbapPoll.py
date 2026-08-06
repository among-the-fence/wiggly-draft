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
        self.bans_enabled = True
        self.player_count = None
        self.team_size = None
        self.previous_users = []
        self.previous_bans = {}
        self.previous_team_size = None

    def start(self, init_user, player_count=None, bans_enabled=True, team_size=None):
        self.owner = init_user
        self.active = True
        self.player_count = player_count
        self.bans_enabled = bans_enabled
        self.team_size = team_size

    def end(self):
        self.users = []
        self.bans = {}
        self.owner = None
        self.active = False
        self.bans_enabled = True
        self.player_count = None
        self.team_size = None

    def snapshot_success(self):
        self.previous_users = list(self.users)
        self.previous_bans = dict(self.bans)
        self.previous_team_size = self.team_size

    def user_reacted(self, user):
        if user in self.users:
            self.users.remove(user)
            self.bans.pop(user.id, None)
        else:
            self.users.append(user)

    def set_bans(self, user_id, heroes):
        self.bans[user_id] = heroes

    def get_bans(self, user_id):
        return self.bans.get(user_id, [])

    def ready(self):
        return len(self.users) >= 2

    def autostart_ready(self):
        return self.player_count is not None and len(self.users) >= self.player_count

    def display_user_str(self):
        if not self.users:
            return "_nobody yet_"
        lines = []
        for user in self.users:
            if self.bans_enabled:
                icon = "✅" if user.id in self.bans else "⚠️"
                lines.append(f"{icon} {user.mention}")
            else:
                lines.append(user.mention)
        return "\n".join(lines)

    def build_embed(self):
        embed = discord.Embed(
            title="BAPBAP — Who's playing?",
            description=f"Sign up below!\n\n{self.display_user_str()}",
            color=self.embed_color(),
        )
        embed.set_thumbnail(url="attachment://logo.webp")
        footer_parts = [f"{len(self.users)} player(s) signed up"]
        if self.player_count:
            footer_parts.append(f"auto-starts at {self.player_count}")
        if self.team_size:
            footer_parts.append(f"teams of {self.team_size}")
        if not self.bans_enabled:
            footer_parts.append("bans off")
        footer_parts.append("Host can press Let's Go! when ready")
        embed.set_footer(text=" • ".join(footer_parts))
        return embed

    def embed_color(self):
        idx = min(len(self.users), len(BapbapPoll.colors) - 1)
        return BapbapPoll.colors[idx]
