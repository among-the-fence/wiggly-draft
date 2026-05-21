import json
import random


class BapbapHeroList:
    def __init__(self, data_path="bapbapHeroData.json"):
        with open(data_path, "r") as f:
            self.heroes = json.load(f)

    def assign(self, users, bans):
        """Assign one unique hero to each user, respecting bans where possible.

        Most-constrained users (fewest non-banned options) are assigned first
        so they get priority on their preferred heroes.
        """
        available = list(self.heroes)

        def non_banned_count(user):
            user_bans = set(bans.get(user.id, []))
            return len([h for h in available if h not in user_bans])

        sorted_users = sorted(users, key=non_banned_count)
        assignments = {}

        for user in sorted_users:
            user_bans = set(bans.get(user.id, []))
            preferred = [h for h in available if h not in user_bans]
            chosen = random.choice(preferred) if preferred else random.choice(available)
            assignments[user] = chosen
            available.remove(chosen)

        return assignments
