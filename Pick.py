from HeroList import Hero


class Pick:
    def __init__(self, hero: Hero, user: str):
        self.hero = hero
        self.user = user