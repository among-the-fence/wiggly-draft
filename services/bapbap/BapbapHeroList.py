import json
import random
from os.path import exists


class BapbapHeroList:
    HISTORY_PATH = "services/bapbap/bapbap_history.json"

    def __init__(self, data_path="bapbapHeroData.json", namemap_path="services/bapbap/bapbap-namemap.json"):
        with open(data_path, "r") as f:
            self.heroes = json.load(f)

        if exists(namemap_path):
            with open(namemap_path, "r") as f:
                self._namemap = json.load(f)
        else:
            self._namemap = {}

        self._history = self._load_history()

    def _load_history(self):
        if exists(self.HISTORY_PATH):
            with open(self.HISTORY_PATH, "r") as f:
                return json.load(f)
        return {}

    def _save_history(self, assignments):
        for user, (real_hero, _) in assignments.items():
            self._history[str(user.id)] = real_hero
        with open(self.HISTORY_PATH, "w") as f:
            json.dump(self._history, f)

    def _get_display_name(self, hero):
        if hero in self._namemap:
            names = self._namemap[hero]
            if isinstance(names, str):
                names = [names, hero]
            else:
                names = list(names) + [hero]
        else:
            names = [hero]
        return random.choice(names)

    def assign(self, users, bans):
        """Assign one unique hero to each user, respecting bans and recent history where possible.

        Most-constrained users (fewest fresh non-banned options) are assigned first
        so they get priority on their preferred heroes.
        """
        available = list(self.heroes)

        def fresh_non_banned_count(user):
            user_bans = set(bans.get(user.id, []))
            last_hero = self._history.get(str(user.id))
            return len([h for h in available if h not in user_bans and h != last_hero])

        sorted_users = sorted(users, key=fresh_non_banned_count)
        assignments = {}

        for user in sorted_users:
            user_bans = set(bans.get(user.id, []))
            last_hero = self._history.get(str(user.id))
            preferred_fresh = [h for h in available if h not in user_bans and h != last_hero]
            preferred = [h for h in available if h not in user_bans]
            if preferred_fresh:
                chosen = random.choice(preferred_fresh)
            elif preferred:
                chosen = random.choice(preferred)
            else:
                chosen = random.choice(available)
            assignments[user] = (chosen, self._get_display_name(chosen))
            available.remove(chosen)

        self._save_history(assignments)
        return assignments
