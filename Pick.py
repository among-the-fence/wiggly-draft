from HeroList import Hero


class Pick:
    def __init__(self, hero: Hero, user):
        self.hero = hero
        self.user = user
        self.user_display_name = user.display_name